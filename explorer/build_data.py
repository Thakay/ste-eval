"""Bundle every reply, judge verdict, reader quiz and metric into one JSON for the recap page.

Experiment 1 (Kay's setup vs Lite, Scoped, Full) sits at the top level; experiment 2
(bare vs the one-liner) sits under "exp2".
"""
import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENS = ["claude-opus", "codex-sol"]
JUDGES = ["opus", "sol"]
sys.path.insert(0, str(ROOT / "harness"))
import metrics as M  # noqa: E402


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


def boot(diffs, n=4000):
    rng = random.Random(7)
    ms = sorted(sum(rng.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(n))
    return [round(sum(diffs) / len(diffs), 3), round(ms[int(0.025 * n)], 3), round(ms[int(0.975 * n)], 3)]


def bundle(base: Path, arms: list[str], control: str) -> dict:
    metrics = {(r["model"], r["arm"], r["task"], int(r["rep"])): r for r in csv.DictReader(open(base / "scores" / "metrics.csv"))}
    cells = {}
    for meta_path in (base / "runs").rglob("meta.json"):
        m = json.loads(meta_path.read_text())
        u = m["usage"]
        think = (u.get("output_tokens_details", {}).get("thinking_tokens", 0) if m["model"].startswith("claude")
                 else u.get("reasoning_output_tokens", 0))
        k = (m["model"], m["arm"], m["task"], m["rep"])
        mt = metrics[k]
        cells[k] = {
            "text": (meta_path.parent / "output.md").read_text(),
            "seconds": m["seconds"], "thinking": think, "out_tokens": u.get("output_tokens", 0),
            "words": int(mt["words_prose"]), "wps": float(mt["wps_mean"]), "over25": float(mt["pct_over_25"]),
            "over20": float(mt["pct_over_20"]), "passive": float(mt["pct_passive"]), "fk": float(mt["fk_grade"]),
            "judges": {}, "reader": None,
        }
    for p in (base / "scores" / "judge").rglob("*.json"):
        d = json.loads(p.read_text())
        ranking = d["verdict"].get("ranking", [])
        for lab, arm in d["label_to_arm"].items():
            a = d["verdict"]["answers"][lab]
            cells[(d["gen"], arm, d["task"], d["rep"])]["judges"][d["judge"]] = {
                "label": lab, "rank": ranking.index(lab) + 1, "overall": a["overall"],
                "checklist": a["checklist"], "clarity": a["clarity"], "actionability": a["actionability"],
                "nuance": a["nuance"], "naturalness": a["naturalness"], "esl": a["esl_ease"],
                "note": a.get("note", ""), "invented": a.get("invented", []), "errors": a.get("errors", []),
            }
    for p in (base / "scores" / "reader").glob("*.json"):
        d = json.loads(p.read_text())
        cells[(d["gen"], d["arm"], d["task"], d["rep"])]["reader"] = {"score": sum(d["scores"]), "of": len(d["scores"]),
                                                                        "answers": d["answers"], "marks": d["scores"]}

    def judge_vals(gen, arm, field, judge=None):
        return [v[field] for (g, a, t, r), c in cells.items() if g == gen and a == arm
                for j, v in c["judges"].items() if judge in (None, j)]

    def paired(field, arm, gen=None):
        diffs = []
        for (g, a, t, r), c in cells.items():
            if a != control or (gen and g != gen):
                continue
            other = cells[(g, arm, t, r)]
            for j in JUDGES:
                vb, vo = c["judges"][j], other["judges"][j]
                if field == "checklist":
                    diffs.append(sum(vo["checklist"]) / len(vo["checklist"]) - sum(vb["checklist"]) / len(vb["checklist"]))
                else:
                    diffs.append(vo[field] - vb[field])
        return boot(diffs)

    agg = {"overall": {}, "overall_by_judge": {}, "thinking": {}, "seconds": {}, "ste": {}, "ste_by_gen": {}, "deltas": {},
           "per_model_deltas": {}, "per_model_dims": {}, "win_rate": {}}
    for gen in GENS:
        agg["overall"][gen] = {a: mean(judge_vals(gen, a, "overall")) for a in arms}
        agg["thinking"][gen] = {a: mean([c["thinking"] for k, c in cells.items() if k[0] == gen and k[1] == a]) for a in arms}
        agg["seconds"][gen] = {a: mean([c["seconds"] for k, c in cells.items() if k[0] == gen and k[1] == a]) for a in arms}
        agg["ste_by_gen"][gen] = {a: {f: mean([c[f] for k, c in cells.items() if k[0] == gen and k[1] == a])
                               for f in ["words", "wps", "over20", "over25", "passive", "fk", "thinking", "seconds"]} for a in arms}
        for j in JUDGES:
            agg["overall_by_judge"][f"{j}|{gen}"] = {a: mean(judge_vals(gen, a, "overall", j)) for a in arms}
    for a in arms:
        sel = [c for k, c in cells.items() if k[1] == a]
        agg["ste"][a] = {f: mean([c[f] for c in sel]) for f in ["words", "wps", "over20", "over25", "passive", "fk", "thinking", "seconds"]}
    fields = ["overall", "checklist", "nuance", "naturalness", "esl", "clarity"]
    for arm in arms:
        if arm == control:
            continue
        agg["deltas"][arm] = {f: paired(f, arm) for f in fields}
        for gen in GENS:
            agg["per_model_deltas"][f"{gen}|{arm}"] = paired("overall", arm, gen)
            agg["per_model_dims"][f"{gen}|{arm}"] = {f: paired(f, arm, gen) for f in fields}
        w = n = 0
        for (g, a, t, r), c in cells.items():
            if a == control:
                for j in JUDGES:
                    n += 1
                    w += cells[(g, arm, t, r)]["judges"][j]["rank"] < c["judges"][j]["rank"]
        agg["win_rate"][arm] = round(w / n, 3)

    hist = {a: [0] * 41 for a in arms}
    for (g, a, t, r), c in cells.items():
        for block in M.to_prose(c["text"]):
            for s in M.NLP(block).sents:
                n = len(M.words(s))
                if n:
                    hist[a][min(n, 40)] += 1
    return {"arms": arms, "reps": sorted({k[3] for k in cells}),
            "cells": {f"{g}|{a}|{t}|{r}": c for (g, a, t, r), c in cells.items()}, "agg": agg, "hist": hist}


out = {"tasks": json.loads((ROOT / "dataset" / "tasks.json").read_text()), "gens": GENS,
       "arm_words": {a: len((ROOT / "arms" / f"ste-{a}.md").read_text().split()) for a in ["lite", "scoped", "full"]}}
out.update(bundle(ROOT, ["base", "lite", "scoped", "full"], "base"))
if (ROOT / "exp2" / "scores" / "metrics.csv").exists():
    out["exp2"] = bundle(ROOT / "exp2", ["bare", "oneliner"], "bare")
    out["exp2"]["oneliner_text"] = (ROOT / "exp2" / "oneliner.md").read_text().strip()
dest = ROOT / "explorer" / "data.json"
dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print(f"{len(out['cells'])} exp1 cells, {len(out.get('exp2', {}).get('cells', {}))} exp2 cells, {dest.stat().st_size // 1024} KB")
if "exp2" in out:
    print(json.dumps(out["exp2"]["agg"]["per_model_deltas"]), json.dumps(out["exp2"]["agg"]["win_rate"]))

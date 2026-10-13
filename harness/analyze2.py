"""Experiment 2 analysis: bare vs bare + "Speak only in ASD-STE100", pairwise.

Inputs: exp2/runs, exp2/scores/{metrics.csv,judge,reader}; for the cross-experiment ladder also
runs/ and scores/metrics.csv from experiment 1 (metrics only: judge scores are not comparable
across experiments because each judge call only saw its own group).
Output: exp2/scores/summary.md
"""
import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
E2 = ROOT / "exp2"
DIMS = ["overall", "checklist", "clarity", "actionability", "nuance", "naturalness", "esl_ease"]


def runs(base: Path, exp: str) -> pd.DataFrame:
    rows = []
    for mp in (base / "runs").rglob("meta.json"):
        m = json.loads(mp.read_text())
        u = m["usage"]
        think = (u.get("output_tokens_details", {}).get("thinking_tokens", 0) if m["model"].startswith("claude")
                 else u.get("reasoning_output_tokens", 0))
        rows.append({"exp": exp, "gen": m["model"], "arm": m["arm"], "task": m["task"], "type": m["type"],
                     "rep": m["rep"], "seconds": m["seconds"], "thinking": think,
                     "output_tokens": u.get("output_tokens", 0), "tool_calls": u.get("tool_calls", 0),
                     "cost_usd": u.get("cost_usd")})
    df = pd.DataFrame(rows)
    met = pd.read_csv(base / "scores" / "metrics.csv").rename(columns={"model": "gen"}).drop(columns=["type", "path"])
    return df.merge(met, on=["gen", "arm", "task", "rep"], how="left")


def judges() -> pd.DataFrame:
    rows = []
    for p in (E2 / "scores" / "judge").rglob("*.json"):
        d = json.loads(p.read_text())
        v = d["verdict"]
        for lab, arm in d["label_to_arm"].items():
            a = v["answers"][lab]
            cl = a.get("checklist", [])
            rows.append({"judge": d["judge"], "gen": d["gen"], "task": d["task"], "rep": d["rep"], "arm": arm,
                         "checklist": sum(cl) / len(cl), "invented": len(a.get("invented", [])),
                         "errors": len(a.get("errors", [])), "won": int(v["ranking"][0] == lab),
                         **{k: a.get(k) for k in DIMS if k != "checklist"}})
    return pd.DataFrame(rows)


def boot(diffs, n=4000):
    rng = random.Random(7)
    ms = sorted(sum(rng.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(n))
    m, lo, hi = sum(diffs) / len(diffs), ms[int(0.025 * n)], ms[int(0.975 * n)]
    return f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]" + ("*" if lo > 0 or hi < 0 else "")


def paired(df, col, key):
    piv = df.pivot_table(index=key, columns="arm", values=col)
    return boot((piv["oneliner"] - piv["bare"]).dropna().tolist())


def main() -> None:
    r2 = runs(E2, "exp2")
    j = judges()
    rd = []
    for p in (E2 / "scores" / "reader").glob("*.json"):
        d = json.loads(p.read_text())
        rd.append({"gen": d["gen"], "arm": d["arm"], "task": d["task"], "rep": d["rep"], "reader": sum(d["scores"]) / len(d["scores"])})
    r2 = r2.merge(pd.DataFrame(rd), on=["gen", "arm", "task", "rep"], how="left") if rd else r2
    out = ["# Experiment 2: bare vs \"Speak only in ASD-STE100\"\n",
           f"Runs: {len(r2)} | judge rows: {len(j)} | tool calls: {int(r2.tool_calls.fillna(0).sum())}\n"]

    out.append("## 1. Paired delta, one-liner minus bare (mean [95% CI], * = excludes 0)\n")
    jk = ["judge", "gen", "task", "rep"]
    rows = []
    for scope, d in [("both models", j)] + [(g, j[j.gen == g]) for g in sorted(j.gen.unique())]:
        rows.append({"scope": scope, **{c: paired(d, c, jk) for c in DIMS}})
    out.append(pd.DataFrame(rows).set_index("scope").to_markdown())
    out.append("\n### By judge (overall)\n")
    rows = [{"judge": jj, "gen": g, "overall": paired(j[(j.judge == jj) & (j.gen == g)], "overall", jk)}
            for jj in ["opus", "sol"] for g in sorted(j.gen.unique())]
    out.append(pd.DataFrame(rows).to_markdown(index=False))
    win = j[j.arm == "oneliner"].groupby(["gen"])["won"].mean()
    out.append(f"\nOne-liner win rate (judge picked it over bare): overall {j[j.arm == 'oneliner'].won.mean():.2f}; "
               + ", ".join(f"{g} {w:.2f}" for g, w in win.items()) + "\n")

    out.append("\n## 2. Means by model and arm\n")
    out.append(j.groupby(["gen", "arm"])[DIMS + ["invented", "errors"]].mean().round(2).to_markdown())
    mcols = ["words_prose", "wps_mean", "pct_over_20", "pct_over_25", "pct_passive", "ing_per_100w",
             "perfect_tense", "semicolons", "fk_grade", "thinking", "output_tokens", "seconds"]
    if "reader" in r2:
        mcols.append("reader")
    out.append("\n")
    out.append(r2.groupby(["gen", "arm"])[mcols].mean().round(2).to_markdown())
    rk = ["gen", "task", "rep"]
    out.append("\n### Paired metric deltas, one-liner minus bare\n")
    out.append(pd.DataFrame([{"gen": g, **{c: paired(r2[r2.gen == g], c, rk) for c in ["words_prose", "wps_mean", "pct_passive", "thinking", "seconds"]}}
                             for g in sorted(r2.gen.unique())]).set_index("gen").to_markdown())

    out.append("\n## 3. Overall by task (judge mean)\n")
    out.append(j.pivot_table(index=["gen", "task"], columns="arm", values="overall").round(2).to_markdown())

    out.append("\n## 4. Ladder across both experiments (metrics only)\n")
    r1 = runs(ROOT, "exp1")
    both = pd.concat([r1, r2.drop(columns=["reader"], errors="ignore")])
    both["cond"] = both.exp + ":" + both.arm
    order = ["exp2:bare", "exp2:oneliner", "exp1:base", "exp1:lite", "exp1:scoped", "exp1:full"]
    lad = both.groupby(["gen", "cond"])[["words_prose", "wps_mean", "pct_over_20", "pct_passive", "fk_grade", "thinking", "seconds"]].mean().round(2)
    out.append(lad.reindex(pd.MultiIndex.from_product([sorted(both.gen.unique()), order])).to_markdown())

    rkk = j.pivot_table(index=["gen", "task", "rep", "arm"], columns="judge", values="overall").dropna()
    out.append(f"\nJudge agreement on overall: r = {rkk['opus'].corr(rkk['sol']):.2f} (n={len(rkk)})\n")
    rp = j.pivot_table(index=["judge", "gen", "task", "arm"], columns="rep", values="overall")
    out.append(f"Rep noise (mean range, highest minus lowest rep): {(rp.max(axis=1) - rp.min(axis=1)).mean():.2f}\n")
    (E2 / "scores" / "summary.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()

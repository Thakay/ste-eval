"""Two-arm comparison for any experiment folder: treatment minus control, paired, with bootstrap intervals.

Inputs: <exp>/arms.json (first arm = control, second = treatment, unless --control/--treatment),
<exp>/runs, <exp>/scores/metrics.csv (from metrics.py), and if present <exp>/scores/judge and
<exp>/scores/reader. Output: <exp>/scores/compare.md (printed too).
Usage: STE_EXP=<folder> compare.py [--control ARM] [--treatment ARM]
"""
import argparse
import json
import os
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["overall", "checklist", "clarity", "actionability", "nuance", "naturalness", "esl_ease"]
METRICS = ["words_prose", "wps_mean", "pct_over_20", "pct_passive", "fk_grade", "thinking", "output_tokens", "seconds"]


def boot(diffs, n=4000):
    """Mean of paired differences with a 95% bootstrap interval; * when the interval excludes zero."""
    if not diffs:
        return "n/a"
    rng = random.Random(7)
    ms = sorted(sum(rng.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(n))
    m, lo, hi = sum(diffs) / len(diffs), ms[int(0.025 * n)], ms[int(0.975 * n)]
    return f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]" + ("*" if lo > 0 or hi < 0 else "")


def runs(exp: Path) -> pd.DataFrame:
    rows = []
    for mp in (exp / "runs").rglob("meta.json"):
        m = json.loads(mp.read_text())
        u = m["usage"]
        think = (u.get("output_tokens_details", {}).get("thinking_tokens", 0) if m["model"].startswith("claude")
                 else u.get("reasoning_output_tokens", 0))
        rows.append({"gen": m["model"], "arm": m["arm"], "task": m["task"], "rep": m["rep"], "seconds": m["seconds"],
                     "thinking": think, "output_tokens": u.get("output_tokens", 0),
                     "tool_calls": u.get("tool_calls", 0)})
    df = pd.DataFrame(rows)
    mpath = exp / "scores" / "metrics.csv"
    if mpath.exists():
        met = pd.read_csv(mpath).rename(columns={"model": "gen"}).drop(columns=["type", "path"], errors="ignore")
        df = df.merge(met, on=["gen", "arm", "task", "rep"], how="left")
    else:
        print(f"note: no {mpath.relative_to(ROOT)}; run metrics.py for the writing metrics", file=sys.stderr)
    rd = []
    for p in (exp / "scores" / "reader").glob("*.json"):
        d = json.loads(p.read_text())
        rd.append({"gen": d["gen"], "arm": d["arm"], "task": d["task"], "rep": d["rep"],
                   "reader": sum(d["scores"]) / len(d["scores"])})
    return df.merge(pd.DataFrame(rd), on=["gen", "arm", "task", "rep"], how="left") if rd else df


def judges(exp: Path) -> pd.DataFrame:
    rows = []
    for p in (exp / "scores" / "judge").rglob("*.json"):
        d = json.loads(p.read_text())
        v = d["verdict"]
        for lab, arm in d["label_to_arm"].items():
            a = v["answers"][lab]
            cl = a.get("checklist", [])
            rows.append({"judge": d["judge"], "gen": d["gen"], "task": d["task"], "rep": d["rep"], "arm": arm,
                         "checklist": sum(cl) / len(cl) if cl else None, "invented": len(a.get("invented", [])),
                         "errors": len(a.get("errors", [])), "won": int(v["ranking"][0] == lab),
                         **{k: a.get(k) for k in DIMS if k != "checklist"}})
    return pd.DataFrame(rows)


def main() -> None:
    if not os.environ.get("STE_EXP"):
        sys.exit("set STE_EXP to the experiment folder, for example STE_EXP=experiments/example")
    exp = ROOT / os.environ["STE_EXP"]
    arms = list(json.loads((exp / "arms.json").read_text()))
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", default=arms[0])
    ap.add_argument("--treatment", default=arms[1] if len(arms) > 1 else None)
    a = ap.parse_args()
    ctl, trt = a.control, a.treatment

    def paired(df, col, key):
        if col not in df:
            return "n/a"
        piv = df.pivot_table(index=key, columns="arm", values=col)
        if ctl not in piv or trt not in piv:
            return "n/a"
        return boot((piv[trt] - piv[ctl]).dropna().tolist())

    r, j = runs(exp), judges(exp)
    r = r[r.arm.isin([ctl, trt])]
    out = [f"# {trt} minus {ctl}\n",
           f"Experiment: `{os.environ['STE_EXP']}` | replies: {len(r)} | judge rows: {len(j)} | "
           f"tool calls: {int(r.tool_calls.fillna(0).sum())}\n",
           "Each cell: mean paired difference [95% bootstrap interval]; * = the interval excludes zero.\n"]

    if len(j):
        j = j[j.arm.isin([ctl, trt])]
        jk = ["judge", "gen", "task", "rep"]
        out.append("## Judge scores\n")
        rows = [{"scope": s, **{c: paired(d, c, jk) for c in DIMS}}
                for s, d in [("all models", j)] + [(g, j[j.gen == g]) for g in sorted(j.gen.unique())]]
        out.append(pd.DataFrame(rows).set_index("scope").to_markdown())
        out.append("\n### Overall, by judge\n")
        out.append(pd.DataFrame([{"judge": jj, "gen": g, "overall": paired(j[(j.judge == jj) & (j.gen == g)], "overall", jk)}
                                 for jj in sorted(j.judge.unique()) for g in sorted(j.gen.unique())]).to_markdown(index=False))
        win = j[j.arm == trt].groupby("gen")["won"].mean()
        out.append(f"\nJudges ranked {trt} first: {j[j.arm == trt].won.mean():.0%} overall; "
                   + ", ".join(f"{g} {w:.0%}" for g, w in win.items()) + "\n")
        out.append("\n### Means by model and arm\n")
        out.append(j.groupby(["gen", "arm"])[DIMS + ["invented", "errors"]].mean().round(2).to_markdown())
        if j.judge.nunique() > 1:
            pv = j.pivot_table(index=["gen", "task", "rep", "arm"], columns="judge", values="overall").dropna()
            out.append(f"\nJudge agreement on overall: r = {pv.iloc[:, 0].corr(pv.iloc[:, 1]):.2f} (n = {len(pv)})\n")
        if j.rep.nunique() > 1:
            rp = j.pivot_table(index=["judge", "gen", "task", "arm"], columns="rep", values="overall")
            reps = list(rp.columns)
            gaps = pd.concat([(rp[a] - rp[b]).abs() for i, a in enumerate(reps) for b in reps[i + 1:]]).dropna()
            out.append(f"Run-to-run noise (mean gap in overall between two runs of the same cell): {gaps.mean():.2f}\n")
    else:
        out.append("No judge files yet: run judge.py.\n")

    cols = [c for c in METRICS + ["reader"] if c in r]
    rk = ["gen", "task", "rep"]
    out.append("\n## Writing metrics, cost and the reading quiz\n")
    out.append(pd.DataFrame([{"gen": g, **{c: paired(r[r.gen == g], c, rk) for c in cols}}
                             for g in sorted(r.gen.unique())]).set_index("gen").to_markdown())
    out.append("\n### Means by model and arm\n")
    out.append(r.groupby(["gen", "arm"])[cols].mean().round(2).to_markdown())

    dest = exp / "scores" / "compare.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()

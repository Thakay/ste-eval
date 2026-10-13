"""Merge metrics, judge scores, reader scores, and run cost into tables.

Inputs: scores/metrics.csv (from metrics.py), scores/judge/**.json, scores/reader/*.json, runs/**/meta.json
Outputs: scores/long.csv (one row per run x judge), scores/summary.md (all tables)
"""
import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "scores"
ARMS = ["base", "lite", "scoped", "full"]
DIMS = ["clarity", "actionability", "nuance", "naturalness", "esl_ease", "overall"]


def load_runs() -> pd.DataFrame:
    rows = []
    for meta_path in (ROOT / "runs").rglob("meta.json"):
        m = json.loads(meta_path.read_text())
        u = m.get("usage", {})
        out_tok = u.get("output_tokens", 0)
        rows.append({"gen": m["model"], "arm": m["arm"], "task": m["task"], "type": m["type"],
                     "rep": m["rep"], "seconds": m["seconds"], "output_tokens": out_tok,
                     "tool_calls": u.get("tool_calls", 0), "cost_usd": u.get("cost_usd")})
    return pd.DataFrame(rows)


def load_judges() -> pd.DataFrame:
    rows = []
    for p in (S / "judge").rglob("*.json"):
        d = json.loads(p.read_text())
        v = d["verdict"]
        ranking = v.get("ranking", [])
        for lab, arm in d["label_to_arm"].items():
            a = v["answers"].get(lab, {})
            cl = a.get("checklist", [])
            row = {"judge": d["judge"], "gen": d["gen"], "task": d["task"], "rep": d["rep"], "arm": arm,
                   "checklist": sum(cl) / len(cl) if cl else None,
                   "invented": len(a.get("invented", [])), "errors": len(a.get("errors", [])),
                   "rank": ranking.index(lab) + 1 if lab in ranking else None}
            row.update({k: a.get(k) for k in DIMS})
            rows.append(row)
    return pd.DataFrame(rows)


def load_reader() -> pd.DataFrame:
    rows = []
    for p in (S / "reader").glob("*.json"):
        d = json.loads(p.read_text())
        rows.append({"gen": d["gen"], "arm": d["arm"], "task": d["task"], "rep": d["rep"],
                     "reader": sum(d["scores"]) / len(d["scores"])})
    return pd.DataFrame(rows)


def boot_delta(df: pd.DataFrame, col: str, arm: str, n: int = 2000) -> str:
    """Mean paired difference arm - base over groups, with a 95% bootstrap interval."""
    key = ["gen", "task", "rep"] + (["judge"] if "judge" in df else [])
    piv = df.pivot_table(index=key, columns="arm", values=col)
    if arm not in piv or "base" not in piv:
        return "n/a"
    diff = (piv[arm] - piv["base"]).dropna().tolist()
    if not diff:
        return "n/a"
    rng = random.Random(7)
    means = sorted(sum(rng.choices(diff, k=len(diff))) / len(diff) for _ in range(n))
    m = sum(diff) / len(diff)
    lo, hi = means[int(0.025 * n)], means[int(0.975 * n)]
    flag = "*" if lo > 0 or hi < 0 else ""
    return f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]{flag}"


def md(df: pd.DataFrame) -> str:
    return df.to_markdown(floatfmt=".2f")


def main() -> None:
    runs = load_runs()
    metrics = pd.read_csv(S / "metrics.csv")
    metrics["gen"] = metrics["model"]
    judges = load_judges()
    reader = load_reader()
    key = ["gen", "arm", "task", "rep"]
    per_run = runs.merge(metrics.drop(columns=["model", "type", "path"]), on=key, how="left")
    if not reader.empty:
        per_run = per_run.merge(reader, on=key, how="left")
    long = per_run.merge(judges, on=key, how="left")
    long.to_csv(S / "long.csv", index=False)

    ste_cols = ["words_prose", "wps_mean", "pct_over_20", "pct_over_25", "pct_passive", "ing_per_100w",
                "noun_clusters_gt3", "paras_gt6_sents", "hedges_per_100w", "may_should_per_100w",
                "perfect_tense", "progressive_tense", "semicolons", "contractions", "fk_grade", "em_dashes"]
    cost_cols = ["output_tokens", "seconds", "tool_calls"]
    judge_cols = ["checklist", "invented", "errors"] + DIMS + ["rank"]
    out = ["# STE A/B results\n",
           f"Runs: {len(runs)}  |  judge rows: {len(judges)}  |  reader quizzes: {len(reader)}\n"]

    out.append("## 1. STE compliance and cost by arm (both models)\n")
    out.append(md(per_run.groupby("arm")[ste_cols + cost_cols].mean().reindex(ARMS)))
    out.append("\n## 2. Quality by arm (judge mean, both judges, both models)\n")
    q = long.groupby("arm")[judge_cols].mean().reindex(ARMS)
    if "reader" in per_run:
        q["reader_quiz"] = per_run.groupby("arm")["reader"].mean().reindex(ARMS)
    out.append(md(q))

    out.append("\n## 3. Paired delta vs base (mean [95% bootstrap CI], * = interval excludes 0)\n")
    jd = judges.copy()
    rows = []
    for arm in ARMS[1:]:
        r = {"arm": arm}
        for c in ["overall", "checklist", "clarity", "esl_ease", "nuance", "naturalness"]:
            r[c] = boot_delta(jd, c, arm)
        for c in ["words_prose", "wps_mean", "pct_passive", "output_tokens"]:
            r[c] = boot_delta(per_run, c, arm)
        if "reader" in per_run:
            r["reader_quiz"] = boot_delta(per_run, "reader", arm)
        rows.append(r)
    out.append(pd.DataFrame(rows).set_index("arm").to_markdown())

    out.append("\n## 4. By generator model and arm\n")
    out.append(md(long.groupby(["gen", "arm"])[["overall", "checklist", "esl_ease", "nuance", "naturalness", "rank"]].mean()))
    out.append("\n")
    out.append(md(per_run.groupby(["gen", "arm"])[["words_prose", "wps_mean", "pct_over_25", "pct_passive", "output_tokens", "seconds"]].mean()))

    out.append("\n## 5. Overall score by task type and arm (judge mean)\n")
    types = per_run[["task", "type"]].drop_duplicates().set_index("task")["type"]
    long["type"] = long["task"].map(types)
    out.append(md(long.pivot_table(index=["task", "type"], columns="arm", values="overall").reindex(columns=ARMS)))
    out.append("\n### Checklist coverage by task type and arm\n")
    out.append(md(long.pivot_table(index=["task", "type"], columns="arm", values="checklist").reindex(columns=ARMS)))

    out.append("\n## 6. Win rate vs base (share of judge groups where the arm ranked above base)\n")
    wins = []
    piv = judges.pivot_table(index=["judge", "gen", "task", "rep"], columns="arm", values="rank")
    for arm in ARMS[1:]:
        w = (piv[arm] < piv["base"]).mean()
        wins.append({"arm": arm, "win_rate_vs_base": round(float(w), 2),
                     "by_opus_judge": round(float((piv.loc["opus"][arm] < piv.loc["opus"]["base"]).mean()), 2) if "opus" in piv.index.get_level_values(0) else None,
                     "by_sol_judge": round(float((piv.loc["sol"][arm] < piv.loc["sol"]["base"]).mean()), 2) if "sol" in piv.index.get_level_values(0) else None})
    out.append(pd.DataFrame(wins).set_index("arm").to_markdown())

    out.append("\n## 7. Judge agreement and self-preference\n")
    rk = judges.pivot_table(index=["gen", "task", "rep", "arm"], columns="judge", values="overall").dropna()
    if {"opus", "sol"} <= set(rk.columns):
        out.append(f"Pearson r between judges on overall: {rk['opus'].corr(rk['sol']):.2f} "
                   f"(Spearman {rk['opus'].rank().corr(rk['sol'].rank()):.2f}), n={len(rk)}\n")
    out.append(md(judges.groupby(["judge", "gen"])["overall"].mean().unstack()))

    out.append("\n## 8. Rep-to-rep noise (mean absolute difference between rep 1 and rep 2, judge overall)\n")
    rp = judges.pivot_table(index=["judge", "gen", "task", "arm"], columns="rep", values="overall").dropna()
    if {1, 2} <= set(rp.columns):
        out.append(f"{(rp[1] - rp[2]).abs().mean():.2f} points on the 1-10 scale\n")

    (S / "summary.md").write_text("\n".join(out))
    print((S / "summary.md").read_text())


if __name__ == "__main__":
    main()

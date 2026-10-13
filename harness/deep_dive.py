"""Extra cuts for the report: judge x generator x arm, thinking vs visible tokens, artifacts."""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ARMS = ["base", "lite", "scoped", "full"]
long = pd.read_csv(ROOT / "scores" / "long.csv")

print("## A. Overall by judge x generator x arm (separates self-preference from arm effect)\n")
print(long.pivot_table(index=["judge", "gen"], columns="arm", values="overall").reindex(columns=ARMS).round(2).to_markdown())
print("\n## A2. Nuance and naturalness by generator x arm\n")
for col in ["nuance", "naturalness", "esl_ease", "checklist"]:
    print(f"\n{col}\n")
    print(long.pivot_table(index="gen", columns="arm", values=col).reindex(columns=ARMS).round(2).to_markdown())

print("\n## A3. Rank (1 best, 4 worst) by judge x generator x arm\n")
print(long.pivot_table(index=["judge", "gen"], columns="arm", values="rank").reindex(columns=ARMS).round(2).to_markdown())

rows = []
for meta in (ROOT / "runs").rglob("meta.json"):
    m = json.loads(meta.read_text())
    u = m["usage"]
    if m["model"].startswith("claude"):
        think = u.get("output_tokens_details", {}).get("thinking_tokens", 0)
        inp = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    else:
        think = u.get("reasoning_output_tokens", 0)
        inp = u.get("input_tokens", 0)
    out = u.get("output_tokens", 0)
    text = (meta.parent / "output.md").read_text()
    rows.append({"gen": m["model"], "arm": m["arm"], "task": m["task"], "input_tokens": inp,
                 "thinking": think, "visible_out": out - think, "seconds": m["seconds"],
                 "cost_usd": u.get("cost_usd"),
                 "mentions_ste": bool(re.search(r"STE|Simplified Technical|ASD", text)),
                 "kept_as_is": "Kept as-is" in text,
                 "bullets": len(re.findall(r"^\s*([-*]|\d+\.)\s", text, flags=re.M)),
                 "bold": text.count("**") // 2})
t = pd.DataFrame(rows)
print("\n## B. Tokens: thinking vs visible, by generator x arm (means per reply)\n")
print(t.groupby(["gen", "arm"])[["input_tokens", "thinking", "visible_out", "seconds", "cost_usd"]].mean().round(1).to_markdown())
print("\n## C. Artifacts and formatting\n")
print(t.groupby("arm")[["mentions_ste", "kept_as_is", "bullets", "bold"]].mean().reindex(ARMS).round(2).to_markdown())

print("\n## D. Invented facts and errors listed by judges, per arm (count)\n")
inv = []
for p in (ROOT / "scores" / "judge").rglob("*.json"):
    d = json.loads(p.read_text())
    for lab, arm in d["label_to_arm"].items():
        a = d["verdict"]["answers"].get(lab, {})
        for x in a.get("invented", []):
            inv.append((arm, d["gen"], d["task"], d["judge"], "invented", x))
        for x in a.get("errors", []):
            inv.append((arm, d["gen"], d["task"], d["judge"], "error", x))
iv = pd.DataFrame(inv, columns=["arm", "gen", "task", "judge", "kind", "text"])
print(iv.groupby(["arm", "kind"]).size().unstack().reindex(ARMS).to_markdown())
iv.to_csv(ROOT / "scores" / "invented_errors.csv", index=False)

"""Blind cross-family judging. One call per (generator, task, rep) group per judge.

Each judge sees the 4 arm outputs for one group, shuffled with its own seed, labeled A-D.
Writes scores/judge/<judge>/<generator>__<task>__r<rep>.json with the label map kept separately.
Usage: judge.py [--jobs N] [--judges opus,sol]
"""
import argparse
import json
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import clients

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / os.environ.get("STE_EXP", "")
TASKS_FILE = EXP / "tasks.json" if (EXP / "tasks.json").exists() else ROOT / "dataset" / "tasks.json"
TASKS = {t["id"]: t for t in json.loads(TASKS_FILE.read_text())}
TEMPLATE = (ROOT / "harness" / "judge_prompt.md").read_text()
ARMS = list(json.loads(((EXP if (EXP / "arms.json").exists() else ROOT / "harness") / "arms.json").read_text()))
JUDGES = {
    "opus": lambda p: clients.claude(p, "opus", "high"),
    "sol": lambda p: clients.codex(p, "gpt-6.1-sol", "high"),
}


def groups() -> list[tuple[str, str, int]]:
    out = []
    for gen_dir in sorted((EXP / "runs").iterdir()):
        reps = sorted({int(p.name[1:]) for p in gen_dir.glob("*/*/r*")})
        for task in TASKS:
            for rep in reps:
                if all((gen_dir / arm / task / f"r{rep}" / "output.md").exists() for arm in ARMS):
                    out.append((gen_dir.name, task, rep))
    return out


def judge_group(judge: str, gen: str, task_id: str, rep: int) -> str:
    dest = EXP / "scores" / "judge" / judge / f"{gen}__{task_id}__r{rep}.json"
    if dest.exists():
        return f"skip {dest.name}"
    rng = random.Random(f"{judge}|{gen}|{task_id}|{rep}")
    arms = ARMS[:]
    rng.shuffle(arms)
    labels = "ABCD"[: len(arms)]
    task = TASKS[task_id]
    answers = "\n\n".join(
        f"=== ANSWER {lab} ===\n" + (EXP / "runs" / gen / arm / task_id / f"r{rep}" / "output.md").read_text()
        for lab, arm in zip(labels, arms))
    checklist = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(task["checklist"]))
    prompt = (TEMPLATE.replace("{N}", str(len(arms))).replace("{LABELS}", ", ".join(labels))
              .replace("{TASK}", task["prompt"]).replace("{CHECKLIST}", checklist)
              .replace("{ANSWERS}", answers))
    last_err = None
    for _ in range(2):
        text, meta = JUDGES[judge](prompt)
        try:
            verdict = clients.extract_json(text)
            break
        except ValueError as e:
            last_err = e
    else:
        return f"FAIL {dest.name}: {last_err}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"judge": judge, "gen": gen, "task": task_id, "rep": rep,
                                "label_to_arm": dict(zip(labels, arms)), "verdict": verdict,
                                "meta": meta}, indent=2))
    return f"ok   {dest.name} ({judge})"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--judges", default="opus,sol")
    a = ap.parse_args()
    jobs = [(j, *g) for j in a.judges.split(",") for g in groups()]
    print(f"{len(jobs)} judge calls")
    with ThreadPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(judge_group, *j) for j in jobs]):
            try:
                print(f.result(), flush=True)
            except Exception as e:
                print(f"ERR  {e}", flush=True)


if __name__ == "__main__":
    main()

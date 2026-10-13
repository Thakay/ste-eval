"""Reader quiz: a small model reads only the reply and answers 3 questions; a grader scores them.

Reader: Claude Haiku (low effort). Grader: Claude Sonnet (medium effort), sees answers and the key.
Writes scores/reader/<generator>__<arm>__<task>__r<rep>.json
Usage: reader.py [--jobs N]
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import clients

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / os.environ.get("STE_EXP", "")
TASKS_FILE = EXP / "tasks.json" if (EXP / "tasks.json").exists() else ROOT / "dataset" / "tasks.json"
TASKS = {t["id"]: t for t in json.loads(TASKS_FILE.read_text())}
READ_T = (ROOT / "harness" / "reader_prompt.md").read_text()
GRADE_T = (ROOT / "harness" / "grade_prompt.md").read_text()


def quiz(out: Path) -> str:
    gen, arm, task_id, rep = out.relative_to(EXP / "runs").parts[:4]
    dest = EXP / "scores" / "reader" / f"{gen}__{arm}__{task_id}__{rep}.json"
    if dest.exists():
        return f"skip {dest.name}"
    qs = TASKS[task_id]["reader_questions"]
    questions = "\n".join(f"{i + 1}. {q['q']}" for i, q in enumerate(qs))
    text, _ = clients.claude(READ_T.replace("{TEXT}", out.read_text()).replace("{QUESTIONS}", questions),
                             "haiku", "low")
    answers = clients.extract_json(text)["answers"]
    items = "\n\n".join(f"Question {i + 1}: {q['q']}\nAnswer key: {q['a']}\nReader's answer: {a}"
                        for i, (q, a) in enumerate(zip(qs, answers)))
    gtext, _ = clients.claude(GRADE_T.replace("{ITEMS}", items), "sonnet", "medium")
    scores = clients.extract_json(gtext)["scores"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"gen": gen, "arm": arm, "task": task_id, "rep": int(rep[1:]),
                                "answers": answers, "scores": scores}, indent=2))
    return f"ok   {dest.name} {sum(scores)}/{len(scores)}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args()
    outs = sorted((EXP / "runs").rglob("output.md"))
    print(f"{len(outs)} quizzes")
    with ThreadPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(quiz, o) for o in outs]):
            try:
                print(f.result(), flush=True)
            except Exception as e:
                print(f"ERR  {e}", flush=True)


if __name__ == "__main__":
    main()

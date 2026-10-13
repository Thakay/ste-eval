"""Run the generation grid: tasks x arms x models x reps, in parallel.

Each run gets its own empty work dir under /tmp/ste-runs/<cell>/ so no project CLAUDE.md or
AGENTS.md leaks in. The arm's rule file (if any) is copied into that dir as CLAUDE.md (Claude)
or AGENTS.md (Codex), which is exactly how a project-level adoption would load.
Outputs: runs/<model>/<arm>/<task>/r<rep>/{output.md,meta.json,raw.txt}

Usage: run.py [--only MODEL] [--tasks T1,T2] [--reps N] [--jobs N] [--dry]
Set STE_EXP=<folder> to run another experiment: it reads <folder>/arms.json, <folder>/models.json and,
if present, <folder>/tasks.json (otherwise dataset/tasks.json),
and writes <folder>/runs/.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / os.environ.get("STE_EXP", "")
CONF = EXP if (EXP / "arms.json").exists() else ROOT / "harness"
TASKS_FILE = EXP / "tasks.json" if (EXP / "tasks.json").exists() else ROOT / "dataset" / "tasks.json"
TASKS = json.loads(TASKS_FILE.read_text())
ARMS = json.loads((CONF / "arms.json").read_text())
MODELS = json.loads((CONF / "models.json").read_text())
WORK = Path("/tmp/ste-runs") / os.environ.get("STE_EXP", "exp1")
SUFFIX = "\n\n(Answer directly from what you know. Do not run commands or look anything up.)"
NODE_BIN = os.environ.get("STE_NODE_BIN", "")  # folder with node, if the CLIs need it on PATH
ID_RE = re.compile(r'"(session_id|thread_id|uuid)":"[0-9a-f-]{20,}"')  # keep run IDs out of the logs


def build_cmd(model: dict, prompt: str) -> list[str]:
    return [part.replace("{PROMPT}", prompt) for part in model["cmd"]]


def run_one(model_key: str, arm_key: str, task: dict, rep: int, dry: bool) -> str:
    model, arm = MODELS[model_key], ARMS[arm_key]
    cell = f"{model_key}/{arm_key}/{task['id']}/r{rep}"
    out_dir = EXP / "runs" / cell
    if (out_dir / "output.md").exists():
        return f"skip {cell}"
    wd = WORK / cell.replace("/", "__")
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir(parents=True)
    if model.get("git_init"):
        subprocess.run(["git", "init", "-q"], cwd=wd, check=True)
    if arm.get("rules_file"):
        shutil.copy(ROOT / arm["rules_file"], wd / model["rules_name"])
    cmd = build_cmd(model, task["prompt"] + SUFFIX)
    if dry:
        return f"dry {cell}: {' '.join(cmd[:6])} ..."
    start = time.time()
    env = dict(os.environ)
    if NODE_BIN:
        env["PATH"] = NODE_BIN + ":" + env["PATH"]
    env.update(model.get("env", {}))
    if "CODEX_HOME" in model.get("env", {}):
        # bare Codex home: only a link to the real login file, so no global AGENTS.md, config or memories
        home = Path(env["CODEX_HOME"])
        home.mkdir(parents=True, exist_ok=True)
        if not (home / "auth.json").exists():
            (home / "auth.json").symlink_to(Path.home() / ".codex" / "auth.json")
    proc = subprocess.run(cmd, cwd=wd, env=env, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=1800)
    elapsed = round(time.time() - start, 1)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = proc.stdout + "\n--- STDERR ---\n" + proc.stderr
    (out_dir / "raw.txt").write_text(ID_RE.sub(r'"\1":"redacted"', raw))
    text, usage = model_parse(model_key, proc.stdout, wd)
    meta = {"model": model_key, "arm": arm_key, "task": task["id"], "type": task["type"],
            "rep": rep, "seconds": elapsed, "exit": proc.returncode, "usage": usage}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    if proc.returncode == 0 and text.strip():
        (out_dir / "output.md").write_text(text)
        return f"ok   {cell} {elapsed}s"
    return f"FAIL {cell} exit={proc.returncode}"


def model_parse(model_key: str, stdout: str, wd: Path) -> tuple[str, dict]:
    """Pull the final reply text and token usage out of each CLI's JSON output."""
    if model_key.startswith("claude"):
        data = json.loads(stdout)
        return data.get("result", ""), data.get("usage", {}) | {"cost_usd": data.get("total_cost_usd")}
    # codex exec --json: JSONL events; last message also written via -o
    last = (wd / "last.md").read_text() if (wd / "last.md").exists() else ""
    usage = {"tool_calls": 0}
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "turn.completed":
            usage.update(ev.get("usage", {}))
        if ev.get("type") == "item.completed" and ev.get("item", {}).get("type") == "command_execution":
            usage["tool_calls"] += 1
    return last, usage


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--tasks")
    ap.add_argument("--arms")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    tasks = [t for t in TASKS if not a.tasks or t["id"] in a.tasks.split(",")]
    models = [a.only] if a.only else list(MODELS)
    arms = a.arms.split(",") if a.arms else list(ARMS)
    jobs = [(m, arm, t, r) for m in models for arm in arms for t in tasks for r in range(1, a.reps + 1)]
    print(f"{len(jobs)} runs")
    with ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(run_one, *j, a.dry) for j in jobs]
        for f in as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # keep the grid going; failures are listed and rerun
                print(f"ERR  {e}", flush=True)


if __name__ == "__main__":
    main()

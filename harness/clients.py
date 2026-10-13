"""Thin headless wrappers for scoring calls (judges, reader, grader). No tools, clean work dir."""
import json
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

NODE_BIN = os.environ.get("STE_NODE_BIN", "")  # folder with node, if codex needs it on PATH
SCRATCH = Path("/tmp/ste-score")


def _workdir() -> Path:
    wd = SCRATCH / uuid.uuid4().hex[:12]
    wd.mkdir(parents=True)
    return wd


def claude(prompt: str, model: str, effort: str) -> tuple[str, dict]:
    wd = _workdir()
    cmd = ["claude", "-p", prompt, "--model", model, "--effort", effort, "--tools", "",
           "--strict-mcp-config", "--permission-mode", "dontAsk", "--no-session-persistence",
           "--output-format", "json"]
    proc = subprocess.run(cmd, cwd=wd, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, timeout=1800)
    shutil.rmtree(wd, ignore_errors=True)
    data = json.loads(proc.stdout)
    return data.get("result", ""), {"usage": data.get("usage", {}), "cost_usd": data.get("total_cost_usd")}


def codex(prompt: str, model: str, effort: str) -> tuple[str, dict]:
    wd = _workdir()
    env = dict(os.environ, PATH=NODE_BIN + ":" + os.environ["PATH"]) if NODE_BIN else None
    cmd = ["codex", "exec", "-m", model, "-c", f'model_reasoning_effort="{effort}"',
           "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
           "-c", "features.apps=false", "-c", "features.browser_use=false",
           "--sandbox", "read-only", "--skip-git-repo-check", "--ephemeral", "--json",
           "-o", "last.md", prompt]
    proc = subprocess.run(cmd, cwd=wd, env=env, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, timeout=1800)
    text = (wd / "last.md").read_text() if (wd / "last.md").exists() else ""
    usage = {}
    for line in proc.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "turn.completed":
            usage = ev.get("usage", {})
    shutil.rmtree(wd, ignore_errors=True)
    return text, {"usage": usage}


def extract_json(text: str) -> dict:
    """Take the outermost JSON object from a reply that may carry extra lines (send-offs, fences)."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in reply")
    blob = text[start:end + 1]
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return json.loads(re.sub(r",\s*([}\]])", r"\1", blob))

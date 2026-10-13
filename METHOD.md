# Method

This is the reference spec for the STE eval: what it tests, how each reply was made and scored, and why each design choice is there. Results are in [REPORT.md](REPORT.md). Rerun commands are in [README.md](README.md).

## 1. What it tests

A common tip says to make a coding agent write in ASD-STE100 Simplified Technical English (STE), the controlled English of aircraft maintenance manuals. Each round asks one question:

1. On top of a setup that already asks for plain language, do STE rule files make an agent's replies better for its readers, and at what cost?
2. Does the tip as people share it, one line on a vanilla CLI, change the writing, and at what cost?

The reader is mixed. Every judge prompt names the same persona: a senior developer (me) who reads fast and wants the decision first, other AI agents that act on handoffs, and teammates, some of whom read English as a second language.

## 2. Design at a glance

| | Round one | Round two |
|---|---|---|
| Setup under the arms | My real user config | Bare CLIs: no user rules, output style, hooks or Codex memories |
| Arms | base, lite, scoped, full | bare, oneliner |
| Generators | Claude Code with `claude-opus-5-5`, Codex with `gpt-6.1-sol`, both at xhigh effort | Same |
| Tasks | 8 | 8 |
| Reps per cell | 2 | 3 |
| Replies | 128 | 96 |
| Judge calls (2 judges) | 64, each over 4 replies | 96, each over 2 replies |
| Reading quizzes | 128 | 96 |

Totals: 224 replies, 160 judge calls and 224 quizzes. Every reply is a single turn with no tools.

## 3. Tasks

`dataset/tasks.json` holds 8 tasks, from STE's home turf (procedures, warnings) to text STE was not built for (tradeoffs, argument). My research predicted that STE would help or be neutral for procedures and descriptions and might hurt discussion (`research/01-standard-and-evidence.md`, section 7).

| ID | Genre | The task | Checklist items |
|---|---|---|---|
| T1 | procedure | Nightly Postgres backup in Docker, with a restore test | 7 |
| T2 | explanation | Explain `git rebase main` to a junior developer | 6 |
| T3 | tradeoff | SQLite or Postgres for a small SaaS (expected to be STE's weakest genre) | 7 |
| T4 | handoff | Turn messy notes into a handoff | 8 |
| T5 | incident | Explain a Docker Compose connection error from logs | 6 |
| T6 | warning | Risky deletes on a nearly full prod disk | 7 |
| T7 | code review | Review a pagination diff that has several bugs | 6 |
| T8 | discussion | Answer pushback on caching advice after a stale-price incident | 6 |

Each task has a hidden fact checklist (53 items in all) that only the judges see, and a 3-question reading quiz with an answer key. Tasks are invented scenarios. Names, places, companies and incidents are fictional.

### Worked example: T4 (handoff)

The prompt is a set of raw session notes. An excerpt:

```
- test_invoice_due_dates flaky on CI, passes local. ~1 in 5 runs fail
- fails when CI run is between 22:00 and 00:00 UTC?? not 100% sure on window,
  saw 3 failures all after 22:10 UTC
- changed invoice.py to datetime.now(timezone.utc) on branch fix/invoice-tz,
  NOT pushed, 2 other tests now fail (test_late_fee, test_reminder_email)
- don't merge anything until Priya answers
```

The checklist, trimmed (each item scores 0 or 1):

1. Root cause: naive local `datetime.now()` compared with UTC dates from the DB.
2. Evidence with its uncertainty: 3 failures, all after 22:10 UTC; window not confirmed.
3. Branch `fix/invoice-tz` is local and not pushed.
4. Names the 2 newly failing tests.
5. Blocker: Priya must say if due dates are UTC or customer local time; no merge until then.
6. freezegun was tried and rejected because it hides the real bug.
7. The reminder cron may have the same bug and was not checked.
8. Invents no facts that are not in the notes.

| Quiz question | Key |
|---|---|
| Is the fix branch pushed? | No, it is only local |
| Who must answer what before anything is merged? | Priya must say if due dates are in UTC or customer local time |
| Which two tests fail with the fix? | test_late_fee and test_reminder_email |

T4 targets the main risk my research found for simplified writing: facts drop out without notice, and a hedge such as "not 100% sure" can harden into a flat claim. Items 2 and 8 catch both.

## 4. Arms

Round one puts each rule file on top of my setup:

| Arm | What loads | Size |
|---|---|---|
| base | My global `CLAUDE.md`, my Codex `AGENTS.md` and my Claude output style (snapshots in `baseline/`) | 0 extra |
| lite | `arms/ste-lite.md`: compact STE rules, always on | 187 words |
| scoped | `arms/ste-scoped.md`: strict for procedures, warnings, handoffs and docs, relaxed for discussion | 245 words |
| full | `arms/ste-full.md`: danyuchn/asd-ste100-skill at commit 32511c6 (MIT), plus a header that turns it on for every reply | 2,639 words |

The base is my real setup, which already has a one-line plain-language rule. So round one tests what STE adds to a strong setup, which was the decision I faced. My survey of 23 STE skills on skills.sh (`research/02-skills-sh-candidates.md`) rates Full the most faithful rewrite tool. It loads as a rule file, so it is always on.

Round two drops my setup. It compares bare CLIs with bare CLIs plus `exp2/oneliner.md`, which holds one line: `Speak only in ASD-STE100`. This is the tip as people share it, and it tests what the models know about STE from its name alone.

Copyright shaped the arms. ASD's notice forbids reproducing any part of the standard's text or dictionary without written permission. Lite and Scoped are my own paraphrases, and Full is a third-party paraphrase under MIT. The one line quotes nothing. Neither this file nor the repo contains STE rule text or dictionary entries, and the fetched survey copies stay unpublished because two of them ship the dictionary.

## 5. Running the models

`harness/run.py` reads the commands from `harness/models.json` (round one) and `exp2/models.json` (round two). Every task prompt ends with this line:

```
(Answer directly from what you know. Do not run commands or look anything up.)
```

Claude Code (round two adds `--setting-sources project,local`):

```bash
claude -p "<prompt + suffix>" --model opus --effort xhigh --tools "" \
  --strict-mcp-config --permission-mode dontAsk --no-session-persistence \
  --output-format json
```

Codex (round two sets `CODEX_HOME=/tmp/codex-bare-home`):

```bash
codex exec -m gpt-6.1-sol -c 'model_reasoning_effort="xhigh"' \
  -c 'approval_policy="never"' -c 'web_search="disabled"' \
  -c features.apps=false -c features.browser_use=false \
  --sandbox read-only --skip-git-repo-check --ephemeral --json \
  -o last.md "<prompt + suffix>"
```

| Flag | Why it is there |
|---|---|
| `--tools ""` | No built-in tools, so the reply comes from what the model knows |
| `--strict-mcp-config` | No `--mcp-config` is given, so none of my MCP servers load |
| `--permission-mode dontAsk`, `approval_policy="never"` | A headless run must never wait for a prompt |
| `--no-session-persistence`, `--ephemeral` | No saved sessions to resume or to mix into my history |
| `--output-format json`, `--json` | Machine-readable reply and usage; Codex's event stream also lists every tool item |
| `web_search="disabled"`, `features.apps=false`, `features.browser_use=false` | Codex has its own web search, apps and browser; Claude had no web, and these put both on equal terms |
| `--sandbox read-only` | Even if Codex ran a command, it could not change anything |
| `--skip-git-repo-check` | The work dir is not a git repo, and Codex refuses to run outside one by default |
| `-o last.md` | Codex's final message goes to a file, which becomes `output.md` |
| Prompt suffix | Tells both models not to reach for tools (section 7) |

Each run saves `output.md` (the reply), `meta.json` (seconds, exit code, usage) and `raw.txt` (CLI output, session IDs redacted).

## 6. Isolation

Each run gets a fresh empty folder under `/tmp/ste-runs/`, and the arm's rule file is copied in as `CLAUDE.md` or `AGENTS.md`. No project file from this repo can leak in, and the rule loads exactly the way a project rule loads in real use. Nothing enforces STE: no hook or linter checks the reply.

Round two runs the CLIs bare. Claude's `--bare` mode needs an API key, and these runs used the normal sign-in, so Claude ran with `--setting-sources project,local`, which skips user settings. Codex ran with a `CODEX_HOME` that holds only a symlink to `~/.codex/auth.json`: the login works, and no global `AGENTS.md`, config or memories load.

A canary checks this. My Claude output style and my Codex `AGENTS.md` both ask for a short "warrior send-off" at the end of every reply, and round one replies often end with one. None of the 96 round-two replies has a send-off, so neither file loaded. Codex gives a second, weaker sign: my `AGENTS.md` bans em dashes, and Codex used none in its 64 round-one replies, while its bare round-two replies used 9 across 5 of 24. My global `CLAUDE.md` leaves no visible mark on a reply, so for that file the isolation rests on the flag alone.

## 7. Contamination controls

The first smoke run almost broke the comparison. Codex searched Docker's documentation before it answered, while Claude had no web access. The two models were no longer answering under the same conditions, and a reply could carry facts from a live lookup.

The fix:

- Codex runs with web search, apps and the browser off, in a read-only sandbox.
- Every prompt, for both models, ends with the suffix line.
- `run.py` counts tool items in Codex's event stream and records the count as `tool_calls` in `meta.json`.
- Any run with a tool call is discarded.

None had to be: there were zero tool calls in 224 replies. The `tool_calls` counter only counts command executions, so a web search would slip past it. Two more checks close that gap. Each of the 112 Codex event streams holds exactly one item, the final message. Claude's JSON output reports `server_tool_use`, and its web search and web fetch counters are zero in all 112 Claude replies.

The judge and quiz calls use the same no-tool flags (`harness/clients.py`), each in a fresh empty folder.

## 8. Judging

`harness/judge.py` makes one call per (generator, task, rep) group per judge. A group holds every arm's reply for that cell: 4 in round one, 2 in round two. All replies in a group come from one generator, so a judge compares arms within one model. A group is judged only when all its replies exist, so judging can start while generation still runs.

The replies are shuffled with a seed per judge and group (`random.Random("<judge>|<gen>|<task>|<rep>")`) and labeled A to D, or A and B. The label map (`label_to_arm`) is saved next to the verdict and never enters the prompt, which shows no arm names and no rule files.

The rubric, trimmed from `harness/judge_prompt.md`:

```
Judge each answer on its own merits. Do not prefer an answer because it is
longer or shorter. Do not guess which instructions produced which answer.

For each answer, give:
- "checklist": an array of 0 or 1, one per checklist item in order
- "invented": one short string per fact that is not supported by the task
  and is wrong or made up
- "errors": one short string per technical mistake
- "clarity", "actionability", "nuance", "naturalness", "esl_ease": 1-5 each
- "overall" 1-10: how good this answer is for the mixed readers
- "note": one sentence on the main strength or weakness

Then give "ranking": the labels from best to worst.
```

The judge replies with one JSON object. The parser takes the outermost `{...}` and drops trailing commas. If nothing parses, the call runs once more, and a second failure leaves no file for the next pass to redo.

The two judges come from different model families: Claude Opus and `gpt-6.1-sol`, both at effort high. Each favors its own family:

| Mean overall score (1-10) | Claude replies | Codex replies |
|---|---|---|
| Opus judge, round one | 7.98 | 7.05 |
| sol judge, round one | 7.59 | 7.86 |
| Opus judge, round two | 8.10 | 7.08 |
| sol judge, round two | 7.79 | 7.94 |

Agreement on the overall score is moderate: Pearson r = 0.45 in round one (128 replies) and 0.46 in round two (96 replies). So I claim a result only when both judges point the same way. In round two, both judges score Codex's one-line replies lower than its bare ones (Opus judge -0.92, sol judge -0.79, both intervals exclude zero). For Claude they split (Opus judge -0.71 with an interval that excludes zero, sol judge +0.17 without), so I make no claim about Claude's overall score. Judge scores are relative to the other replies in a call, so only metrics are compared across rounds.

The judges ran under my normal user config (no `--setting-sources` override, my usual Codex home). Both carried my plain-language rule, and the Claude judge also carried my output style, which may tilt them toward plain text. The same config is why the parser accepts extra lines around the JSON: a judge's reply can end with a send-off.

## 9. Reading quiz

`harness/reader.py` quizzes every reply. Claude Haiku at low effort gets only the reply and the 3 questions. It must use only the text, answer "NOT STATED" when the text does not say, and keep each answer under 20 words. Claude Sonnet at medium effort grades each answer 0 or 1 against the key, on the main point only. Text in the key after "for example" or inside parentheses is an illustration, so an answer that names another valid command or detail still scores 1.

The quiz is a weak proxy. A language model reads long sentences without trouble, so it does not feel what a person reading in a second language feels. It also moved little: in round one, no arm's quiz change had an interval that excludes zero.

## 10. Metrics

`harness/metrics.py` uses spaCy 3.8.16 (`en_core_web_sm` 3.8.0) and textstat 0.7.13. It first reduces the reply to prose: it removes fenced code, turns inline code into one placeholder word, drops table rows and headings, and strips markup. Each list item becomes its own block, so long text cannot hide in bullets that merge into one sentence.

| Metric | How it is computed |
|---|---|
| Prose words | spaCy tokens that are words or numbers; inline code counts as one word |
| Words per sentence | spaCy sentences in each block: mean, 90th percentile, maximum |
| Share over 20 and over 25 words | Share of all sentences longer than 20 or 25 words |
| Passive voice | Share of sentences with an `nsubjpass`, `auxpass` or `csubjpass` dependency |
| "-ing" forms | `VBG` tags per 100 prose words |
| Perfect tense | Count of past participles with a "have" auxiliary |
| Semicolons | Count in the prose |
| FK grade | textstat Flesch-Kincaid grade of the joined prose |

Sections 6.3 and 6.4 of the research notes explain these choices and their pitfalls. STE sets different length limits for instructions and descriptions, but the script applies both thresholds to every sentence. spaCy's small model mislabels some passives and "-ing" forms in technical text, and the FK grade rewards short sentences whether or not they read well.

Cost per reply comes from each CLI's own report. Thinking tokens are Claude's `usage.output_tokens_details.thinking_tokens` and Codex's `usage.reasoning_output_tokens` from the `turn.completed` event. Seconds are wall-clock time around the CLI call, start-up included. Cost is Claude's `total_cost_usd`, saved as `usage.cost_usd` in `meta.json`. Codex reports no cost.

## 11. Statistics

All comparisons are paired. For judge scores, a pair is two arms' replies with the same generator, task, rep and judge. For metrics, a pair shares generator, task and rep.

Each interval is a percentile bootstrap of the mean paired difference: resample the differences with replacement, take the mean, repeat, and read the 2.5th and 97.5th percentiles. Round one uses 2,000 resamples (`harness/analyze.py`) and round two uses 4,000 (`harness/analyze2.py`), both with seed 7. A star (*) marks an interval that excludes zero.

In round one, the same judge's overall score for the same cell moved 0.76 points on average between rep 1 and rep 2, which is why round two used 3 reps. Measured the same way across round two's 3 reps (the mean gap between any two of them), it was 0.56. Round two's summary also reports 0.84, which is the mean range (highest minus lowest) across the 3 reps, a different measure. With 8 tasks per model, per-task numbers are hints only.

Two cautions for reuse. The bootstrap treats every pair as independent, but each reply pair appears once per judge and each task repeats across reps, so the intervals are likely too narrow. The tables also test many cells with no correction for multiple comparisons, so a few stars are expected by chance.

## 12. Process

- The research notes and the harness came first, before any eval run.
- I approved the design (test counts, tasks, arms and scoring) before any run started.
- A smoke test of one cell per model ran before each grid. Round two kept its smoke cells in the data: rep 1 of T5 (incident) in the one-line arm, which the grid run then skipped as done.
- Every script resumes and skips finished work. A failed call leaves no file, so a rerun fills the gap. In round two, one quiz reply failed to parse on the first pass, and the second pass filled it.
- Judging and quizzes started on finished groups while generation still ran. By file times, the replies took about 11 minutes in round one and 8 in round two, and most scoring ended within 3 minutes of the last reply. Round two's last 26 judge calls and 14 quizzes ran in a later pass.

Recorded Claude-side cost, from the CLI's `total_cost_usd`:

| | Round one | Round two |
|---|---|---|
| Opus replies | $9.47 (64 replies) | $5.67 (48 replies) |
| Opus judge calls | $3.38 (32 calls) | $3.61 (48 calls) |

That is $22.11 in all. Unknown: the Codex replies and sol judge calls (the Codex CLI reports tokens only), the Haiku and Sonnet quiz calls (`reader.py` does not save their usage), and the smoke runs.

## 13. Threats to validity

- The judges are models, and they agree only moderately. The only human rating is my own blind read of five round-two pairs (N=1): bare preferred twice, the one line once, two ties.
- Each judge favors its own family. The Claude result changes sign with the judge, so it stays unclaimed.
- The judges carried my plain-language rule, which may tilt them toward plain replies.
- Each judge saw each group in one random order. That spreads position bias across the arms but does not cancel it.
- Every reply is a single turn with no tools, while real agent sessions are mostly tool work.
- Only xhigh effort and two models were tested.
- I wrote the tasks and checklists, so they encode my view of a good answer.
- The quiz reader is a language model, a weak stand-in for a person reading in a second language.
- Round one reproduces only with the files in `baseline/`, and the rest of my user-level state (settings, hooks, Codex config and memories) is not published. Round two is bare, so anyone with both CLIs signed in can rerun it.
- The metrics and the intervals have the weaknesses listed in sections 10 and 11.

## 14. Next

Round three tests the one line where I would use it: as an on-demand rewrite of a finished document. It will rewrite finished handoffs and runbooks with the one line and measure which facts survive. The checklist method carries over: list the facts in each source document in advance, and have a judge mark each one as present, absent or changed in the rewrite (the fact-recall idea in section 6.3 of the research notes). Hedges get their own check, because a rewrite can turn "not sure" into a flat claim.

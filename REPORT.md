# STE (Simplified Technical English) adoption test: report

Date: 2026-10-12. Round one: 8 tasks x 4 arms x 2 models x 2 reps = 128 replies, 64 blind judge calls, 128 reader quizzes. Round two (bare CLIs vs one line): 8 tasks x 2 arms x 2 models x 3 reps = 96 replies, 96 judge calls, 96 reader quizzes.

## Verdict

**Do not adopt STE as an always-on rule.** Keep the current one-line plain-language rule. Use STE only as an on-demand rewrite for text meant for second-language readers or translation.

Why:
- **No net quality gain.** Every STE arm scored a little below baseline overall (-0.14 to -0.25 on a 1-10 scale) and beat baseline in only 38 to 41% of blind rankings.
- **It hurts Codex clearly.** gpt-6.1-sol lost 0.5 to 0.7 points with STE, and both judges scored it lower (the Opus judge by 0.75 to 0.94, the sol judge by 0.31 to 0.56). For Opus the judges split (the Opus judge says slightly worse, the sol judge says better), so the Opus gain is not reliable.
- **It costs a lot.** STE rules raise thinking tokens by 50 to 83%, reply time by 36 to 46%, and Opus cost per reply by 49 to 82%. The visible reply barely gets shorter.
- **The one real win is second-language ease** (+0.4 to +0.6 on a 1-5 scale, both judges agree). It comes with a real loss in naturalness (-0.3 to -0.5) and, for Lite and Full, in nuance.
- **The current one-line rule already does most of the work.** Baseline replies average about 10 words per sentence, with only 1.5% of sentences over 25 words. STE mainly removes passive voice (6% down to 1-2%) and perfect/progressive tenses.

## Arms (what was compared)

| Arm | What it is | Size |
|---|---|---|
| base | My real setup: global CLAUDE.md, Codex AGENTS.md and the kay output style (snapshots in `baseline/`) | 0 extra |
| lite | Compact STE rules, always on, as a folder CLAUDE.md / AGENTS.md (`arms/ste-lite.md`) | 187 words |
| scoped | Strict STE for procedures, warnings, handoffs, docs; relaxed for discussion (`arms/ste-scoped.md`) | 245 words |
| full | Most faithful skills.sh rewrite skill (danyuchn/asd-ste100, MIT) forced on (`arms/ste-full.md`) | 2,639 words |

Models: Claude Code Opus 5.5 at xhigh effort; Codex gpt-6.1-sol at xhigh effort. Single turn, no tools, no web, clean folders.
Tasks: T1 (procedure), T2 (explanation), T3 (tradeoff), T4 (handoff from messy notes), T5 (incident from logs), T6 (risky-action warning), T7 (code review), T8 (pushback discussion).

## Tradeoff table (change vs baseline; * = 95% interval excludes zero)

| Measure | lite | scoped | full |
|---|---|---|---|
| Overall judge score (1-10), both models | -0.25 | -0.14 | -0.25 |
| Overall, Opus replies | +0.22 | +0.25 | +0.19 |
| Overall, Codex sol replies | -0.72* | -0.53* | -0.69* |
| Win rate vs baseline | 41% | 41% | 38% |
| Checklist facts covered | -2 pts | -1 pt | -3 pts* |
| Invented facts (judge count, base = 13) | 7 | 17 | 5 |
| Nuance (1-5) | -0.34* | -0.11 | -0.28* |
| Second-language ease (1-5) | +0.58* | +0.41* | +0.59* |
| Clarity (1-5) | +0.11 | +0.02 | +0.16* |
| Naturalness (1-5) | -0.47* | -0.45* | -0.28* |
| Reader quiz (Haiku answers from the reply) | +7 pts | +6 pts | +2 pts |
| Prose words | -7% | -4% | -18%* |
| Sentences over 20 words (base 5.9%) | 0.5% | 1.8% | 0.9% |
| Passive voice (base 6.1%) | 1.0% | 1.6% | 1.5% |
| Thinking tokens, Opus | +62% | +66% | +51% |
| Thinking tokens, Codex | +83% | +65% | +77% |
| Reply time (base 48 s) | +46% | +43% | +36% |
| Opus cost per reply (base $0.10) | +49% | +55% | +82% |
| Context added to every turn and subagent | ~400 tokens | ~530 tokens | ~5,500 tokens |

Formatting side effects: STE arms use about 45% more bullets and about 37% less bold.

## Decision matrix

Scores are 1 (bad) to 5 (good), based on the measured data. Weights reflect what matters for daily agent use.

| Option | Quality 25% | Facts and nuance 20% | 2nd-language ease 15% | Naturalness 10% | Cost and speed 15% | Simplicity, both tools 15% | **Weighted** |
|---|---|---|---|---|---|---|---|
| A. Keep current plain-language rule | 4 | 5 | 3 | 5 | 5 | 5 | **4.45** |
| E. A + on-demand STE rewrite skill | 4 | 5 | 4 | 5 | 5 | 4 | **4.45** |
| C. STE-Scoped always on (both tools) | 3.5 | 4 | 4 | 2 | 2 | 4 | 3.38 |
| F. STE-Scoped for Claude only | 3.5 | 4 | 4 | 2 | 2.5 | 3 | 3.30 |
| B. STE-Lite always on (both tools) | 3 | 3 | 5 | 2 | 2 | 4 | 3.20 |
| G. One line always on: "Speak only in ASD-STE100" | 2.5 | 2.5 | 5 | 1 | 1 | 5 | 2.88 |
| D. STE-Full always on (skill text forced) | 3 | 2.5 | 5 | 3 | 1 | 2 | 2.75 |

**Recommendation: E.** It costs nothing day to day and keeps a tool for docs that second-language readers or translators will use. Before you rely on it, check one rewrite for dropped facts, because the Full arm lost 3 points of checklist coverage.

## Round two: bare CLIs vs one line

Setup: no global CLAUDE.md or AGENTS.md, no output style, no hooks, no Codex memories. Claude ran with `--setting-sources project,local` (`--bare` needs an API key). Codex ran with `CODEX_HOME` set to a temp folder that only links `auth.json`. The one-line arm had `Speak only in ASD-STE100` as the run folder's CLAUDE.md or AGENTS.md. Zero tool calls, zero send-offs in 96 replies.

Verdict: **the models know STE from the name alone, and the one line pushes harder than any rule file.** It is a poor always-on rule and a good on-demand rewrite instruction.

| Measure (one line minus bare; * = 95% interval excludes zero) | Claude Opus | Codex sol | Both |
|---|---|---|---|
| Overall (1-10) | -0.27 | -0.85* | -0.56* |
| Judge picked the one line | 38% | 10% | 24% |
| Checklist facts | +2 pts* | -7 pts* | -2 pts* |
| Second-language ease (1-5) | +1.08* | +0.92* | +1.00* |
| Naturalness (1-5) | -1.56* | -0.75* | -1.16* |
| Nuance (1-5) | -0.62* | -0.92* | -0.77* |
| Sentences over 20 words | 8.1% to 0.1% | 9.3% to 0.7% | |
| Passive voice | 8.2% to 2.6% | 6.9% to 3.3% | |
| Thinking tokens per reply | 1,677 to 5,245 (x3.1) | 913 to 1,709 (+87%) | |
| Seconds per reply | 34 to 67 (x2) | 53 to 79 (+48%) | |

- Same judge pattern as round one: both judges say Codex gets worse; for Claude the Opus judge says worse (-0.71*) and the sol judge says no change (+0.17).
- Compliance is in the same range as the round-one rule files. For Claude it beats Lite on long sentences; for both models it is looser than Lite on passive voice.
- Side finding (crosses rounds, so a hint only): Kay's own global rules and output style add about 1,200 thinking tokens and 10 seconds per Claude reply versus bare Claude. Codex is unaffected.
- Effect on the decision: option E stays the pick, and its on-demand rewrite can be one line naming the standard, with no rule text to paraphrase. Not yet tested: the one line in rewrite mode on a finished document, where dropped facts are the risk.
- Files: `exp2/` (arms, models, one-line rule, runs, scores). Analysis: `harness/analyze2.py`, output in `exp2/scores/summary.md`.

## How to adopt, by mechanism

| Mechanism | Verdict | Reason |
|---|---|---|
| ~/.claude/CLAUDE.md + ~/.codex/AGENTS.md | Right place for any always-on writing rule | The only surface that is always on, reaches subagents, covers files and commit messages, and works in both tools. The test shows STE does not earn this place. |
| Output style (kay.md) | No | Main thread only. Subagents and Codex do not get it. |
| Skill (on demand) | Yes, for option E | Loads only when named or matched, so it costs nothing when unused. It cannot cover every reply. |
| skills.sh as is | No | None of 23 candidates fits as is. danyuchn/asd-ste100 (MIT, faithful) is the best base for an on-demand skill. Avoid 0xpili and iammrduncan, which ship the copyrighted dictionary. |
| Stop hook linter | Optional | Log-only checking is cheap if you want to watch sentence length or passive voice without changing behavior. |

Legal constraints: the ASD standard text and dictionary are copyrighted, and "ASD-STE100" is an EU trademark. Use our own paraphrased rules. Do not copy rule text or dictionary entries into any file, and do not publish a skill under the ASD-STE100 name.

## Limits of this test

- The judges are models. Their agreement is moderate (r = 0.45), and each judge rates its own family higher. Both judges score Codex lower with STE. The Opus result changes sign with the judge.
- Rep-to-rep noise is 0.76 points, so per-task cells (n = 8) are too thin for task-level claims. Hints only: STE helped code review (T7) and incident (T5), and hurt the pushback discussion (T8) and the risky-action warning (T6).
- The test used single turns without tools. In real tool-heavy sessions, the thinking overhead per writing turn is likely similar, but it is a smaller share of total session time.
- The baseline already had a plain-language rule. This measures STE on top of a strong baseline, not STE against unguided output.
- The reader quiz (Haiku) moved little. LLM readers handle long sentences well, so it is a weak proxy for human second-language readers.

## Suggested follow-up (optional, about 20 minutes)

The base's only clear STE gap is passive voice, and the only clear STE win is second-language ease. A micro test can check if two lines in the existing Writing section ("Use active voice." and "Use one term for one thing.") capture that win without the thinking cost. This needs 32 new runs; the baseline is reused.

## Files

- Research: `research/01-standard-and-evidence.md`, `research/02-skills-sh-candidates.md`, `research/candidate-sources.md`
- Dataset: `dataset/tasks.json`; arms: `arms/`
- Replies: `runs/<model>/<arm>/<task>/r<rep>/output.md`
- Scores: `scores/summary.md`, `scores/deep_dive.md`, `scores/per_model.md`, `scores/long.csv`, `scores/invented_errors.csv`
- Harness: `harness/` (run.py, metrics.py, judge.py, reader.py, analyze.py, deep_dive.py)
- The fetched skill copies are not published. `research/candidate-sources.md` lists each one with its repo and commit.

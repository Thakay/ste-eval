# STE skills on skills.sh: candidates and assessment

Date: 2026-10-12. Scope: existing agent skills that apply ASD-STE100 Simplified Technical English (STE) or plain-language rules, as options for a writing rule in Claude Code and OpenAI Codex. Nothing was installed. Each skill was fetched at a pinned commit into a local `candidates/<owner>__<repo>__<skill>/` folder and read as untrusted data. No script from those folders was run. The copies are not published; `candidate-sources.md` maps each folder name to its repo and commit.

## Verdict

No candidate is good enough to adopt as is. Two are good bases to borrow from. The best plan is to write our own compact rule set (about 150 to 250 words) for `~/.claude/CLAUDE.md` and the Codex `AGENTS.md`, and keep an on-demand skill only for rewrite and check jobs on docs.

Reasons:

1. A skill loads only when the model decides that a task matches its description. A normal chat reply or status report seldom triggers a skill load. The authors who wanted the rules on every reply had to add hooks or output styles (SimpleEnglish, woosal1337). For an always-on writing rule, the instruction file is the reliable place.
2. The full skills cost 1,000 to 9,000 tokens each when loaded. The evidence from their own authors says that a short rule set gives most of the gain (see "Evidence from the authors' own tests").
3. Each candidate has at least one problem for our use: a scope limited to manuals, a hedge-killing modal rule, factual errors in the word table, copied dictionary content, no license, or heavy hooks.

Best base: AminBlg/SimpleEnglish (`candidates/aminblg__simpleenglish__simple-english/`). It is the only popular candidate with separate rules for the document and the chat reply, a Codex plugin, a 609-word paste-in version (`prompts/system-prompt.md`), MIT license, and honest evals. Most faithful rewrite tool: danyuchn/asd-ste100-skill (`candidates/danyuchn__asd-ste100-skill__asd-ste100/`), also MIT.

## Yardstick: what real STE asks for

These are the core ASD-STE100 rules that the candidates agree on and that the public sources support. Rule numbers below are as the candidates cite them for Issue 9. I did not check them against the standard itself.

| Area | Real STE rule |
|---|---|
| Sentence length | 20 words at most in a procedure sentence, 25 in a descriptive sentence |
| Instructions | One instruction per sentence (two only if the actions happen at the same time). Imperative mood. Condition first, then a comma, then the command |
| Voice | Active voice in procedures. Passive is allowed in descriptions only when the actor is unknown or not relevant |
| Tenses | Infinitive, imperative, simple present, simple past, simple future, past participle as adjective. No present perfect or other compound forms. No "-ing" form as a verb |
| Noun clusters | Three words at most. Break longer ones with a preposition or a hyphen |
| Paragraphs | One topic, six sentences at most (descriptive text) |
| Missing words | Keep articles and other words. Do not write in telegraph style. No contractions |
| Punctuation | No semicolons (Rule 8.1, no semicolons). The em dash is not banned by STE |
| Words | About 875 to 900 approved words, each with one meaning and one part of speech, plus project technical nouns and technical verbs (for software: install, click, upload and similar). Examples: "check" is approved only as a noun, "make sure" is the approved verb. "can", "must" and "will" are the approved modals. In the Issue 7 list, "could" is approved as the past form of "can" |
| Safety text | Warning (injury) and caution (damage) start with the command or condition, then give the risk |

The dictionary is copyrighted by ASD. The standard is a free download, but redistribution needs written permission. A skill that ships the word list is a legal risk for anyone who republishes it.

## Ranked table (top 8)

Fidelity is my judgment on a 1 to 5 scale, against the yardstick above. Size counts words in SKILL.md, then words in reference files that load on demand. Tokens are roughly words times 1.3. Installs and audits come from skills.sh on 2026-10-12. All eight passed all three skills.sh audits (Gen Agent Trust Hub, Socket, Snyk). skills.sh shows no reason text, so the scope of each audit is not known. Do not read a Pass as a review of the plugin hooks.

| Rank | Skill (install id) | Installs, stars | License | Last skill commit | Size (SKILL.md + refs) | Trigger | Job | Fidelity | Copies dictionary | Risk |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `AminBlg/SimpleEnglish@simple-english` | 12.3K, 3.9K | MIT | 2026-09-30 | 1,224 + 3,717 | Wide: docs, replies, many phrases. Plugin hook makes it always on | Write, rewrite, check | 3.5 | No (small set of rulings) | Plugin adds SessionStart, PostToolUse, Stop hooks (node, python). `npx skills add` installs the skill only |
| 2 | `danyuchn/asd-ste100-skill@asd-ste100` | 5.2K, 4.7K | MIT | 2026-09-10 | 2,655 + 708 | On request, or for text that agents parse | Rewrite (check on request) | 4 | No | Stdlib linter, no network |
| 3 | `posthog/ai-plugin@writing-simplified-technical-english` | 77, 88 | None in repo (adapted from danyuchn, MIT) | 2026-09-03 | 799 + 1,058 | Any agent prose someone acts on | Write as you go, rewrite | 4 | No | None found |
| 4 | `woosal1337/blog@asd-ste100` | 206, 540 | MIT | 2026-10-09 | 2,842 + 672 | Standing rule for all prose, chat included | Write, rewrite, review | 4.5 | Small excerpt (39 recurring errors list) | Heavy: 4 hooks, installer edits `~/.claude/settings.json`, skill tells agent to run a linter before replies |
| 5 | `theangrybyrd/simplified-technical-english-skill@simplified-technical-english` | 80, 33 | MIT | 2026-07-31 | 891 + 1,800 | Docs, code comments, software text. Excludes casual chat | Write, review | 4.5 | No | Optional `uv run` script that searches a PDF you supply |
| 6 | `samber/cc-skills@humanizer-en-asd-ste100` | 1.2K, 230 | MIT | 2026-09-02 | 6,818 + 0 | On request (STE, de-slop a manual) | Write, rewrite | 5 | No (starter lexicon only) | Asks for WebFetch and Agent tools. Fetches the 434-page official PDF when unsure |
| 7 | `dobroslavradosavljevic/skills@plain-language` | 51, 3 | MIT | 2026-08-17 | 932 + 1,595 | "Always, every turn" (chat and naming) | Write as you go | 3 | No | None found |
| 8 | `nuelcyoung/asd-ste100@asd-ste100` | 39, 29 | MIT | 2026-08-22 | 3,007 + 10,349 | On request (manuals) | Write, rewrite, check | 5 | No (known rulings only) | None found |

## Notes on each ranked candidate

### 1. AminBlg/SimpleEnglish, simple-english

- Path: `candidates/aminblg__simpleenglish__simple-english/` (skill in `skills/simple-english/`, paste-in rules in `prompts/system-prompt.md`).
- The only popular candidate with two registers: rules for documents (12 rules, STE limits) and rules for chat replies (answer first, no openers or closers, no em dashes, define terms, no contractions). It also has a 60-token version for tight prompts.
- Fidelity gaps: it bans should, would, may, might and could. STE approves "could" as the past of "can", and a blanket ban pushes the agent to delete hedges, which changes the claim. The reply rule "prose only, no lists, no headers, no tables" is the author's taste, not STE. "Make sure that" for every check, verify and confirm is correct STE.
- Codex support: a Codex plugin with a SessionStart hook. Claude Code plugin adds a PostToolUse lint on Markdown files and a Stop check on the last reply. Hooks have no network calls.
- Good practice: the author publishes negative results (see the evidence section) and recomputes published numbers in CI.

### 2. danyuchn/asd-ste100-skill, asd-ste100

- Path: `candidates/danyuchn__asd-ste100-skill__asd-ste100/`.
- Most careful about what it can and cannot claim. It splits the rules into structural rules (sentence shape, can be applied without the dictionary) and lexical rules (need the dictionary, so only a direction). It keeps hedges such as "may have failed" and keeps present perfect when it carries meaning, and it says so.
- Aimed at text that machines read: tool descriptions, error messages, prompts, status reports. Not meant to run on every chat reply.
- Default output is the rewritten text only, with a rule table on request. Good for a rewrite skill.
- Ships `scripts/ste-lint.py` (standard library only, no network). It checks semicolons, sentence length, phrasal verbs, nominalization, marketing words, synonym rotation, passive voice and compound tenses.
- 2,655 words is heavy for an always-on rule. Small slip: one example uses "inspect", which is not an approved STE verb.
- A second entry from the same repo, "Simplified Technical English (ASD-STE100)" (200 installs), is an older name of this skill.

### 3. PostHog/ai-plugin, writing-simplified-technical-english

- Path: `candidates/posthog__ai-plugin__writing-simplified-technical-english/`.
- A short rewrite of danyuchn: one rule table, a rewrite procedure and a five-question self-check. Its description targets the right text: reports, PR descriptions, commit messages, prompts, status summaries.
- Adds "one hedge at most" and a PostHog house style (American English, sentence case, Oxford comma, no em dash).
- The PostHog repo has no license file. The text credits danyuchn under MIT, so borrow from danyuchn, not from this copy.

### 4. woosal1337/blog, asd-ste100

- Path: `candidates/woosal1337__blog__asd-ste100/`.
- The most faithful of the agent-focused skills. It cites Issue 9 rule numbers, has a strict word set (but, because, can, must, use), and covers chat replies. It adds "Layer 2", a reply shape (next action first, numbered steps, no preamble or closer, five-item cap on action lists). Layer 2 is not STE.
- It reproduces the standard's list of 39 recurring writer errors in `references/ste-recurring-errors.md`. The author calls it a small factual excerpt. It is still copied content from the standard.
- Heavy footprint. The plugin hooks run on every prompt (UserPromptSubmit), after every tool call (PostToolUse matcher `*`), before Bash and an author-specific MCP server (PreToolUse), and on Stop, where a gate can block a reply. `install.py` edits `~/.claude/settings.json` and sets an output style. SKILL.md tells the agent to write each reply over 60 words to a scratch file and run node and python on it before it sends. No network calls.
- Two other listed skills, `8asd8f8f1/ste-writing-skill` and `jokot/skills@ste-writing`, are copies of an earlier version of this skill.

### 5. TheAngryByrd, simplified-technical-english

- Path: `candidates/theangrybyrd__simplified-technical-english-skill__simplified-technical-english/`.
- Clean, compact and accurate. Its modal rules match STE (must, can, no "may"). It has good rules for code comments (say why, do not restate the code) and error messages (name the failed operation, give a fix).
- Its description excludes casual conversation, so it will not cover chat replies.
- Ships a script that searches a copy of the standard that you download yourself. No copied dictionary.

### 6. samber/cc-skills, humanizer-en-asd-ste100

- Path: `candidates/samber__cc-skills__humanizer-en-asd-ste100/`.
- The most complete rule-by-rule summary of Issue 9 (all 9 sections, technical noun and verb categories, vertical list rules). Also strips AI artifacts (chat leftovers, padding).
- 6,818 words (about 9,000 tokens) in one file. Aimed at maintenance manuals, medical device text and API docs. It asks questions before drafting and suggests "ultrathink". Too heavy and too formal for daily agent output.

### 7. DobroslavRadosavljevic/skills, plain-language

- Path: `candidates/dobroslavradosavljevic__skills__plain-language/`.
- The closest in intent to Kay's goal: always on, for every reply, status update and summary, plus rules for readable names in code.
- Weak on fidelity. It says "use approved words only" but has no dictionary, so the rule cannot be met or checked. Very low adoption (3 stars). Its "always, every turn" description does not make a skill load on every turn.

### 8. nuelcyoung/asd-ste100, asd-ste100

- Path: `candidates/nuelcyoung__asd-ste100__asd-ste100/`.
- Aerospace-grade: part-of-speech checks, participle rules, and a strong "meaning outranks vocabulary" rule against wrong word swaps and lost hedges. It explains how to check words against your own copy of the standard.
- Over 13,000 words with references, and it tells the agent to load `meaning-fidelity.md` for every rewrite. Says "could" is not approved, which conflicts with the Issue 7 list.

## Other candidates seen (not ranked)

| Skill | Installs | Why not ranked |
|---|---|---|
| `0xpili/simplified-technical-english` | 71 (974 stars) | Ships the full approved-word list of Issue 7 (869 entries with parts of speech and forms) in `references/word-list.md`. Copyright risk, and an old issue |
| `iammrduncan/skills@simplified-technical-english` | 11 | Ships the whole controlled vocabulary and rule statements close to the published text in 1.8 MB of JSON (not saved locally, inspected only). Snyk: Warn |
| `blagoysimandov/asd-ste100-writer-skill@ste100-writer` | 279 | Word table has STE errors: "need" for "require" (need is not approved), "about" for "approximately" (approximately is approved), and it lists approved verbs "examine" and "illuminate" as words to avoid. No repo license. Snyk: Warn |
| `jsath/simplified-technical-english@technical-english` | 25 | States that "check" is a verb, not a noun, which is the reverse of STE |
| `Ikaleio/skills@ste-writing` | 12 | 3,101 words, multilingual (Chinese adaptation), auto-trigger on technical prose. No license |
| `jpcaparas/skills@simplified-technical-english` | 24 | Procedures and safety text. No license |
| `gohypergiant/agent-skills@accelint-english-manager` | 61 | General prose editor with an STE strict mode. 3,055 + 6,195 words |
| `alexander-danilenko/cortex-ai-skills@simple-english` | 42 | STE-based, 2,331 + 2,276 words |
| `saschb2b/skills@no-slop` | 76 | STE plus Microsoft style guide. 2,045 + 17,970 words |
| `b1rdmania/claude-plain-english-skill@plain-english` | 96 | Orwell and Gowers rules for long-form prose, not STE |
| `obra/the-elements-of-style@writing-clearly-and-concisely` | 2K | Strunk (1918). Not STE. The full book is about 12,000 tokens |
| `vercel-labs/agent-skills@writing-guidelines` | 91.3K | Vercel house style review. Fetches its rules from a remote URL on every run, so the repo owner can change the prompt at any time |
| `yzhao062/agent-style@agent-style` | 40 (710 stars) | Not STE (Strunk, Orwell, Pinker, 21 rules). CC BY 4.0 needs attribution. Allows semicolons. A good model of a compact always-on block (`agents/AGENTS.md`, 619 words) |

The PostHog skill also appears as `posthog/posthog@writing-simplified-technical-english` (6 installs).

## What is missing for everyday agent output

- **No compact always-on block.** Every candidate is a skill of 800 to 7,000 words. The closest small versions are SimpleEnglish `prompts/system-prompt.md` (609 words, plus a 60-token version) and the woosal1337 `output-style.md` (348 words). Neither is STE-faithful on modals and hedges.
- **Chat replies are mostly out of scope.** Only SimpleEnglish, woosal1337, PostHog and Dobroslav aim at chat and status text. The others target manuals, procedures and safety text.
- **Skills do not fire on every reply.** In both Claude Code and Codex, a skill body loads only when the model matches the task to the description. A "use always" description does not change that. Always-on behavior needs the instruction file, a hook, or an output style.
- **Software terms are under-served.** Real STE treats run, deploy, merge and commit as technical verbs that a project must declare. Only samber, TheAngryByrd and nuelcyoung explain this. No skill gives a ready glossary for coding work.
- **Status-report modality.** Agents often must say "the test may have failed" or "the job has completed". Only danyuchn, woosal1337 and nuelcyoung protect hedges and qualifiers. SimpleEnglish and PostHog push toward fewer hedges.
- **No reader testing.** Every published benchmark measures linter hits, not reader understanding.
- **Kay's existing rules are partly covered.** SimpleEnglish, PostHog and blagoysimandov include a "no em dash" rule. None covers "IDs carry their meaning" directly, though SimpleEnglish and Dobroslav ask the agent to define terms at first use.

## Evidence from the authors' own tests

- SimpleEnglish, interim audit dated 2026-09-02 (`evals/results/WHY-USELESS-2026-09-02.md`): on 8 chat-reply scenarios with claude-sonnet-4-6, an 8-line micro prompt beat the full skill on words, sentences, em dashes, bold, headers and bullets. The skill won only on its own linter. The author then rebuilt the skill around the document and reply registers (version 2.0.1) and later dropped a five-sentence reply cap that the model did not obey (2.1.0).
- SimpleEnglish benchmark (version 2.0.1, 9 Claude models, 144 generations): about 81% fewer linter-counted STE violations per 100 words. A Claude judge preferred the skill text in 62 of 72 pairs. Same-family judge, one run per cell.
- 8asd8f8f1 experiment (6 tasks, heuristic linter): STE cut violations per 100 words by 74% on Claude Sonnet and 50% on gpt-5.5. On gpt-5.5, Orwell's six rules did as well (1.69 against 1.76). A banned-word list did almost nothing on Claude but cut 40% on GPT.
- agent-style (non-STE, 21 rules) reported a mechanical violation drop from 105 to 58 on Claude Opus. Directional only.

The shared lesson: a short, clear rule system gives most of the gain. Long rule sets dilute the few rules that matter, and their benchmarks mostly measure obedience to their own linter.

## Recommendation

1. Write our own compact rule set and put it in `~/.claude/CLAUDE.md` and the Codex `AGENTS.md`. Keep it at about 150 to 250 words.
2. Take the content from the two MIT bases, with a credit line:
   - From danyuchn: the structural rules (20 and 25 word limits, one instruction per sentence, active voice, simple tenses, noun clusters of three words or fewer, no semicolons, keep articles), the rule to keep hedges and qualifiers, and the honesty that we do not check the dictionary.
   - From SimpleEnglish: the split between documents and chat replies, condition before command, "make sure" for the check, verify and confirm family, define a term at first use, no openers or closers.
3. Add what no candidate has: a short software glossary of declared technical verbs (run, merge, commit, deploy), Kay's "IDs carry their meaning" rule, and a rule that code, paths, commands and quoted errors stay exact.
4. Optional: keep one on-demand skill for rewriting or checking a doc. danyuchn is the best fit (MIT, rewrite-only output, linter without network). Read its linter before any use, because the folder content is untrusted.
5. Do not install the woosal1337 hooks or SimpleEnglish plugin hooks for this purpose. Do not use or republish 0xpili or iammrduncan, because they ship ASD dictionary content.

## Files

- Sources: `candidate-sources.md` (23 skills, each with repo and commit). The fetched copies stay local.
- Two of the skills ship ASD dictionary or standard content: `0xpili__simplified-technical-english__simplified-technical-english/references/word-list.md` and `woosal1337__blog__asd-ste100/references/ste-recurring-errors.md`. Do not republish them.

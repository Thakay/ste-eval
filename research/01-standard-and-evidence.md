# 01. ASD-STE100: the standard, the evidence, and how to measure it

Date: 2026-10-12. Scope: facts for an A/B test and a decision on whether Claude Code and OpenAI Codex should write in ASD-STE100 Simplified Technical English (STE). Outputs in scope: chat replies, reports, handoff docs, specs, commit messages, code comments.

Method: the rules and the copyright terms come from the primary source, the Issue 9 PDF served by the official STEMG (STE Maintenance Group) website. I read it locally in a scratch folder. It is not copied into this project, and this brief paraphrases it. Other facts come from the STEMG site, ASD, peer-reviewed papers, and public repos. Where I could only see an abstract or a secondary summary, the text says so.

## Key points

1. **Current issue:** Issue 9, dated 2025-01-15. It changed STE from a "specification" to a "standard". It adds no new rules: 31 of the 53 rules got new wording, and 555 dictionary entries changed. Issue 10 is planned for January 2028.
2. **License:** free to download, but ASD owns the copyright and the EU trademark. The notice forbids any reproduction or publication of any part of the standard without written permission from an ASD officer. Free reuse rights go only to 8 listed groups, such as aerospace industry members, airworthiness authorities, and universities for teaching. Kay's use does not appear to fit any of them. Do not paste the rule text or the dictionary into a prompt or a public skill. A paraphrase of the rule ideas in your own words is the safe route. The two most popular public STE skills take that route.
3. **Core numbers:** procedure sentences have 20 words at most (warnings and cautions too). Descriptive sentences and notes have 25 words at most. A paragraph has 6 sentences at most and one topic. A multi-word noun has 3 words at most. Semicolons are not allowed. The dictionary has about 900 approved words, and each word has one meaning and one part of speech.
4. **Model without the dictionary:** a model can follow 35 of the 53 rules from the rule alone (sentence length, voice, tenses, "-ing" forms, noun clusters, procedure form, paragraphs, punctuation, word count, phrasal verbs). 8 rules need the ASD dictionary (approved words, meanings, part of speech, verb forms). 9 rules need a project term list (technical nouns and technical verbs). Rule 3.7 (use a verb, not a noun, for an action) partly needs the dictionary.
5. **Human evidence:** real but small and old. Aviation studies from 1995 to 2002 found better comprehension and fewer task errors. The gains were largest for complex documents and for non-native readers, and reading time did not change. One study found that a mixed version of the instructions made errors worse. Eye tracking found only a marginal gain. For neural machine translation, controlled-language rules gave no gain and a small loss.
6. **LLM evidence:** I found no peer-reviewed study of LLMs writing ASD-STE100. The best data is a community benchmark (AminBlg/SimpleEnglish). A full STE skill cut regex-linter violations by 75% to 88% on 9 Claude models and by 96% on gpt-4.1-mini. But its own audit found that an 8-line prompt beat the full skill prompt on everything a reader sees. Research on instruction following shows that compliance drops as the number of rules grows.
7. **Main risks:** STE was built for procedures and product descriptions, not for discussion. The STEMG says so itself. Simplification research shows frequent silent information loss. Brevity instructions can raise hallucination in some models. STE removes "may" and "should" (the dictionary gives "can" and "must"), so hedges can harden into claims.

## 1. The current issue, recent changes, access, and license

### 1.1 Current issue

- ASD-STE100 Simplified Technical English, Issue 9, dated 2025-01-15, subtitle "Standard for technical documentation". It fully replaces all older issues.
- It is 434 pages long (ASD news release). It has two parts: Part 1 has the writing rules (53 rules in 9 sections plus 8 general recommendations), and Part 2 has the dictionary.
- Dictionary size: the STEMG site says about 900 approved words and about 1,200 words that are not approved. A 2025 paper by two STEMG members counts 875 approved entries and about 1,400 entries that are not approved (Zambrini and Chiarello 2025).
- Owner: ASD (Aerospace, Security and Defence Industries Association of Europe, Brussels). It holds the copyright and EU trademark No. 017966390. The STEMG maintains the standard.
- Cadence: one issue about every 3 years. Issue 7 came out in 2017, Issue 8 on 2021-04-30, and Issue 9 on 2025-01-15. The STEMG FAQ says Issue 10 is scheduled for January 2028.
- Where it is required (per the STEMG site): ATA iSpec 2200 (the airline industry spec for maintenance manuals) has required it since the 1980s. S1000D (an international spec for technical publications) recommends it. Aviation authorities (EASA, FAA, CAAC) require it in some continued-airworthiness directives. ISO 24620-4:2023 (language resource management) also references it.
- Status of AI tools: in June 2026, the STEMG published a white paper on STE and AI. It extends ASD's non-endorsement policy to AI tools. It warns that AI text can look STE-compliant without being compliant, and that a plausible look is not proof. It says AI compliance checks have uneven accuracy today, and it plans benchmarks for AI performance in STE writing.

### 1.2 What changed in recent issues

Issue 9 (2025), from its own change table and the STEMG papers:

- Status changed from specification to standard. New subtitle.
- No new rules. 31 of 53 rules have new wording, and more help notes were added.
- "Technical name" is now "technical noun" everywhere. Terms were aligned with ISO 1087:2019 (terminology vocabulary).
- Section 2 was renamed from "Noun clusters" to "Multi-word nouns". Old Rule 2.3 (use articles) moved and is now Rule 4.5 (use an article or "this/these" before a noun).
- Rule 1.5 (technical noun categories) gained two categories: 21, law and regulations, and 22, animals, plants, and other life forms. Rule 1.12 (technical verb categories) was rebuilt with subject-field subcategories.
- Rule 8.6 (things that count as one word) was widened. A number together with its unit now counts as one word, and so do proper nouns of people, groups, organizations, and places.
- Two new general recommendations: GR-7 (inclusive language) and GR-8 (possessive form).
- 555 dictionary entries were updated. The dictionary now lists approved verbs and defines verb types. Legacy aerospace and defense examples dropped from 15% of the dictionary examples in Issue 1 (1986) to 3% in Issue 9.
- Issue 8 (2021) focused mainly on the dictionary (Part 2).

### 1.3 How to get it

- The official route is the request form on the STEMG Downloads page. The copy is free, and PDF is the only format. The same official site also serves the Issue 9 PDF directly at `https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf`.
- The standard has been free since Issue 6 (2013). Wikipedia reports 18,981 official copies of Issues 6 to 8 sent out, and about 1,000 copies of Issue 9 by March 2025.

### 1.4 Copyright, trademark, and what Kay may do

What the Issue 9 front matter says, paraphrased:

- ASD owns the information. Getting or holding a copy gives no license. Nobody may reproduce or publish all or any part of it "without the written authority of an officer of ASD".
- "Special usage rights": free and irrevocable rights to use, reproduce, or publish the standard go to 8 groups only. These are (1) ASD national member associations and their member companies, (2) members of AIA (US) and AIAC (Canada), (3) other ICCAIA members, (4) customers of groups 1 to 3, (5) ministries of defense of ASD, AIA, and AIAC countries, (6) Airlines for America (A4A), (7) airworthiness authorities, and (8) universities and research institutes, for teaching only.
- "Distribution": anyone can get it free from the STEMG, ASD, or ASD-STAN websites. Distribution by other channels, direct or through other websites, needs written permission from the STEMG.
- The STEMG tools page adds a rule for tool makers: tool providers may not use the ASD logo, copyright, or trademark, and may not claim ASD approval.

Practical reading for our case. This is not legal advice.

| What Kay might do | Allowed? | Basis |
|---|---|---|
| Download and read the PDF for own work | Yes | Free download, official route |
| Put the PDF in a repo or share it | No, unless the STEMG gives written permission | Distribution clause |
| Paste rule text or dictionary entries into `CLAUDE.md`, `AGENTS.md`, or a prompt | Not permitted by the notice, even in private. It also sends the text to a model vendor. Avoid it | Reproduction of any part needs written authority |
| Publish a skill that holds the rule text or the word list | No | Same, plus a possible EU database right on the dictionary (ASD is in Belgium) |
| Write the rule ideas and numeric limits in our own words, and cite rule numbers | Generally fine. Copyright protects the wording, not the ideas or numbers. This is what the MIT-licensed skills do (danyuchn/asd-ste100-skill, AminBlg/SimpleEnglish) | General copyright principle; existing practice |
| Name a public skill "ASD-STE100" or claim "STE compliant" | Avoid. Say "STE-inspired" and add "not affiliated with or endorsed by ASD" | EU trademark; STEMG tools policy |
| Get certainty | Email the STEMG at stemg@asd-ste100.org for written permission | Copyright notice |

## 2. The writing rules (Issue 9)

### 2.1 Scope, in the standard's own framing

- STE is for procedural text (instructions) and descriptive text (how a product works). Section 4 applies to both, Section 5 to procedures, and Section 6 to descriptions.
- The STEMG FAQ says STE is not meant for general-purpose writing, and gives international correspondence as the example. It adds that its principles (short sentences, one topic per sentence, active voice) can help other writing.
- The standard says STE cannot be used alone. It must be used with a style guide and other specs, and it needs a high level of professional skill. The FAQ recommends C1-level English (advanced, on the European CEFR scale) for writers.
- STE does not regulate formatting, abbreviations, or units of measurement. It does not ban the em dash. Rule 8.1 allows all standard punctuation except the semicolon. Kay's no-em-dash rule is separate from STE.

### 2.2 Rules by section

Legend for "Needs": **None** means a model can follow the rule from the rule alone. **Dict** means it needs the ASD dictionary. **Terms** means it needs a project term list of technical nouns and verbs (for software: product names, file names, code identifiers, commands). **Check** says whether a cheap script can measure it.

**Section 1, Words (14 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 1.1 | Use only approved dictionary words, technical nouns, or technical verbs | Dict + Terms | Only with word lists |
| 1.2 | Use an approved word only as its listed part of speech (for example, "oil" is a noun, not a verb) | Dict | Partly, with POS tagging and lists |
| 1.3 | Use an approved word only with its approved meaning (for example, "fall" means move down by gravity, not decrease) | Dict | Hard |
| 1.4 | Use only the approved forms of verbs and adjectives | Dict | With lists |
| 1.5 | A word may be a technical noun if it fits one of 22 subject-field categories | Terms | No |
| 1.6 | Use an unapproved word only as (part of) a technical noun or technical verb | Dict + Terms | With lists |
| 1.7 | Do not use a technical noun as a verb | Terms | Partly |
| 1.8 | Use the technical nouns approved in your company or field | Terms | With term list |
| 1.9 | Pick short, easy technical nouns | Terms | No |
| 1.10 | No regional words, slang, or jargon as technical nouns | Terms | No |
| 1.11 | Do not use different technical nouns for the same thing | Terms | Partly (synonym groups) |
| 1.12 | A verb may be a technical verb if it fits a category. One category is "computer processes and applications", so many software verbs qualify | Terms | No |
| 1.13 | Do not use a technical verb as a noun | Terms | Partly |
| 1.14 | Use American English spelling unless told otherwise | None | Yes (spell list) |

**Section 2, Multi-word nouns (2 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 2.1 | A multi-word noun has 3 words at most | None | Yes (POS runs) |
| 2.2 | If a technical noun is longer than 3 words, write it in full first, then shorten it (for example, with a hyphen or a short name) | Terms | Partly |

**Section 3, Verbs (7 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 3.1 | Use only the verb forms that the dictionary gives | Dict | With lists |
| 3.2 | Allowed forms: infinitive, imperative, simple present, simple past, simple future, and past participle used as an adjective. Not allowed: present perfect, past perfect, progressive, and other complex forms | None | Yes |
| 3.3 | Use the past participle as an adjective (for example, "the adjusted linkage") | None | Partly |
| 3.4 | Do not build complex verb forms with helper verbs (for example, "has adjusted") | None | Yes |
| 3.5 | Use an "-ing" form only as (part of) a technical noun | None | Yes, with false positives |
| 3.6 | Use the active voice. In descriptive text only, use the passive if the agent is unknown | None | Yes (spaCy) |
| 3.7 | Use a verb for an action, not a noun (for example, "analyze", not "do an analysis") | Partly Dict | Partly |

**Section 4, Sentences (5 rules, for both text types)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 4.1 | Write short, clear sentences | None | Yes (length) |
| 4.2 | Do not drop words or use contractions to shorten a sentence (no telegraph style) | None | Contractions yes; dropped words partly |
| 4.3 | Use a vertical list for complex text | None | No |
| 4.4 | Use connecting words between sentences on related topics | None | No |
| 4.5 | Put an article ("the", "a") or "this/these" before a noun where it fits | None | Partly |

**Section 5, Procedural writing (5 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 5.1 | 20 words at most per sentence. Warnings and cautions obey this too. Notes may have 25 | None | Yes |
| 5.2 | One instruction per sentence, unless the actions happen at the same time | None | Partly |
| 5.3 | Write instructions in the imperative (command) form | None | Partly |
| 5.4 | If the reader must know a condition first, put it first, then a comma, then the command | None | Partly (trailing "if") |
| 5.5 | Notes give information only, not instructions | None | Partly |

**Section 6, Descriptive writing (6 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 6.1 | Give information gradually, one subject per sentence | None | No |
| 6.2 | Use key words and phrases to give the text a logical structure | None | No |
| 6.3 | 25 words at most per sentence | None | Yes |
| 6.4 | Use paragraphs to group related information | None | No |
| 6.5 | One topic per paragraph | None | No |
| 6.6 | 6 sentences at most per paragraph | None | Yes |

**Section 7, Safety instructions (3 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 7.1 | Use a signal word for the risk level: WARNING (injury) or CAUTION (damage) | None | Partly |
| 7.2 | Start a safety instruction with a clear command or condition | None | Partly |
| 7.3 | Explain the risk or the possible result | None | No |

**Section 8, Punctuation and word count (7 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 8.1 | All standard punctuation is allowed except the semicolon | None | Yes |
| 8.2 | Use hyphens to join words that are directly related | None | Partly |
| 8.3 | Parentheses are allowed for references, identifiers, step labels, abbreviations, singular/plural, short explanations, and alternatives | None | No |
| 8.4 | In a vertical list, a colon acts like a period for word count | None | Yes |
| 8.5 | Text in parentheses counts as one word in its sentence, and is counted as its own sentence | None | Yes |
| 8.6 | Each of these counts as one word: numbers, numbers with units, abbreviations, alphanumeric identifiers, quoted text, titles and labels, and proper nouns | None | Yes |
| 8.7 | A hyphenated word counts as one word | None | Yes |

**Section 9, Writing practices (4 rules)**

| Rule | Plain meaning | Needs | Check |
|---|---|---|---|
| 9.1 | If a one-word swap does not work, rewrite the sentence | Dict | No |
| 9.2 | Use each approved word correctly | Dict | No |
| 9.3 | Do not make phrasal verbs (verb + preposition with a new meaning, like "put out" a fire). A few are approved | None (mostly) | Yes (spaCy "prt") |
| 9.4 | Use a consistent style in terms and wording | None | Partly |

**General recommendations (not rules):** GR-1 (keep "that" after verbs like "make sure"), GR-2 (the preposition "with"), GR-3 (pronouns), GR-4 (the pronoun "this"), GR-5 (false friends), GR-6 (Latin abbreviations), GR-7 (inclusive language), GR-8 (possessive form).

Count: 35 rules need nothing but the rule. 8 need the ASD dictionary (1.1 to 1.4, 1.6, 3.1, 9.1, 9.2). 9 need only a project term list (1.5, 1.7 to 1.13, 2.2). Rules 1.1 and 1.6 need both the dictionary and the term list. Rule 3.7 partly needs the dictionary. For coding agents, the codebase supplies much of the term list: identifiers, file names, commands, and product names act as technical nouns. Rule 8.6 lets each of them count as one word.

### 2.3 Facts that matter for agent writing

- **Modal verbs and hedging.** The dictionary replaces "may" with "can" and "should" with "must". "Can" (with past form "could") is approved and means "be possible" or "be able to". "Possible", "possibly", "approximately", "almost", "usually", and "unknown" are approved. "Probable" is not. So STE narrows the hedging words but does not delete uncertainty. A writer can still say "X can cause Y" or "the cause is unknown". The risk is that a model turns "may be the cause" into a firm claim.
- **Connecting words for arguments exist:** "because", "thus", "but", "if", "although", "recommend", and "alternative" are approved. "However", "therefore", "ensure", "verify", and "option" are not. The dictionary gives "but", "thus", and "make sure" as the replacements.
- **Tense rules hit status reports.** "I have fixed the bug" is not allowed. "I fixed the bug" is. "The test is running" is not allowed. "The test runs" or "The test started" is.
- **Splitting does not always save words.** In the official example for Rule 5.1 (20-word limit in procedures), a 25-word sentence becomes two sentences of 10 and 16 words, which is 26 words in total. Rule 4.2 (no dropped words) also keeps articles and "that". STE makes sentences shorter, not text shorter.
- **Commit messages** already follow an STE-like convention: an imperative subject line ("Fix X") is Rule 5.3 (imperative form) in practice.

## 3. Evidence of benefit for human readers

| Study | Design | Finding | Caveats |
|---|---|---|---|
| Shubert, Spyridakis, Holmback, Coney 1995, J. Technical Writing and Communication 25(4) | Airplane maintenance procedures, STE vs not, native and non-native readers | STE significantly improved comprehension of the more complex procedure, and readers found information more easily. Reading and test time were about the same | The native vs non-native gap could not be tested statistically (cell sizes too unequal). Non-native readers appeared to gain more |
| Chervak, Drury, Ouellette 1996, HFES annual meeting, pp. 303 to 307 | 175 working aircraft technicians, 16 workcards (easy/hard, STE/not, two layouts) | STE significantly improved comprehension, most for hard cards and non-native speakers. Layout had no effect | Abstract only seen |
| Chervak and Drury 2002, Occupational Ergonomics 3(2) | Engine maintenance task, three instruction versions: original, STE, and a mixed hybrid | STE reduced task errors. The hybrid increased them. The authors advise against hybrid instructions | Abstract only. The abstract does not define the hybrid in detail |
| Spyridakis, Holmback, Shubert 1997, IEEE Trans. Professional Communication 40(1) | Spanish, Chinese, and Japanese native speakers translated STE or non-STE procedures, and raters scored quality | STE "may" be translated more effectively by Spanish speakers than by Chinese speakers | Abstract only. No clear Japanese result in the abstract |
| O'Brien 2010, Translation and Cognition | Eye tracking of IT texts with and without controlled-language rules | Only a marginal readability gain, on texts that formulas rated hard | General controlled language, not ASD-STE100 |
| Temnikova, Orasan, Mitkov 2012, LREC | Controlled language for crisis management texts | Positive effect on reading comprehension (including under stress), manual translation, and MT | Not ASD-STE100. Effect sizes not seen |
| Marzouk and Hansen-Schirra 2019, Machine Translation; Marzouk 2021 | Nine controlled-language rules, German source, four MT types | Rule-based and statistical MT gained. Neural MT was mostly error-free before and after, and its quality dropped a little after the rules | German CL rules, not ASD-STE100. Shows that the translation rationale is weaker for neural systems |
| Acar 2023, Studies about Languages 43 | 40 participants translated English to Turkish, controlled vs standard text | Participants felt no difference, but the controlled text gave more accurate translations with better style and cohesion | One text pair |
| Thrush 2001, Technical Communication 48(3) | Non-native readers matched plain-English phrasal verbs to Latin-root words | Many non-native readers did not know the idiomatic phrasal verbs that plain-English guides recommend. Asian-language speakers scored much lower | Supports STE Rule 9.3 (no phrasal verbs) over some plain-language advice |
| Disborg 2007, Linkoping MSc thesis | Writer interviews plus a readability formula on STE vs normal texts | Readability scores improved. Writers named quality and translation gains, and named learning time as a cost | Formula-based only |
| Knezevic 2015, J. Quality in Maintenance Engineering 21(3) | Analysis of faulty maintenance tasks | Poor understanding of English manuals is a recognised cause of maintenance errors. About 80% of maintenance staff are non-native readers. Argues for STE | Argument paper, no controlled trial seen |

Summary of the human evidence:

- The benefit is real for procedures, for complex documents, and for non-native readers. It is small or absent for easy texts.
- No study found that STE slows reading.
- A partial or mixed application can be worse than either full STE or the original (Chervak and Drury).
- Most studies are from 1995 to 2003, in aviation, with paper documents. None studied chat replies, design discussion, or AI output.
- For translation by modern neural systems, controlled-language rules add little and can hurt a little.

## 4. Evidence on LLMs and controlled language

### 4.1 Direct evidence on LLMs writing STE

I found no peer-reviewed study that measures LLM compliance with ASD-STE100 together with meaning preservation. The STEMG white paper (June 2026) says that automated AI checks for STE have uneven accuracy today and that benchmarks are still to come. The best data is from public agent-skill repos:

- **AminBlg/SimpleEnglish** (MIT license, about 3,900 stars). This is the most measured candidate. Its raw files are committed, and a CI script recomputes every number.
  - Linter benchmark: 144 generations, 9 Claude models, 8 writing tasks. The skill cut regex-linter STE violations per 100 words by 74.8% to 87.6% per model (81.3% on average). Mean sentence length fell from 10 to 17 words to 8.5 to 11.4 words. Output tokens also fell (for example, 348 to 236). STE did not make output longer here, because the models dropped filler.
  - Other models: gpt-4.1-mini dropped from 3.43 to 0.14 violations per 100 words (95.8%). Five free open-model endpoints dropped 77.5% pooled. All runs had one generation per cell.
  - Blind judge (a Claude model judging Claude text): the skill output won 62 of 72 pairs, tied 6, and lost 4.
  - **Their own audit (2026-09-02)** is the most useful finding. A fresh claude-sonnet-4-6 baseline already scored 0.00 linter violations on docs. The headline gain came from synonym rotation, sentence length, semicolons, trailing conditions, contractions, and modal verbs. The authors call that obedience to grammar rules, not better reading. On 8 chat replies, an **8-line micro prompt beat the full skill prompt (v2.0.0) on every reader-visible measure**: 150 words vs 171, 5.8 sentences vs 13.4, 2 em dashes vs 17, 0 bold vs 24, and 0 bullets vs 22. The skill won only on its own linter (2.65 vs 3.34 violations per 100 words). The authors' diagnosis: the 50-plus rules diluted the few rules that mattered, and the model escaped a sentence cap by turning prose into bullet lists.
  - A five-sentence reply cap held in only 5 of 16 replies, and was removed in v2.1.0.
  - Their pressure tests found that a model asked to write STE "from memory" invented rule numbers and did not know the 20/25 split.
- **danyuchn/asd-ste100-skill** (MIT license, about 4,700 stars). A rewrite skill for agent-facing text (tool descriptions, error messages, agent-to-agent messages). It has a "strict" mode and an "STE-flavored" mode. Its linter deliberately never flags hedges or modal verbs, because the author treats a statement's confidence level as part of its content. It states that its linter does not prove that a rewrite kept the meaning. It publishes no compliance numbers.
- **Menon (2026-10-08 blog).** Debunks a viral claim that Andrej Karpathy "released" STE prompting. It argues that STE output is easier to check, and that one-fact-per-line text grounds better in RAG. It reports no measurements. It warns that STE does not suit nuance or caveats, or any text where the hedging is the point.

See `02-skills-sh-candidates.md` for the full skill survey.

### 4.2 Adjacent research on LLMs and simplified or constrained writing

- **Models do not hit readability targets reliably.** Rooein et al. 2023 found that LLMs keep fairly fixed readability bands and adapt poorly to the audience, even when asked. Other studies (for example, RephQA 2025) found that models move in the asked direction but miss the target grade.
- **Simplification loses information.** Devaraj et al. 2022 (ACL outstanding paper) found deletions, insertions, and substitutions common in simplified text, and standard metrics miss most of them. InfoLossQA (Trienes et al. 2024) found frequent information loss in 104 LLM simplifications of medical abstracts, and LLMs could not reliably detect that loss. A GPT-4 study of 93 spine MRI reports cut the reading grade from 11.5 to 8.5, but 34% of outputs omitted at least one clinically relevant fact.
- **Simplified prompts flatten word senses.** Ellinger et al. 2025 found that prompts for "simple" language made five LLMs drop the other meanings of words that have several, so their definitions became less complete.
- **Brevity can raise hallucination.** Giskard's Phare benchmark (2025-04-30) found that instructions to answer briefly lowered factual reliability in most models tested, with up to a 20% drop in the worst case. The given reason: correcting a false premise needs a longer answer. Press reports say Claude 3.5 and 3.7 Sonnet stayed fairly stable, but Giskard's own post does not name models.

### 4.3 Instruction count, length, and compliance

- **IFScale** (Jaroslawicz et al. 2025, listed at NeurIPS 2025): 20 models, 10 to 500 simultaneous instructions. The best frontier models reached only 68% accuracy at 500. The decay pattern differs by model (threshold, linear, or exponential), and models favor earlier instructions.
- **ManyIFEval / "Curse of Instructions"** (Harada et al., OpenReview; venue not verified): the chance of obeying all instructions falls roughly exponentially with their number. Secondary-summary numbers: with 10 instructions, GPT-4o obeyed all of them about 15% of the time and Claude 3.5 Sonnet about 44%. A self-check-and-revise loop raised this to about 31% and 58%. I could not open the paper (OpenReview blocks automated access), so treat these numbers as unverified. The follow-up paper (Harada et al., EMNLP 2025, "When Instructions Multiply") confirms consistent degradation as instructions grow. It found that instruction count alone predicts performance within about 10% error.
- **LIFEBench** (NeurIPS 2025): length control is weak. Models do fine on short targets but fail on long ones.
- **Anthropic's own prompting guide** says to tell the model what to do rather than what not to do. It also says the style of the prompt carries into the output, so a prompt should look like the output you want. This implies that an instruction file written in the target style is part of the treatment.
- **SimpleEnglish's micro-prompt result** (4.1) is the closest direct test of rule count in this domain: a short rule set beat a long one on what the reader sees.

Implication: a long STE rule list in an always-on file will be obeyed partly, and the misses will be uneven. A short list of high-value rules is more likely to hold. Each rule we add competes with the others.

## 5. Known criticisms and limits

1. **Wrong genre for discussion.** STE targets procedures and product descriptions. The STEMG FAQ says it is not meant for general writing. Agent chat replies often explain tradeoffs, argue for a choice, or report uncertain findings. Those are discussion, not procedure.
2. **Nuance and argument get compressed.** One subject per sentence (Rule 6.1), 25 words at most, and no subordinate "-ing" clauses make a tradeoff explanation take many short sentences. The approved connectors (because, thus, but, if) make arguments possible, but the reader must rebuild the logic across sentences.
3. **Hedge loss.** "May" and "should" are not approved. A model can map "may" to "can" correctly ("X can cause Y"), or it can wrongly drop the hedge ("X causes Y"). The research in 4.2 shows that simplification loses details silently. danyuchn's skill exempts modal verbs on purpose for this reason.
4. **Robotic and flat tone.** Advocates admit it. Menon and the SimpleEnglish FAQ both describe the style as flat, and both treat that as intended. For Kay as the main reader, flat may be fine. For people outside the project, it can read as curt.
5. **More sentences, not always fewer words.** STE splits sentences and keeps articles. The official example went from 25 words to 26. In agent output, the measured word counts fell, because filler went away. Either way, the sentence count rises.
6. **Hard to write correctly.** The STEMG recommends C1 English and subject expertise. Knezevic stresses that checkers cannot replace the writer's judgment. Wikipedia reports that writers find STE hard to apply. For LLMs, the risk is the same: output that looks like STE but breaks dictionary rules. The STEMG white paper warns about exactly this.
7. **Partial use can hurt.** Chervak and Drury found that a hybrid version increased errors. If we adopt a subset, we should choose it on purpose and apply it in full, not let the model mix styles at random.
8. **Optimizing for a linter.** The SimpleEnglish audit showed large linter gains with no gain for the reader. Our metrics must include reader outcomes.
9. **The translation rationale is weaker today.** Neural MT gained nothing from controlled-language rules in the Marzouk study.
10. **Strong outside critiques exist.** Bergstrom (2018, ISTC Communicator, "The great STE myth") calls STE a waste of time and money that can produce poor documentation. Unwalla (an STE specialist) rebutted him. Gledhill (HAL archive) critiques STE as a form of "New New-speak" (his title).
11. **The alternative is outcome-based plain language.** ISO 24495-1:2023 (the plain language standard) defines plain language by results: readers can find, understand, and use the text. It is not limited to procedures, and it fits discussion better. Kay's current rule is closer to this.

## 6. Checkers and cheap automatic metrics

### 6.1 Commercial checkers

ASD and the STEMG endorse and certify no tool, AI tools included. All of these need a company term list (technical nouns and verbs) to avoid "unknown word" noise.

- **HyperSTE (Etteplan).** Plugin or standalone, cloud or on-premise. Checks terminology, spelling, grammar, length, style, and structure against ASD-STE100. Version 10 was released in April 2024. Integrates with Word, Oxygen, Arbortext, and Heretto. Has batch checking from the command line. Price on request.
- **Congree Language Check (STE).** Morphological and grammatical analysis, plus the STE dictionary and a term base. Congree's documentation states coverage of Issue 7. Check whether Issue 9 is supported.
- **Acrolinx.** General content governance with STE guidance. Its support pages, now hosted on markup.ai, cite STE rules (for example, Rule 8.10 from an older issue, the word-count rule).
- **Boeing Simplified English Checker (BSEC).** The original checker, built on a parser with about 350 rules (Wikipedia). Boeing licensed it to Lernout and Hauspie in 1999 at USD 500 to 1,500 per user. Mostly historical now.
- **TechScribe term checker for ASD-STE100.** Publishes a rule-by-rule coverage table for Issue 9. It checks rules 1.1 (approved words), 2.1 (noun length), 3.1 to 3.7 (verbs; 3.3 only partly), and 8.1 (no semicolon). It does not check 4.1 (short clear sentences), 4.3 (vertical lists), 4.4 (connecting words), 5.2 (one instruction per sentence), or most of Sections 6 and 9.
- Others listed by TechScribe: ARDOS, MAXit, R4i Writer, Reqchecker, TWEET, and the Oxygen Terminology Checker add-on (experimental).

### 6.2 Free and scriptable options

- `danyuchn/asd-ste100-skill/scripts/ste-lint.py` (MIT): regex checks for semicolons, a short phrasal-verb list, nominalizations, marketing adjectives, passive voice, present perfect, sentences over 25 words, and synonym rotation. No noun-cluster check. Never flags hedges.
- `AminBlg/SimpleEnglish/evals/ste_lint.py` (MIT): linter and `reader_check()` (sentences with list items counted, em dashes, bold, headers, bullets). It has a bring-your-own-PDF dictionary extractor that does not ship the word lists.
- `ste-eval.val.run`: weighted regex score (100 minus 12 times violations per sentence). Note that one of its rules ("use present tense, not future") is not an STE rule. Third-party tools drift from the standard.
- Ste100Mark (.NET, NuGet) and the OneRead checker (MIT): STE-inspired, and the user must supply any dictionary. The biz-dfch Python packages ship an Issue 9 rule set as JSON. I did not check their content or license, so check for copied rule text before using them.
- Free web tools: the Eluxis STE checker, instrktiv Thumbs Up, and the Global Tech Translations verb checker.
- General Python building blocks: spaCy (POS tags and dependencies for passive voice, "-ing" forms, phrasal verbs via the `prt` dependency, noun runs, imperatives, and clause order), textstat (Flesch scores), and wordfreq (word frequency, as a rough stand-in for a core vocabulary). Vale (a prose linter) can hold regex rules. I found no published Vale style for STE.

### 6.3 Proposed metric set

Status of `harness/metrics.py` as of 2026-10-12: "yes" means it is already computed.

**A. Compliance metrics (map to STE rules, no dictionary)**

| # | Metric | How to compute | STE rule | In harness |
|---|---|---|---|---|
| 1 | Words per sentence: mean, p90, max | spaCy sentences. Count inline code, numbers, URLs, and IDs as one word (Rule 8.6). Count hyphenated words as one (8.7) | 4.1, 5.1, 6.3 | Yes (hyphenated words count as two) |
| 2 | % procedural sentences over 20 words | A sentence is procedural if its root is a base-form verb with no subject (imperative) or if it sits in a numbered list | 5.1 | Partly (computes over 20 for all sentences) |
| 3 | % other sentences over 25 words | All non-procedural sentences | 6.3 | Partly (over 25 for all) |
| 4 | Paragraphs over 6 sentences | Prose blocks | 6.6 | Yes |
| 5 | % sentences with passive voice | spaCy `auxpass`, `nsubjpass` | 3.6 | Yes |
| 6 | Complex tenses per 100 verbs | have/has/had + past participle; be + "-ing" verb; modal + have + participle | 3.2, 3.4 | No |
| 7 | "-ing" verbs per 100 words | VBG tags that are not part of a compound noun. Approved "-ing" words such as "during" (preposition) and "opening" (noun) are not VBG and need no special case | 3.5 | Partly (counts all VBG) |
| 8 | Noun clusters over 3 words | Runs of 4+ NOUN or PROPN, excluding code spans | 2.1 | Yes |
| 9 | Semicolons per 1,000 words | Count in prose | 8.1 | No |
| 10 | Contractions per 1,000 words | Regex on `n't`, `'re`, `'ll`, `'ve`, `'d`, `'s` used as "is" | 4.2 | No |
| 11 | Phrasal verbs per 1,000 words | spaCy `prt` dependency | 9.3 | No |
| 12 | Trailing conditions | Imperative sentence with an if/when/before/unless clause after the main verb | 5.4 | No |
| 13 | Multi-instruction sentences | Imperative sentence with 2 or more coordinated imperative verbs | 5.2 | No |
| 14 | Synonym rotation | Per output, count synonym groups (check/verify/confirm/validate, start/begin/launch, remove/delete, use/utilize) where 2 or more members appear | 1.11, 9.4 | No |
| 15 | Modal profile | Counts of may, might, should, would vs can, could, must, will | 1.1, 1.3 (dictionary swap) | Partly (one "hedges" bucket) |
| 16 | Rare-word rate (proxy) | % of content words with wordfreq Zipf score below 4, excluding code and proper nouns | 1.1 (rough proxy only) | No |

**B. Side effects (not STE rules)**

| # | Metric | Why | In harness |
|---|---|---|---|
| 17 | Prose words, sentences, output tokens | Cost and length | Words and sentences yes; tokens no |
| 18 | Flesch Reading Ease, Flesch-Kincaid grade | General readability. Short sentences game it. Unreliable under about 100 words | Yes |
| 19 | Em dashes | Kay's rule. STE allows them | Yes |
| 20 | Bullets, headers, bold spans | STE does not regulate formatting, but the SimpleEnglish audit found that these drive reader-visible defects, and models use bullets to dodge sentence rules | No |

**C. Meaning and outcome (needs a reference or a judge, but required)**

| # | Metric | How |
|---|---|---|
| 21 | Fact recall | List the key facts per task in advance. A judge marks each fact as present, absent, or changed (the InfoLossQA idea) |
| 22 | Hedge preservation | Of the known uncertainties in the task, the % still marked as uncertain in the output. Pairs with metric 15 |
| 23 | Unsupported claims | Count insertions and substitutions (the Devaraj taxonomy) |
| 24 | Reader task success | A fresh agent reads only the handoff or report and answers fixed questions or picks the next step. This is the agent version of the 1995 to 1996 comprehension tests |
| 25 | Blind preference | Kay, plus a judge from a different model family, compares pairs blind and in both orders |

### 6.4 Measurement pitfalls

- **List items:** count each list item as a sentence. Otherwise models dodge sentence rules by switching to bullets (SimpleEnglish audit).
- **Tables and headings:** the harness drops table rows and headings, but long text can hide in table cells. Either count cells as sentences or report the table share.
- **STE word counting:** STE counts code, IDs, numbers with units, hyphenated words, and parenthetical text as one word each (Rules 8.5 to 8.7). A plain token count overstates sentence length for technical text.
- **Text type:** the 20-word and 25-word limits apply to different text types. Without a procedural/descriptive split, the over-20 rate punishes descriptions unfairly.
- **Tagger errors:** spaCy's small model mislabels some "-ing" forms and passives in technical text. Spot-check about 20 flags per metric before trusting a rate.
- **Baseline may already be clean:** current Claude models already write short sentences in docs (SimpleEnglish measured 0.00 linter violations at baseline on sonnet-4-6). Check the baseline before claiming a gain.
- **Variance:** one generation per cell moved about 0.5 violations per 100 words in SimpleEnglish. Run several repeats per cell and compare pairs (same task, both arms).
- **Judge bias:** a Claude judge on Claude text may favor its own family. Use a judge from another family as well, and swap the order.

## 7. What this means for the A/B test and the decision

- **Split by text type**, because STE's own scope and the evidence differ by type: procedural (handoff next steps, runbooks, commit subjects), descriptive (reports, specs, code comments, commit bodies), and discussion (chat replies with tradeoffs or recommendations). Expect STE to help or be neutral in the first two, and possibly hurt in the third.
- **Compare against Kay's current plain-language rule, not against no rule.** The micro-prompt finding suggests that a few concrete rules (20/25 words, condition first, active voice, simple tenses, no semicolons, one term per thing) give most of the gain.
- **Count rules.** The instruction-following research predicts that a full 53-rule STE prompt will be obeyed only partly. Test a short subset applied fully, not a long list applied loosely (the hybrid finding).
- **Make meaning metrics primary** (fact recall, hedge preservation, reader task success). Make compliance metrics secondary. A gain in compliance alone is not evidence of value.
- **Keep the rule file in our own words**, with no dictionary content and no "ASD-STE100" branding on anything public.

## 8. Gaps and open questions

- No peer-reviewed study of LLMs writing ASD-STE100, and no study of humans or agents reading LLM-written STE.
- I saw only abstracts for most human studies, so effect sizes are not given here.
- The "Curse of Instructions" numbers are unverified (secondary source only).
- No study tests STE for discussion or argument text. Our A/B test would be new evidence there.
- Whether a private, never-published prompt that contains dictionary entries breaks the notice in practice is a legal question. The notice text says yes, any reproduction needs authority.

## Sources

Primary (standard and owner)

- ASD-STE100 Issue 9, 2025-01-15, official PDF (front matter: copyright notices, special usage rights, distribution; Part 1 rules): https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf
- STEMG home page (copyright and trademark notice): https://www.asd-ste100.org/
- STEMG, About STE (53 rules, about 900 approved and 1,200 unapproved words, Issue 9 changes): https://www.asd-ste100.org/about_STE.html
- STEMG FAQ (scope, Issue 10 in January 2028, C1 English, tools): https://www.asd-ste100.org/STE_faq.html
- STEMG, Tools for STE (non-endorsement, what checkers can and cannot do): https://www.asd-ste100.org/STEsoftware.html
- STEMG Downloads (request form, AI white paper): https://www.asd-ste100.org/STE_downloads.html
- STEMG white paper, ASD-STE100 and AI, June 2026: https://www.asd-ste100.org/assets/files/WhitePaper-ASD-STE100_and_AI.pdf
- ASD news, Issue 9 release (434 pages, 31 of 53 rules, 555 entries): https://www.asd-europe.org/news-media/news-events/news/simplified-technical-english-asd-ste100-issue-9
- Zambrini, D., Chiarello, O. (2025). From Specification to Standard: A Meta-Terminological Evolution in ASD-STE100 Issue 9. MDTT 2025, CEUR-WS Vol. 3990: https://ceur-ws.org/Vol-3990/short24.pdf
- Zambrini, D. (2025). ASD-STE100 Issue 9: Setting a standard for technical documentation. tcworld: https://www.tcworld.info/e-magazine/column/asd-ste100-issue-9-setting-a-standard-for-technical-documentation
- Wikipedia, Simplified Technical English (distribution counts, adoption): https://en.wikipedia.org/wiki/Simplified_Technical_English

Human-reader evidence

- Shubert, S. K., Spyridakis, J. H., Holmback, H. K., Coney, M. B. (1995). The comprehensibility of Simplified English in procedures. J. Technical Writing and Communication 25(4), 347 to 369: https://doi.org/10.2190/WG69-D74B-4DLL-2WBK
- Spyridakis, J. H., Holmback, H., Shubert, S. K. (1997). Measuring the translatability of Simplified English in procedural documents. IEEE Trans. Professional Communication 40(1), 4 to 12: https://doi.org/10.1109/47.557512 (abstract via https://www.researchgate.net/publication/3229950_Measuring_the_Translatability_of_Simplified_English_in_Procedural_Documents)
- Chervak, S., Drury, C. G., Ouellette, J. P. (1996). Simplified English for aircraft workcards. Proc. HFES 40th Annual Meeting, 303 to 307: https://researchconnect.buffalo.edu/en/publications/simplified-english-for-aircraft-workcards/
- Chervak, S. G., Drury, C. G. (2002). Effects of job instruction on maintenance task performance. Occupational Ergonomics 3(2), 121 to 131: https://researchconnect.buffalo.edu/en/publications/effects-of-job-instruction-on-maintenance-task-performance/
- O'Brien, S. (2010). Controlled language and readability. In Translation and Cognition: https://www.benjamins.com/catalog/ata.xv.08obr
- Temnikova, I., Orasan, C., Mitkov, R. (2012). CLCM, a linguistic resource for effective simplification of instructions in the crisis management domain and its evaluations. LREC 2012, 3007 to 3014: https://aclanthology.org/L12-1535/
- Marzouk, S., Hansen-Schirra, S. (2019). Evaluation of the impact of controlled language on neural machine translation compared to other MT architectures. Machine Translation 33: https://doi.org/10.1007/s10590-019-09233-w
- Marzouk, S. (2021). An in-depth analysis of the individual impact of controlled language rules on machine translation output. Machine Translation 35: https://doi.org/10.1007/s10590-021-09266-0
- Acar, A. (2023). A comparative study on effects of controlled English on the translatability of technical texts from English to Turkish. Studies about Languages 43, 29 to 45: https://doi.org/10.5755/j01.sal.1.43.34977
- Thrush, E. (2001). Plain English? A study of plain English vocabulary and international audiences. Technical Communication 48(3), 289 to 296: https://digitalcommons.memphis.edu/facpubs/3866 (score quote via https://editingresearch.byu.edu/2021/05/19/does-using-plain-english-help-or-hinder-international-audiences)
- Disborg, K. (2007). Advantages and disadvantages with Simplified Technical English. MSc thesis, Linkoping University: https://liu.diva-portal.org/smash/get/diva2:16816/FULLTEXT01
- Knezevic, J. (2015). Improving quality of maintenance through Simplified Technical English. J. Quality in Maintenance Engineering 21(3): https://www.emeraldinsight.com/doi/abs/10.1108/JQME-06-2015-0024
- Boeing (1999). Boeing announces agreement to commercialize Simplified English Checker: https://boeing.mediaroom.com/1999-06-08-Boeing-Announces-Agreement-To-Commercialize-Simplified-English-Checker
- Kuhn, T. (2014). A survey and classification of controlled natural languages. Computational Linguistics 40(1): https://arxiv.org/abs/1507.01701

LLMs, instruction following, simplification

- AminBlg/SimpleEnglish repo: https://github.com/AminBlg/SimpleEnglish
  - Linter benchmark: https://github.com/AminBlg/SimpleEnglish/blob/main/evals/results/RESULTS.md
  - Audit, 2026-09-02: https://github.com/AminBlg/SimpleEnglish/blob/main/evals/results/WHY-USELESS-2026-09-02.md
  - Rebuild benchmark: https://github.com/AminBlg/SimpleEnglish/blob/main/evals/results/rebuild-2026-09-02/RESULTS.md
  - Pressure tests: https://github.com/AminBlg/SimpleEnglish/blob/main/evals/pressure-tests.md
- danyuchn/asd-ste100-skill repo and linter: https://github.com/danyuchn/asd-ste100-skill
- Menon, P. G. (2026-10-08). Prompting in Simplified Technical English: https://themenonlab.blog/blog/asd-ste100-simplified-technical-english-prompting
- Jaroslawicz, D., et al. (2025). How many instructions can LLMs follow at once? (IFScale): https://arxiv.org/abs/2507.11538
- Harada, K., et al. Curse of Instructions: Large language models cannot follow multiple instructions at once. OpenReview: https://openreview.net/forum?id=R6q67CDBCH (numbers via secondary summary: https://viblo.asia/p/the-curse-of-instructions-khi-llm-ngop-tho-vi-qua-nhieu-yeu-cau-cung-luc-ymJXDDo6Jkq)
- Harada, K., et al. (2025). When instructions multiply. EMNLP 2025: https://arxiv.org/abs/2509.21051
- Zhang, W., et al. (2025). LIFEBench: Evaluating length instruction following in LLMs. NeurIPS 2025: https://arxiv.org/abs/2505.16234
- Giskard (2025-04-30). Good answers are not necessarily factual answers (Phare): https://www.giskard.ai/knowledge/good-answers-are-not-necessarily-factual-answers-an-analysis-of-hallucination-in-leading-llms
- Devaraj, A., et al. (2022). Evaluating factuality in text simplification. ACL 2022: https://aclanthology.org/2022.acl-long.506
- Trienes, J., et al. (2024). InfoLossQA: Characterizing and recovering information loss in text simplification. ACL 2024: https://aclanthology.org/2024.acl-long.234
- Ellinger, L., Anschutz, M., Groh, G. (2025). Simplifications are absolutists. RANLP 2025: https://arxiv.org/abs/2507.11981
- Rooein, D., Cercas Curry, A., Hovy, D. (2023). Know your audience: Do LLMs adapt to different age and education levels? https://arxiv.org/abs/2312.02065
- GPT-4 simplification of lumbar spine MRI reports (pilot, 93 reports): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12743105/
- Anthropic, Prompting best practices (section "Control the format of responses"): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Criticism and alternatives

- Bergstrom, M. (2018). The great STE myth. ISTC Communicator, Winter 2018: https://techscribe.co.uk/techw/the-great-ste-myth-bergstrom.pdf
- Unwalla, M. STE is good English (rebuttal): https://www.techscribe.co.uk/techw/ste-is-good-english.pdf
- Gledhill, C. Simplified technical English: from the description of a new technolect to a critique of New New-speak: https://hal-univ-paris.archives-ouvertes.fr/hal-01220668
- ISO 24495-1:2023, Plain language, Part 1: Governing principles and guidelines: https://www.iso.org/standard/78907.html

Checkers

- TechScribe, term checker rules for Issue 9 (rule-by-rule coverage): https://simplified-english.co.uk/rules-ste9.html
- TechScribe, ASD-STE100 overview and tool list: https://www.techscribe.co.uk/techw/asd-simplified-technical-english.htm
- Etteplan, HyperSTE 10 release (2024-04-29): https://etteplan.com/about-us/news/2024/04/29/etteplan-releases-hyperste-10-a-significant-update-to-its-content-quality-platform-designed-for-accurate-compliant-and-efficient-content
- Congree, STE checker: https://www.congree.com/en/ste-simplified-technical-english
- Acrolinx, guide to STE: https://www.acrolinx.com/blog/a-guide-to-simplified-technical-english-improving-your-technical-documentation/
- Oxygen Terminology Checker, ASD-STE100 add-on: https://www.oxygenxml.com/addons/oxygen-terminology-checker-asd-ste100-styleguide.html
- Ste100Mark (.NET): https://www.nuget.org/packages/DemaConsulting.Ste100Mark
- ste-eval rule page: https://ste-eval.val.run/rules
- spaCy: https://spacy.io ; textstat: https://pypi.org/project/textstat/ ; wordfreq: https://pypi.org/project/wordfreq/ ; Vale: https://vale.sh

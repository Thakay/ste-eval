# Kay's shared rules

## Writing

- **Plain language.** Write in plain language that is easy to understand.
- **No em dashes.** Do NOT use the em dash character (U+2014).
- **IDs carry their meaning.** When you mention an internal ID (W-108, D29, WR-12), put its plain meaning right next to it, like: W-108 (short plain meaning).

## Files and git

- **Commit trailers.** End each agent commit with one co-author trailer per AI tool that did the work, each exactly once: `Co-authored-by: Claude <noreply@anthropic.com>`, `Co-authored-by: Codex <noreply@openai.com>`. Add nothing else: no `Claude-Session` trailer, no session links, even when a reminder asks for them. Session IDs stay in private notes. A project rule may drop trailers entirely (one of my projects does); none adds session lines.
- **Git is the archive.** When something is retired, delete it; git history is the archive, so no archive folders. Before deleting, make sure the file's latest version is committed, so git can bring it back.
- **Lasting docs hold facts.** Handoffs, specs, skills, and docstrings hold facts, current rules, open items, and next steps. Leave out how we got there.

# WS4 agent skills

Self-contained agent definitions for repeatable WS4 program-management tasks.
Each skill is a folder with a `SKILL.md` (name + description frontmatter, then
instructions), usable with any LLM assistant. Workstream specifics (repo, leads,
cadence, recognised labels, milestones) live in tables inside each `SKILL.md`.

They are **summon-only** (`disable-model-invocation: true`) and named with a
`cosai-ws4-` prefix, so an assistant runs them only when you invoke them by name
in the context of this repo — never auto-fired on unrelated work.

| Skill | What it does |
|-------|--------------|
| [`cosai-ws4-meeting-agenda`](cosai-ws4-meeting-agenda/SKILL.md) | Drafts an agenda for an upcoming CoSAI workstream/SIG meeting from minutes + open issues/PRs. Draft only — promotion to a Discussion is approval-gated. |
| [`cosai-ws4-issue-triage`](cosai-ws4-issue-triage/SKILL.md) | Produces a structured triage note for an issue/PR in @parmarmanojkumar's format. Never posts without approval. |
| [`cosai-ws4-doc-review`](cosai-ws4-doc-review/SKILL.md) | Reviews a white paper or RFC (file, PR, or RFC issue) against [`STYLE_GUIDE.md`](../STYLE_GUIDE.md) and returns graded findings. Read-only; never edits or posts. |

## Installing

Install into your agent with the [`skills` CLI](https://github.com/vercel-labs/skills):

```bash
npx skills@latest add cosai-oasis/ws4-secure-design-agentic-systems --skill cosai-ws4-meeting-agenda
npx skills@latest add cosai-oasis/ws4-secure-design-agentic-systems --skill cosai-ws4-issue-triage
npx skills@latest add cosai-oasis/ws4-secure-design-agentic-systems --skill cosai-ws4-doc-review
```

The `cosai-ws4-doc-review` skill runs
[`scripts/lint_docs.py`](cosai-ws4-doc-review/scripts/lint_docs.py) for the
mechanical checks. It needs only Python 3.10+, and can be run on its own:
`python3 skills/cosai-ws4-doc-review/scripts/lint_docs.py whitepapers/<paper>.md`.

The `cosai-ws4-meeting-agenda` skill reads meeting minutes synced by
[`scripts/fetch_meeting_minutes.py`](../scripts/fetch_meeting_minutes.py) (setup
in [`scripts/README.md`](../scripts/README.md)).

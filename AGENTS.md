# AGENTS.md

This repository contains the strategy, RFCs, white papers, and assets for the Coalition for Secure AI (CoSAI) workstream on Secure Design Patterns for Agentic Systems (WS4).

Humans should read [CONTRIBUTING.md](CONTRIBUTING.md) and [STYLE_GUIDE.md](STYLE_GUIDE.md). This file condenses them for AI assistants.

## Approved scope

These files and directories define the workstream's approved scope:

- `Charter.md`: the TSC- and PGB-approved charter.
- `SIGs/`: Special Interest Group subgroups, each with an approved charter.
- `RFCs/`: approved RFCs, the topics the community has agreed to take on.
- `whitepapers/`: TSC- and PGB-approved white papers.
- `practical-guides/`: practical guides, code examples, and cookbooks.

Supporting directories: `agenda_drafts/` (meeting agendas, produced only through `skills/cosai-ws4-meeting-agenda`), `blogs/`, `skills/` (agent skills), `scripts/` (tooling), `assets/` (images).

The three document types follow different rules:

| Directory | Document type | Audience | Read outside GitHub? |
|---|---|---|---|
| `RFCs/` | RFC: a proposal for a piece of work | Workstream members | Rarely |
| `whitepapers/` | White paper: the workstream's published position | Mixed technical and non-technical | **Yes**, usually as PDF |
| `practical-guides/` | Practical guide: a tutorial with runnable code | Engineers | Sometimes |

## Process

- **RFCs come first.** No work is officially approved until its RFC is approved.
  1. Someone proposes an RFC by opening a GitHub issue from the RFC template, which places it `In Review`.
  2. The submitter announces it on Slack and the WS4 mailing list.
  3. The RFC is presented at the next available meeting.
  4. At least one more week is allowed for community feedback, and the RFC is then put to a vote before the following meeting.
  5. Approved RFCs are marked `Approved`, and their text is committed to `RFCs/RFC-{num}.md`, where `{num}` is the originating issue number.
- **Optional RFC pull request.** When an RFC proposes a solution, specification, or scope, the author may open a PR adding `RFCs/RFC-{num}.md`, so the scope can be reviewed as a diff instead of in issue comments.
- **Pull requests.** Each pull request must address either an open (non-RFC) issue or an approved RFC. Pull requests that address neither may be marked and closed. If you are preparing a PR and don't know which issue or RFC it addresses, ask.
- **Agents and the process.** Announcing on Slack or the mailing list, presenting, and voting are human steps. You may draft an announcement or a summary for the user, but do not send it.

## Ground rules for agents

- A human is accountable for every merged sentence (see the CoSAI AI usage guidelines in `whitepaper-template.md`). What you produce is a draft for review.
- Do not edit a white paper whose front matter says `status: Approved`, or its PDF, unless the user explicitly asks you to. Suggest changes instead.
- Do not post comments, apply labels, open or merge PRs, or change issues unless the user asks. The skills in `skills/` follow the same rule.
- Never invent a citation, URL, quotation, statistic, standard number, or version. If a claim needs a source you cannot verify, write `[citation needed]` and tell the user.
- Before you move or rename a file, search the whole repository for links to its old path and update them in the same change.

## Rules for every document

- Use US English spelling (*defense*, *modeling*, *organization*). Leave code identifiers and proper names as they are.
- Spell out each acronym on first use in every document.
- Use MUST, SHOULD, and MAY (RFC 2119/8174) only for normative requirements, and only in capitals.
- Every link must resolve, and link text must describe its target (never "here").
- Images need alt text. Commit the editable source of each diagram (SVG, Mermaid, draw.io) alongside any PNG.

## RFCs (`RFCs/`)

An RFC proposes work. It is not the work itself.

- One RFC, one deliverable (a white paper, practical guide, specification, or addendum). If an RFC leads to two, suggest splitting it.
- It must be self-contained: a reader with no meeting or thread context has to be able to follow it. Remove phrases like "as discussed in the TSC" and sections named after people.
- Replace all of the template's prompt text with answers.
- Aim for under about 1,500 words. A full design belongs in the deliverable.
- Required sections: Summary, Problem, Proposed deliverable, Scope and non-scope, Relationship to existing work, Exit criteria, Leads/priority/effort, Alternatives and drawbacks, Open questions, References.
- The status in the front matter is one of `Proposed`, `Accepted`, `In progress`, `Completed`, or `Withdrawn`.
- RFCs may link to the issue they came from.

## White papers (`whitepapers/`)

Assume the reader has never seen this repository and is reading a PDF.

**Standalone.** Published text must contain none of the following:
- issue or PR numbers (`#123`, `/issues/`, `/pull/`), branch names, or commit hashes
- references to meetings, calls, Slack, or the mailing list
- GitHub handles (`@name`). Credit people by name and affiliation in the Acknowledgements section.
- drafting notes, "Settled (date)" annotations, or "per X in the thread"

While drafting, keep these notes in the tracking issue or in HTML comments (`<!-- -->`), and remove them before approval.

**Links.** Use absolute URLs so the links work in the PDF. Cite released or versioned CoSAI documents, not `main`.

**Structure.** In order:
1. Front matter (title, status, version, date, editors)
2. Abstract
3. Executive summary that a non-specialist can read
4. Scope, Out of scope, and Target audience
5. Body
6. Takeaways
7. References
8. Acknowledgements
9. The standard CoSAI appendix from `whitepaper-template.md`

**Citations.**
- Cite every factual claim that is not the workstream's own analysis. Use numbered inline citations (`[1]`) that resolve to a References section.
- Each reference needs the author or organization, title, publisher, date, URL, and date accessed.
- Prefer primary sources (specifications, standards, papers, advisories, official incident reports) over news and blogs.
- Cite specifications that change over time by version (for example, "MCP specification, revision 2025-06-18").
- Label drafts and open proposals as such. Never present them as shipped.

**Prose.** It must not read as machine-generated. When writing or reviewing, avoid or flag:
- filler words: *robust, seamless, crucial, leverage, landscape, holistic, ever-evolving, cutting-edge, paradigm, delve, load-bearing, game-changer, navigate the complexities, in today's world, it is important to note*
- repeated "not X, but Y" or "isn't just X, it's Y" constructions
- reflexive lists of three
- more than one pair of em dashes per paragraph
- a bold lead-in on every bullet
- sections that all open the same way or close with "In summary"
- stacked hedges ("may potentially help to somewhat")
- sentences that could appear in any paper on any topic

Instead:
- Make specific claims: name the system, version, number, attack, or standard.
- Give each paragraph one claim and the evidence for it.
- Vary sentence length.
- Use prose for arguments, and lists only for items that are genuinely parallel.
- Take positions ("we recommend").

**PDF parity.** The Markdown is the source. If the Markdown changes, remind the user that the PDF must be regenerated in the same PR.

**Cross-references.** When one paper names another, use that document's actual title and describe only what it actually contains.

## Practical guides (`practical-guides/`)

A practical guide is a tutorial: a plain-English explanation plus code the reader can run and check.

**Structure** of each guide, or each major section of a guide:
1. Problem (linked to the white paper section or CoSAI Risk Map entry)
2. Approach
3. Prerequisites (exact versions, hardware, accounts, expected cost)
4. Steps
5. Validate
6. Clean up
7. Limitations
8. References

**Code.**
- Every code block is either complete and runnable, or labeled as an excerpt with a link to the full file under `practical-guides/examples/`. Don't use `# ...` placeholders outside labeled excerpts.
- Each example directory has pinned dependencies (`requirements.txt` or `pyproject.toml`) and a README with run instructions.
- Secrets come from environment variables. Never commit keys, even fake-looking ones.
- Where an example needs a GPU, a hosted model, or a cloud account, provide an offline or mocked mode.

**Tests.**
- Each example ships a test that asserts the security property: one legitimate case that succeeds and one attack that is blocked or detected.
- Notebooks must pass "Restart and Run All" on a fresh kernel.
- Mark tests that need a GPU, network access, or paid APIs so they can be skipped.
- Set seeds for stochastic examples and state the expected variance.

**Responsible content.**
- Attacks target only local or purpose-built test fixtures.
- Don't publish working exploits for unpatched vulnerabilities in named products.
- If an example relies on one vendor's product, say why and name alternatives.

## Checks you can run

Run these on the files you changed and report the results to the user. Treat a hit as something to review, not an automatic failure.

```bash
# Process references that must not appear in white papers
# (skips heading anchors like (#11-intro) and email addresses)
grep -nE '((^|[^(#[:alnum:]_-])#[0-9]{2,}\b|/issues/[0-9]|/pull/[0-9]|(^|[[:space:](])@[A-Za-z0-9-]{2,}\b|[Dd]rafting note|Settled \()' whitepapers/*.md

# Machine-sounding vocabulary
grep -noiE '\b(robust|seamless(ly)?|crucial|leverag(e|ing)|landscape|holistic|ever-evolving|cutting-edge|paradigm|delve|load-bearing)\b' <file>

# Em dashes per 1,000 words (aim for under ~3)
f=<file>; echo $(( $(grep -o '—' "$f" | wc -l) * 1000 / $(wc -w < "$f") ))

# UK spellings
grep -noiE '\b(defence|modelling|organisation|behaviour|analyse)\b' <file>

# Relative links that point at missing files
python3 - <<'EOF'
import re, os, glob
for f in glob.glob('**/*.md', recursive=True):
    for u in re.findall(r'\]\(([^)\s]+)\)', open(f, encoding='utf-8').read()):
        if re.match(r'(https?:|mailto:|#)', u): continue
        p = os.path.normpath(os.path.join(os.path.dirname(f), u.split('#')[0]))
        if not os.path.exists(p): print(f, u)
EOF
```

## When asked to review a document

Work out the document type from its path and apply the matching section above. Report findings without editing the file:

- **Blocking:** breaks a rule above. Examples: process references in a white paper, an uncited factual claim, a broken link, code that doesn't run, a missing test, template text left in, or a PR with no linked issue or approved RFC.
- **Should fix:** weakens the document. Examples: machine-sounding prose, missing scope, an unversioned spec, or a secondary source where a primary one exists.
- **Nit:** style and consistency.

For each finding, give the file and line, quote the offending text, and suggest a replacement. For citations, say whether you opened the source and checked that it supports the claim, or only checked that the URL resolves.

## Repository skills

Summon-only skills live in `skills/` (see `skills/README.md`): `cosai-ws4-meeting-agenda` and `cosai-ws4-issue-triage`. Use them only when the user names them.

# Contributing

Thank you for your interest in contributing to the Secure Design Patterns for Agentic Systems workstream. This guide outlines the process for proposing new work and submitting contributions.

## Repository Structure

This repository contains:
- `Charter.md` - TSC and PGB approved charter
- `SIGs/` - Special Interest Group subgroups with approved charters
- `RFCs/` - Approved topics for community work
- `whitepapers/` - TSC and PGB approved whitepapers
- `practical-guides/` - Practical guides, code examples, and cookbooks

## RFC Process

All new work must be approved through the Request for Comments (RFC) process:

1. **Submit RFC**: Create a [new GitHub issue](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/new?template=rfc-template.md) with the `rfc` label. This will automatically mark it as `In Review`. You can find the [template here](rfc-template.md).

2. **Notify Community**: Post notifications on:
   - Slack channel to [#ws4-secure-design-agentic-systems](https://cosai-op.slack.com/archives/C08ET0T8L57)
   - WS4 [mailing list](mailto:cosai-agentic-systems-ws@lists.oasis-open-projects.org)

3. **Present RFC**: Time will be allocated to present your RFC at the next available meeting.

4. **Community Review**: After presentation, at least one additional week will be provided for community feedback.

5. **Vote**: The RFC will be placed for a vote prior to the next meeting. Note that we seek contributions that have broad community interest and support from at least two participating member organizations.

6. **Approval**: Approved RFCs will be:
   - Marked as `Approved` in GitHub
   - Committed to the `RFCs/` folder with an RFC number corresponding to the originating issue number

## Pull Request Guidelines

- **Required Reference**: Each pull request must address either:
  - An open issue (non-RFC), or
  - An approved RFC
  
- **Unlinked PRs**: Pull requests not addressing an RFC or issue may be marked and closed.

## Working with WS4 tooling

Repeatable PM tasks (meeting agendas, issue triage) are defined under [`skills/`](skills/) — one self-contained `<skill>/SKILL.md` folder per task, installable with the `skills` CLI and usable with any LLM assistant. Workstream specifics (repo, leads, cadence, recognised labels, milestones) live in tables inside each definition. Meeting minutes are synced out-of-band by `scripts/fetch_meeting_minutes.py` (setup in [`scripts/README.md`](scripts/README.md)); agenda drafts land in `agenda_drafts/` for chair review.

## Questions?

If you have questions about the contribution process, please reach out through our Slack channel or mailing list.

## AI Usage Policy

This workstream produces guidance for *secure* agentic systems, so we hold
contributions made with AI assistance to the same standard we ask others to
hold theirs. AI tools are welcome — many maintainers use them — but the
following rules apply to every contribution, regardless of who submits it.

This policy operates within the framework of the [OASIS CoSAI AI Usage Guidelines](https://github.com/cosai-oasis/oasis-open-project/blob/main/AI-USAGE-GUIDELINES.md),
which set the baseline for all CoSAI workstreams. Where this document is
more specific, it adds workstream-specific expectations on top of that
baseline; where it is silent, the parent guidelines govern.

### Engagement before contribution

This workstream's effort is directed by approved RFCs and prioritized issues.
Contributions are welcome when they land within work the working group has
already scoped and agreed to — not as unsolicited proposals dropped into the
PR queue.

Unsolicited "drive-by" pull requests, large code or document donations not
linked to an approved RFC, and AI-assisted contributions submitted without
prior engagement on the issue tracker, mailing list, or Slack channel may be
closed without review. This applies regardless of how the work was produced;
AI tools make it inexpensive to generate volume, which makes alignment with
the working group's scope the load-bearing step, not the writing.

If you have an idea you want to contribute, start by:

1. Opening an issue or [RFC](rfc-template.md) describing the problem and
   proposed approach.
2. Engaging on the [Slack channel](https://cosai-op.slack.com/archives/C08ET0T8L57)
   or [mailing list](mailto:cosai-agentic-systems-ws@lists.oasis-open-projects.org)
   so the working group can weigh in *before* substantial work is invested.

This is the same expectation the [Pull Request Guidelines](#pull-request-guidelines)
above set for all contributions; we restate it here because AI assistance
changes the economics of producing PRs, not the economics of reviewing them.

### Disclosure

This workstream follows the CoSAI-wide convention for attributing AI
assistance, originating from
[secure-ai-tooling#149](https://github.com/cosai-oasis/secure-ai-tooling/issues/149):

- **Use the standard vendor-neutral trailer in commit messages** when a
  commit was produced with AI assistance:

  ```
  Co-authored-by: AI Assistant <ai-assistant@coalitionforsecureai.org>
  ```

  This matches the existing `Co-authored-by:` convention for human
  collaborators. Naming specific AI vendors or models in commit attribution
  is discouraged — see the linked issue for rationale (avoiding the
  appearance of endorsement or friction in a multi-org coalition).

- **For substantial AI assistance** — for example, AI drafted a section,
  generated structured content, or produced more than a brief edit —
  additionally describe the assistance in the PR or issue body: what the
  tool helped with and at what stage of drafting. This is consistent with
  the OASIS CoSAI AI Usage Guidelines' call for transparency about
  substantial use of AI systems.

- A `prepare-commit-msg` hook for adding the trailer automatically is
  documented in
  [secure-ai-tooling#149](https://github.com/cosai-oasis/secure-ai-tooling/issues/149).

### Human accountability

- **You must understand what you submit.** If you cannot explain what your
  contribution says or does, and how it fits into the surrounding work,
  without the aid of an AI tool, do not submit it. Reviewers will ask, and
  the workstream relies on contributors being able to defend their reasoning.
- **Human-in-the-loop review is required for AI-assisted text.** Any AI-drafted
  prose in issues, discussions, or PRs must be read and edited by a human
  before submission. AI output tends toward verbosity and surface plausibility;
  trimming and verification are the contributor's responsibility.
- **Treat AI output as a starting point, not a finished artefact.** Per the
  [OASIS CoSAI AI Usage Guidelines](https://github.com/cosai-oasis/oasis-open-project/blob/main/AI-USAGE-GUIDELINES.md),
  substantial use of AI in drafting is expected to be iterative — multiple
  rounds of human review and refinement before submission, not a single-pass
  paste from a generation tool.

### Scope and limits

- **Text and code only.** AI-generated images, diagrams, audio, or video are
  not accepted. Diagrams should be hand-authored (e.g. Mermaid, draw.io,
  hand-drawn) so that the design intent is auditable.
- **Choice of tools.** CoSAI does not endorse or require any specific AI
  vendor. Editors are encouraged to vary tools across contributions, both to
  avoid the appearance of favoring a single vendor and to keep the
  workstream's outputs from depending on any one tool's idiosyncrasies.

### Intellectual property

- **You are responsible for the IP status of what you contribute.** It is
  the contributor's responsibility to confirm that any AI-generated content
  they submit may be redistributed under this repository's licenses
  (CC-BY 4.0 for documents, Apache 2.0 for code) and donated to OASIS under
  the [OASIS Open Projects rules](https://www.oasis-open.org/policies-guidelines/open-projects-process/).
  Contributors should prefer reputable AI systems with clear terms regarding
  output ownership and training-data provenance.

### Why this policy exists

This is a public OASIS Open Project producing security guidance that
downstream users will rely on. Low-effort, AI-generated submissions push
review burden onto maintainers and undermine the workstream's credibility.
The bar is not "no AI" — it is "a human who understands the work, and who
has engaged with the working group on what's worth doing, stands behind
every contribution."

*This policy draws on the [Ghostty project's AI Usage Policy](https://github.com/ghostty-org/ghostty/blob/main/AI_POLICY.md)
as prior art, with thanks; it has been adapted for the OASIS open-standards
context and the specific governance of this workstream.*


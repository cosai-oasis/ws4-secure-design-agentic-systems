---
title: "WS4 — State of the Workstream: deliverables and target timelines (revised)"
audience: CoSAI TSC
meeting: 2026-09-08 TSC (1:00–2:00 PM ET) — workstream standup (#49) and scope/roadmap reassessment (#52)
presenter: Sarah Novotny and Ian Molloy
supersedes: agenda_drafts/ws4/2026-09-01-tsc-report.md
source: WS4 2026-09-03 — Gemini notes, chat log, attendance, and a full machine transcript of the
  recording (local Whisper; no diarization); TSC minutes 2026-09-01; TSC agenda 2026-09-08;
  repo issue/PR state as of 2026-09-08
---

# WS4 — State of the Workstream (revised for 2026-09-08)

**Why this exists:** this revises the 2026-09-01 report against the 2026-09-03 WS4 call.
Today's TSC runs the end-of-term workstream standup ([#49](https://github.com/cosai-oasis/cosai-tsc/issues/49))
and the scope/goals/roadmap reassessment ([#52](https://github.com/cosai-oasis/cosai-tsc/issues/52)),
so this is the view the incoming co-chairs inherit.

> **On the quotations.** Quotes below come from a *machine* transcript of the 2026-09-03 recording
> (local Whisper, no speaker diarization; speakers attributed by cross-referencing the Gemini notes,
> chat log and attendance). They are verbatim against that transcript and the sense is unambiguous,
> but if any quote attributed to another person is going to be read aloud to the TSC, confirm it
> with them first. Full transcript: `meeting_minutes/ws4/WS4-20260903-transcript.md` (local only).

**The headline has changed.** A week ago WS4 had one owner-confirmed date and six TBDs.
It now has **three dated deliverables and a named editor on the containment paper** — but the
TSC deliverables roadmap **still carries exactly one WS4 row**. The §5 rows from the Sep 1
report were never added.

---

## 1. What changed since 2026-09-01

| Item | Was (Sep 1) | Now (Sep 8) |
|---|---|---|
| **Containment follow-on** ([#172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172)) | Owner TBD, date TBD, placement unresolved | **Jeff Leva (@Levaj2000) is Editor**; skeleton [PR #181](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/181) open (+340 lines, all 21 scope questions mapped to sections); **three dates set** |
| **Agent Credentials paper** | Late September 2026, owner-confirmed | **Slipped to October 2026** — Benedict Lau reported a slight delay on 2026-09-03 |
| **Multimodal threat taxonomy** | Draft date TBD | **Late October 2026**, Shriti Priya, modality-agnostic taxonomy — but she had not yet consulted her team |
| **Observability** ([#175](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/175)) | Blocked on "top-level category or subcategory?" | **Question is moot.** Emrick Donadei found the existing `AuditRecordRepository` component already covers semantic observability and proposes **withdrawing the RFC**, reframing the behavioral half as a *control* |
| **ADLC definitional / landscape paper** | Emrick Donadei drafting; SIG P0 | **Authorship vacant.** I corrected this live on 2026-09-03: Emrick is the ADLC **SIG lead**, which is where I had anchored the paper's lead. The pen is Parul Singh's, and she has moved on |
| **Containment placement** | Open ask to the TSC | **Resolved** — broad WS4 workstream, not the ADLC SIG |
| **Agent Credentials ↔ WS1** | Open ask to the TSC | **Resolved 2026-09-01** — TSC declined to fold the group; work product incorporates WS1 findings, schemas being defined with OCSF |
| **MCP risk-map decomposition** | Not tracked as a commitment | Now a named review commitment ([#178](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/178)) — 76 entries awaiting WS4 SME review |
| **Trust Graph** | Absent from the report entirely | Surfaced on the call as **a WS4 group** — biweekly, co-chaired, no draft yet. See §4.5 |

> **Correction to the Sep 1 report.** Its lead ask — "is Observability a top-level CoSAI-RM
> category or a subcategory under Application?" — was already superseded when I presented it.
> Emrick Donadei posted the `AuditRecordRepository` finding at 01:54 UTC on Sep 1, hours before
> the call. The decision the TSC actually needs is in §4, and it is a smaller one.

---

## 2. Shipped

| Deliverable | Evidence | On TSC roadmap? |
|---|---|---|
| **MCP Security Whitepaper V2** | PR [#141](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/141) merged 2026-08-12 | ❌ **Still not listed** |
| **Agentic Isolation blog** — *"Treat Your Agent Like an Insider Threat"* | PR [#167](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/167) merged 2026-08-25; live on coalitionforsecureai.org | ✅ Row 6, 🟢 Complete |

> **Accuracy flag on the published blog.** Working Q21 of the containment scope questions,
> Jeff Leva read the primary disclosures and found the post conflates two separate intrusions:
> the JFrog Artifactory CVEs and the Hugging Face data-pipeline compromise are different events
> with different vulnerability sets. This affects §6 of the follow-on paper and probably warrants
> a correction to the live post. Detail in [#172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172).

---

## 3. In flight — nine items

Ordered by how close each is to landing. Dated items first.

| # | Deliverable | Owner | Stage | Target | Confidence |
|---|---|---|---|---|---|
| 1 | **Containment follow-on paper** ([#172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172), [PR #181](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/181)) | **Jeff Leva** (@Levaj2000), Editor. Contributors: John Cavanaugh (@Johncavanaugh-IIS, research synthesis), **Jason Bowman** (security + RL-agent background, introduced by Kevin Calloway; attended 2026-09-03, needs Slack access and an intro to Jeff). TSC reviewers: Akila Srinivasan (@Akilsrin), David LaBianca (@davidlabianca), Jodi Middleton | Skeleton PR open; contributions land by PR against a section | **Contributions 2026-10-08 · first draft to TSC reviewers 2026-10-15 · review-ready 2026-10-29** | Editor-set, dated in writing |
| 2 | **Agent Credentials paper** | Benedict Lau (@benhylau), Rithikha Rajamohan (@rithikha) | Drafting by section; OCSF schema definition underway | **October 2026** — early draft skeleton for broader review | Owner-stated; **day not fixed** |
| 3 | **Multimodal threat taxonomy** ([#113](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/113)) | Shriti Priya (@monshri) | Resolving ambiguities; modality-agnostic taxonomy | **Late October 2026** — refined draft for review | Owner-stated, *not* team-confirmed: *"I haven't talked to my team members"* |
| 4 | **MCP risk-map decomposition review** ([#178](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/178)) | WS4 SMEs; David LaBianca (@davidlabianca) driving | [secure-ai-tooling#507](https://github.com/cosai-oasis/secure-ai-tooling/pull/507): 46 new + 30 updated entries. Controls 37→67, risks 36→52. Review **against V1** to prevent scope creep | **TBD** — needs volunteers for discrete chunks | Blocked on reviewer capacity |
| 5 | **Observability CoSAI-RM component** ([#175](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/175), [PR #501](https://github.com/cosai-oasis/secure-ai-tooling/pull/501)) | Emrick Donadei (@edonadei) | **Rescoping.** Semantic half already covered by `AuditRecordRepository`; behavioral half (baselines, drift and tool-usage anomaly detection, circuit breakers, kill switches, escalation gates) to be reframed as a control. PR #501 still draft. Second, quieter blocker: David LaBianca serialises contributors to the risk map — *"I can only have so many people in queue to modify the same space at any one time"* — and WS2's telemetry work is ahead of ADLC in that queue | **TBD** — pending the §4.1 confirmation | Small decision, then days |
| 6 | **ADLC lifecycle definitional / landscape paper** | **Vacant** | Nobody holds the pen and **the paper itself is unwritten** — I checked the ADLC Drive folder and the repo. Emrick Donadei leads the *SIG*, not this paper; the 2026-09-03 agenda listed him as owner and I corrected it on the call. The doc offered on the call when Raymond Sheh asked for this paper was *ADLC Risks and Controls* — a different deliverable, which is why he was confused | **TBD — cannot be set without an author** | Blocked |
| 7 | **ADLC risks and controls** | ADLC SIG | 30–40 risks identified | **Overdue** — end of August, missed | Blocked on SIG leadership and #5 |
| 8 | **MCP Security V2.x residuals** ([#163](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/163)) | Chairs | Two items: one editorial, one needing a chair call on citing a pre-release OWASP document normatively | **TBD** | Chairs; no movement since 2026-08-12 |
| 9 | **Trust Graph** | Co-chaired, incl. Rithikha Rajamohan (@rithikha) and Kapil Singh (@ksingh299) | Meets alternate Thursdays, 09:30–11:00 ET. Hypergraph representation of delegation and agent state. Two documents exist but are thin — a **172-word** white-paper stub and a 654-word scoping note; the substance is still on a Miro board. Distinct from Agent Credentials, with acknowledged overlap: *"we constantly talk about whether we should be combining into one effort"* | **None set** | Not previously reported to the TSC (§4.5) |

*Handles are given where the mapping is evidenced — by a GitHub profile name, or by authorship of
the RFC or PR in question. **Jason Bowman, Kevin Calloway, Jodi Middleton and Teryl Taylor are named
without handles because I could not confirm theirs**; they are the gaps to fill before anyone is
assigned in GitHub.*

### Where each deliverable lives

Assembled by walking the WS4 Drive and the repos, because no single index exists (§4.5). Word
counts are of the live drafts as of 2026-09-08 — they are the honest measure of how far each
deliverable actually is, and in two cases they are well ahead of what was reported verbally.

| Deliverable | Issue | Draft |
|---|---|---|
| MCP Security Whitepaper V2 | [#163](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/163) (residuals) | [`whitepapers/model-context-protocol-security.md`](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/whitepapers/model-context-protocol-security.md) — shipped |
| Agentic Isolation blog | — | [`blogs/sandbox-now.md`](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/blogs/sandbox-now.md) — shipped |
| Containment follow-on | [#172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172) | [PR #181](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/181) → `whitepapers/agent-containment.md`, 340-line skeleton |
| Agent Credentials paper | [#99](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/99) — RFC **accepted**, issue closed | [Agent Credentials White Paper (Draft)](https://docs.google.com/document/d/1ILDtbNJw_1GCj6V9uXaDgMLGKQJR9JJqUNWMef9Vamk/edit)[^access] — **12,243 words**, updated 2026-09-03 |
| Multimodal threat taxonomy | [#113](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/113) | [RFC: v1Draft Multimodal Agentic Security](https://docs.google.com/document/d/1_71VIIOl2Nas16U-aXo6t1Y7sz71w6zeYC7jwdTweiA/edit)[^access] — **12,250 words**, updated 2026-09-03 |
| MCP risk-map review | [#178](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/178) | [secure-ai-tooling#507](https://github.com/cosai-oasis/secure-ai-tooling/pull/507) — 76 entries |
| Observability component | [#175](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/175) | [secure-ai-tooling#501](https://github.com/cosai-oasis/secure-ai-tooling/pull/501) — still draft |
| ADLC risks and controls | SIG chartered by [#97](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/97) | [ADLC Risks and Controls](https://docs.google.com/document/d/16rb7h2y4FYu2tDsgVRA3HfUlXYEM0scVnQneCkB30SM/edit)[^access] — **25,466 words**, updated 2026-08-19 |
| ADLC lifecycle definitional paper | [#97](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/97) (SIG scope, accepted) | **the paper itself is unwritten.** Nearest material is [`SIGs/ADLC/adlc-scope-doc.md`](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/SIGs/ADLC/adlc-scope-doc.md) — the SIG's *scope*, not the definitional paper, and by the same departed author |
| Trust Graph | **none** — the only one genuinely untracked | [Trust Graph White Paper](https://docs.google.com/document/d/14ySBvzyC7sdXg6H0d8zCfgkVdy6kDbMuu0wLQUdywyE/edit)[^access] — 172 words; [Proposal Scoping](https://docs.google.com/document/d/1nISpW50DFNe0-24LG5JksgzCg8vK374fzjbjbaThv_s/edit)[^access] — 654 words |

**Two things this table says that the status updates did not.**

First, **Agent Credentials and Multimodal are both sitting on ~12,000-word drafts.** Both were
described on the call as very early — "a very early skeleton," "very early stages of drafting."
The October and late-October dates are better supported than the verbal reports suggested.

Second, **the ADLC SIG has written the downstream artifact and not the upstream one.** Risks and
controls is 25,000 words; the definitional paper that is supposed to precede it does not exist.
That inverts the sequencing the SIG itself agreed — get the lifecycle paper out *before* the risks
land in the CoSAI-RM. It is the strongest argument for ask 4.3.

**A correction to my own first pass.** I initially recorded four of these as having no GitHub issue.
That was wrong: Agent Credentials has an **accepted** RFC ([#99](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/99), closed as completed,
eight named authors across EQTY Lab, IBM, Microsoft, Zscaler, Dell/AGNTCY and Cisco) and the ADLC SIG
was chartered by an accepted RFC ([#97](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/97)) whose scope doc is committed. Only **Trust
Graph** is genuinely untracked. The tracking is better than I first reported — it is the *index* that
is missing, not the records.

**One real process gap, though.** `CONTRIBUTING.md` says approved RFCs are committed to `RFCs/` with
the originating issue number. `RFCs/` holds only `RFC-6.md` and `RFC-50.md` — accepted RFCs
[#99](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/99) (Agent Credentials) and [#113](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/113) (Multimodal) never landed there,
so two of our largest drafts have no in-repo anchor.

**And the departure cost is larger than "the SIG lost leads."** Parul Singh (@husky-parul) authored the ADLC SIG
scope doc (#97), the accepted Trust-Aware Dataplane RFC ([#50](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/50), committed as
`RFCs/RFC-50.md` and now unattended), the open Identity Architecture Patterns playbook
([PR #116](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/116)), and was leading the ADLC definitional paper. One reassignment orphaned four
artifacts across three deliverables. That is the concrete version of ask 4.2 and 4.3.

### RFCs under review — not deliverables until accepted

- **[#170](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/170) Decommissioning as ADLC phase / lifecycle stage 9** (Bill Stout, @billbrietstout). *Converging.* Imran Siddique (@imran-siddique) proposed dropping the soft/hard split entirely on 2026-09-03, with a definition the thread is coalescing on: *"Decommissioning ends the agent's authority to act; whether it can come back later is a policy choice."* Raymond Sheh (@raymondsheh) added wider-system dependency and institutional-knowledge risks. **A resolution path emerged on 2026-09-03**: put decommissioning into the definitional paper *as a phase* so that risks have somewhere to attach — Bill Stout's *"there is need of place to land."* That converts David LaBianca's sequencing objection into another dependency on item 6 above, rather than a standing disagreement.
- **[#149](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/149) Agent Manifest** (Imran Siddique, @imran-siddique), Phase 2. The GitHub issue is quiet since 2026-08-27, but the work moved elsewhere: the Agent Credentials group spent its 2026-09-03 call deciding **whether an agent manifest is evidence or a credential**, and took an action to meet with Imran to settle manifests and traces. Expect #149's fate to be decided inside the Agent Credentials paper rather than as a standalone RFC.

### Cross-workstream commitments

- **WS2 Telemetry for AI Systems** — Josiah Hagen (@jo5iah) presented the roadmap to WS4 on 2026-09-03.
  WS4 feedback due **2026-09-14** via GitHub issues or PRs; he wants TSC co-chair review the week
  of **2026-09-15**. Document: [`ws2-defenders/telemetry/CoSAI-AI-Telemetry-RFC.md`](https://github.com/cosai-oasis/ws2-defenders/blob/main/telemetry/CoSAI-AI-Telemetry-RFC.md). Anyone doing OCSF or OpenTelemetry work must align to **Appendices D and E**.
  Worth the TSC's attention: WS4's MCP decomposition **shrank that paper's ask on the CoSAI-RM to
  three risks and one control** — the two workstreams' outputs are already interlocking as intended.
  This discharges my open TSC action on the telemetry documentation request; I can close the issue.
- **WS2 [Zero Trust for AI Systems](https://github.com/cosai-oasis/ws2-defenders/blob/main/zero-trust/Zero%20Trust%20for%20AI%20Systems.md)** — Josiah flagged it in chat as required reading for the
  containment authors; it was pending PGB approval on 2026-09-03 and publishes imminently.
  Vocabulary alignment between it and the containment paper is cheaper now than after both ship.
- **ODIS** — readout and discussion scheduled for the **2026-09-10** WS4 call.

---

## 4. What WS4 needs from the TSC — five asks

**4.1 Confirm the Observability reframe.** Not the question I brought on Sep 1. The ask now:
agree that RFC #175 is **withdrawn** and the behavioral piece is refiled as a *control* against the
existing `AuditRecordRepository` component. This is a chairs-and-RM-SIG call, it costs one comment,
and it unblocks ADLC risk drafting for the Runtime and Reflection phases.

**4.2 ADLC SIG leadership — open since 2026-08-27.** One correction to today's agenda, which
says the SIG has *no* co-chairs: it has **one and a half, down from four** — Emrick Donadei is still
serving. The gap is real but it is a thinning, not a vacancy, and a couple of people have already
approached me. TSC action [#63](https://github.com/cosai-oasis/cosai-tsc/issues/63) sits with Ian
and me, but WS4 cannot staff it from inside; this needs member organisations to nominate.
*(Today's agenda item 4.)*

**4.3 An author for the ADLC definitional paper — separate from 4.2.** Even with new co-chairs,
this paper needs a named pen, and it is not the SIG lead's by default — that conflation is one I
made myself on the agenda and corrected on the 2026-09-03 call. It is the foundational document
that the decommissioning RFC (#170), the risks-and-controls set, and the CoSAI-RM integration all
sequence behind. It is the single largest unowned dependency in the workstream — and one of four
artifacts a single reassignment orphaned, itemised at the end of §3.

**4.4 Add the §5 rows to the roadmap — repeating last week's ask.** WS4 shipped two major
deliverables in August; the roadmap shows one blog post. If today's reassessment (#52) judges
workstream scope from the roadmap as it stands, WS4 is assessed on roughly a tenth of its output.

**4.5 For agenda item 1, the scope reassessment — WS4's real problem is not scope, it is that
nobody holds the map.** I said this out loud on the 2026-09-03 call: *"I need a better intersecting
group of who's working on which things and how many different things inside workstream 4 are
happening, because I'm not keeping track."* Trust Graph is the proof — an active WS4 group, meeting
fortnightly, that appears in none of my own reporting until this document. The instrument already
exists: Jeff Leva has an **interop document** mapping Agent Credentials, Trust Graph, OCSF and the
layers each owns, and offered to reshare it. My proposal for the reassessment is that each
workstream produces exactly that — an owned map of its internal efforts, refreshed per co-chair
term — rather than a scope renegotiation. WS4 does not need a narrower remit; it needs its remit
written down in one place.

---

## 5. Rows for `TSC Deliverables/roadmap.md`

Copy-paste ready. Continues Active Deliverables numbering from row 6. Stage glyphs use the
roadmap's own legend — blocked states are described in Next Milestone rather than given a new glyph.

### Active Deliverables

| # | Deliverable | Workstream / SIG | Current Stage | Next Deadline | Next Milestone |
|---|---|---|---|---|---|
| 7 | MCP Security Whitepaper V2 | WS4 — Secure Design Patterns for Agentic Systems | 🟢 Published / Complete | 2026-08-12 | Published; V2.x residuals tracked in #163 |
| 8 | Containment Follow-on Paper | WS4 — Secure Design Patterns for Agentic Systems | 🔵 In Progress | 2026-10-15 | First draft to TSC reviewers; contributions close 2026-10-08 |
| 9 | Agent Credentials Paper | WS4 — Agent Credentials Group | 🔵 In Progress | 2026-10-31 | Early draft skeleton for broader review (October; day not fixed) |
| 10 | Multimodal Threat Taxonomy | WS4 — Multimodal Agentic Security Group | 🔵 In Progress | 2026-10-31 | Refined modality-agnostic taxonomy draft for review |
| 11 | MCP Risk Map Decomposition Review | WS4 — Secure Design Patterns for Agentic Systems | 🔵 In Progress | TBD | SME review of secure-ai-tooling#507 (76 entries); needs volunteers (#178) |
| 12 | ADLC Lifecycle Definitional Paper | WS4 — SIG ADLC | 🔵 Planned | TBD | Blocked: paper has no author (SIG lead ≠ paper owner) |
| 13 | ADLC Risks and Controls | WS4 — SIG ADLC | 🔵 In Progress | Overdue (end of Aug) | Blocked on SIG leadership and the Definitional Paper |

### Papers & Points of View

| Title | Workstream / SIG | Owner | Start Date | Target Date | Status | Issue |
|---|---|---|---|---|---|---|
| MCP Security Whitepaper V2 | WS4 | Sarah Novotny (@sarahnovotny), Ian Molloy (@imolloy) | | 2026-08-12 | 🟢 Published / Complete | [#141](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/141) |
| Containment Follow-on Paper | WS4 | Jeff Leva (@Levaj2000, Editor) | 2026-08-25 | 2026-10-29 | 🔵 In Progress | [#172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172) |
| Agent Credentials Paper | WS4 | Benedict Lau (@benhylau), Rithikha Rajamohan (@rithikha) | | 2026-10-31 | 🔵 In Progress | *no issue; [draft](https://docs.google.com/document/d/1ILDtbNJw_1GCj6V9uXaDgMLGKQJR9JJqUNWMef9Vamk/edit)[^access]* |
| Multimodal Threat Taxonomy | WS4 / Multimodal Agentic Security | Shriti Priya (@monshri) | | 2026-10-31 | 🔵 In Progress | [#113](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/113) |
| ADLC Lifecycle Definitional Paper | WS4 / SIG ADLC | **Unowned** | | TBD | 🔵 Planned | *no issue, no draft* |

### Blog Posts

Row 1 is present and correct. A factual correction may follow — see §2.

---

## 6. Three-minute talk track

If time collapses, say points 1, 4 and 5 and point at this document — the dates are written
down, the two structural asks are not.

1. **Since last week WS4 went from one date to four.** Containment has an editor — Jeff Leva
   volunteered on Thursday's call, and by Saturday had declared himself Editor and opened a
   skeleton PR with all 21 scope questions mapped to sections and three dates attached. Agent
   Credentials is October, Multimodal is late October.

2. **One slip, honestly reported — and the drafts are further along than the updates suggest.**
   Agent Credentials moved from late September to October; Benedict called it a slight delay. But
   both it and the multimodal taxonomy are sitting on ~12,000-word drafts, and ADLC risks and
   controls is at 25,000. §3 links every one of them. The dates are better supported than the
   verbal "very early" reports implied.

3. **Two of last week's four asks are closed** — containment sits in the broad workstream, not the
   ADLC SIG, and you decided Agent Credentials stays in WS4 while absorbing WS1's findings. Thank
   you; both unblocked real work.

4. **The remaining problem is ADLC, and it is two problems, not one.** Correct today's agenda on
   one point — the SIG has one and a half co-chairs, not none. The deeper issue is that one
   reassignment orphaned four artifacts: the ADLC scope doc, an accepted RFC, an open playbook PR,
   and the unwritten definitional paper. That paper is what risks-and-controls, the decommissioning
   RFC and the CoSAI-RM integration all sequence behind — and the SIG has written 25,000 words of
   the downstream artifact while the upstream anchor sits empty. New co-chairs, that is the
   highest-leverage thing you can staff.

5. **On agenda item 1: don't renegotiate our scope, make us map it.** I found a WS4 group last
   Thursday — Trust Graph, meeting fortnightly — that appears in none of my own reporting. That is
   not a scope problem, it is a bookkeeping one, and every workstream likely has it. Jeff Leva
   already built the instrument: an interop doc showing who owns which layer. Ask each workstream
   for that, once a co-chair term.

6. **And the roadmap still shows one WS4 row.** I brought rows last week; they were not added. If
   today's reassessment reads scope off the roadmap, WS4 looks like a blog post. §5 is copy-paste ready.

[^access]: These are CoSAI working documents in Google Drive and are not open to the public. If the link asks for access, that is expected — request it by joining the workstream rather than by requesting the file. Start with the [CoSAI onboarding guide](https://github.com/cosai-oasis/oasis-open-project/blob/main/ONBOARDING.md), which covers the mailing lists, meeting invitations and Slack; workstream membership is what grants document access.

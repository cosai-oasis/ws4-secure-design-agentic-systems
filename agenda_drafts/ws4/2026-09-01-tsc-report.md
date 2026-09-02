---
title: "WS4 — State of the Workstream: deliverables and target timelines"
audience: CoSAI TSC
meeting: 2026-09-01 TSC (1:00–2:00 PM ET), agenda item 8
presenter: Sarah Novotny (Ian Molloy away)
source: WS4 minutes 2026-08-27; TSC minutes 2026-08-25; repo issue/PR state as of 2026-09-01
---

# WS4 — State of the Workstream

**Why this exists:** the 2026-08-25 TSC scheduled a workstream standup for today, and
the 2026-08-27 WS4 call took an action on the group to "outline upcoming project
deliverables and target timelines to present at the September 1 meeting."

**The headline:** the TSC deliverables roadmap carries **one** WS4 row — the agentic
isolation blog, marked complete. WS4 shipped a second major deliverable that never
appeared on the roadmap at all, and has seven more in flight. §4 supplies the rows.

---

## 1. Shipped

| Deliverable | Evidence | On TSC roadmap? |
|---|---|---|
| **MCP Security Whitepaper V2** | PR [#141](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/141) merged 2026-08-12; publication and social distribution reported to WS4 on 2026-08-27 | ❌ **No — never listed** |
| **Agentic Isolation blog** — *"Treat Your Agent Like an Insider Threat: Why AI Sandboxing Can't Wait"* | PR [#167](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/167) merged 2026-08-25; **verified live** on coalitionforsecureai.org, dated 2026-08-25 | ✅ Row 6, 🟢 Complete |

> Correction for the record: the 2026-08-27 WS4 minutes say the blog is "awaiting
> marketing committee posting." That was already stale when recorded — the post went
> live on the CoSAI site on Aug 25. No marketing action is outstanding on publication;
> promotion copy is.

---

## 2. In flight — seven deliverables

Ordered by how close each is to landing.

| # | Deliverable | Owner | Stage | Target | Who owes the date |
|---|---|---|---|---|---|
| 1 | **Observability as a CoSAI-RM component** ([#175](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/175)) | Parul Singh, Emrick Donadei | RFC filed; implementation PR [secure-ai-tooling#501](https://github.com/cosai-oasis/secure-ai-tooling/pull/501) **written and validating green** | **~1 hour** after one decision; +1 day for the 8-risk catalog | Blocked on TSC/chairs — see §3 |
| 2 | **ADLC risks and controls** | ADLC SIG | 30–40 risks identified | End of August — **now passed** | ADLC SIG; leadership gap is the cause (§3) |
| 3 | **Agent Credentials paper** | Rithikha Rajamohan, Ben | Drafting by section; definitions consensus reached 2026-08-27 | **Late September 2026** — first draft | ✅ Owner-confirmed 2026-08-27 |
| 4 | **Multimodal threat taxonomy** | Multimodal Agentic Security group (Shriti Priya, Raymond Sheh, Kevin) | Scope agreed 2026-08-24: **taxonomy, not mitigations**; 7-layer agentic stack mapped | Scope finalisation targeted for w/c 2026-08-24; draft date TBD | Group to set at next weekly |
| 5 | **ADLC lifecycle definitional ("anchor") paper** | Emrick Donadei | Drafting; **set as the ADLC SIG's P0 on 2026-08-27**, ahead of containment | **TBD** | Emrick Donadei holds an open action to set it |
| 6 | **Containment follow-on paper** ([#172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172)) | Chairs + volunteer authors. TSC reviewers named 2026-08-25: **Akila Srinivasan, David LaBianca, Jodi Middleton** | Scoping — 21 scope questions banked from the blog review | **TBD** — next milestone is an outline with named section owners | Chairs, once placement resolves (§3) |
| 7 | **MCP Security V2.x residuals** ([#163](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/163)) | Chairs | Two items: one editorial, one needing a chair decision on citing a pre-release OWASP document normatively | **TBD** | Chairs |

**Two RFCs under review that are not yet deliverables** — they become deliverables if accepted:

- [#170](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/170) **Decommissioning as ADLC phase / lifecycle stage 9** (Bill Stout). Rescoped to hard decommissioning only. David LaBianca objects to adding a phase before ADLC publishes foundational docs — unresolved, needs a chair call.
- [#149](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/149) **Agent Manifest** (Imran Siddique), Phase 2. Next: integration diagram, and reconciling the verifier/trace architecture with Raghuram Yeluri. May fold into Agent Credentials (#3 above).

---

## 3. What WS4 needs from the TSC — four asks

1. **Unblock Observability (RFC #175, question 1).** Is Observability a **top-level
   CoSAI-RM category** or a **subcategory under Application**? The implementation branch
   is written and passes every corpus check; it waits only on this. Roughly fifteen
   observability risks currently have no correct home, and ADLC risk drafting for the
   Runtime and Reflection phases is blocked behind it. This is the same live blocker
   as **today's agenda item 3** (#50, CoSAI-RM component rework).

2. **ADLC SIG leadership.** Two leads stepped back for work reasons. The SIG paused RFC
   work pending a check-in with the WS4 chairs. This is the direct cause of the missed
   end-of-August risks deadline. *(Today's agenda item 9.)*

3. **Where does the containment follow-on live?** The ADLC SIG is a **process** working
   group; a technical how-to containment paper is an **implementation** artifact.
   Raghuram Yeluri and I both flagged the mismatch on 2026-08-27. WS4's position: ADLC
   focuses on the definitional lifecycle paper, and a broader workstream owns the
   containment follow-on plus its technical playbooks. Confirming that placement lets
   the named reviewers start.

4. **Agent Credentials ↔ WS1 consolidation.** Kapil and Nicolai Nielsen proposed merging
   parallel verifiable-claims threads to avoid fragmented, piecemeal output; WS1 is
   separately exploring transportable evidence for AI/ML artifacts. This needs
   TSC/OASIS guidance on how to unify rather than a WS4 decision. *(Today's agenda item 10.)*

**Plus one housekeeping ask:** add the rows in §4 so WS4's forward work is visible on the
roadmap ahead of the 2026-09-08 scope and realignment discussion.

---

## 4. Rows for `TSC Deliverables/roadmap.md`

Copy-paste ready. Continues the Active Deliverables numbering from row 6.

### Active Deliverables

| # | Deliverable | Workstream / SIG | Current Stage | Next Deadline | Next Milestone |
|---|---|---|---|---|---|
| 7 | MCP Security Whitepaper V2 | WS4 — Secure Design Patterns for Agentic Systems | 🟢 Published / Complete | 2026-08-12 | Published; V2.x residuals tracked in #163 |
| 8 | Agent Credentials Paper | WS4 — Agent Credentials Group | 🔵 In Progress | 2026-09-30 | First full draft |
| 9 | ADLC Lifecycle Definitional Paper | WS4 — SIG ADLC | 🔵 In Progress | TBD | Emrick Donadei to set timeline |
| 10 | Containment Follow-on Paper | WS4 — Secure Design Patterns for Agentic Systems | 🔵 In Progress | TBD | Outline with named section owners |
| 11 | Multimodal Threat Taxonomy | WS4 — Multimodal Agentic Security Group | 🔵 In Progress | TBD | Taxonomy draft; scope agreed 2026-08-24 |
| 12 | Observability CoSAI-RM Component | WS4 — SIG ADLC | 🔵 In Progress | Blocked | Category-vs-subcategory decision (#175 Q1) |
| 13 | ADLC Risks and Controls | WS4 — SIG ADLC | 🔵 In Progress | Overdue (end of Aug) | 30–40 risks identified; blocked on #175 and SIG leadership |

### Papers & Points of View

| Title | Workstream / SIG | Owner | Start Date | Target Date | Status | Issue |
|---|---|---|---|---|---|---|
| MCP Security Whitepaper V2 | WS4 | Sarah Novotny, Ian Molloy | | 2026-08-12 | 🟢 Published / Complete | [#141](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/141) |
| Agent Credentials Paper | WS4 | Rithikha Rajamohan | | 2026-09-30 | 🔵 In Progress | |
| ADLC Lifecycle Definitional Paper | WS4 / SIG ADLC | Emrick Donadei | | TBD | 🔵 In Progress | |
| Containment Follow-on Paper | WS4 | Sarah Novotny, Ian Molloy | 2026-08-25 | TBD | 🔵 In Progress | [#172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172) |
| Multimodal Threat Taxonomy | WS4 / Multimodal Agentic Security | Shriti Priya | | TBD | 🔵 In Progress | [#113](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/113) |

### Blog Posts

Row 1 is already present and correct; verified live on the CoSAI site 2026-08-25.

---

## 5. Three-minute talk track

WS4 is item 8 of 10 in a 40-minute block. If time collapses, say items 1–3 and point at
this document.

1. **We shipped two things since the last standup, and only one of them is on your
   roadmap.** MCP Security Whitepaper V2 merged Aug 12 and is out. The isolation blog is
   live on the CoSAI site as of Aug 25 — I've verified it.

2. **Seven deliverables in flight. One has an owner-confirmed date:** the Agent
   Credentials paper, first draft late September. The rest are TBD, and I'd rather tell
   you that than give you dates the owners haven't agreed to. The names who owe those
   dates are in the doc.

3. **One decision from this room unblocks the most work.** RFC #175 — is Observability a
   top-level CoSAI-RM category or a subcategory under Application? The code is written
   and green. Fifteen risks have nowhere to live until someone answers, and it's the same
   blocker as agenda item 3.

4. **Two structural problems I can't solve inside WS4:** the ADLC SIG lost two leads, and
   Agent Credentials is running parallel to WS1 on verifiable claims. Both are on today's
   agenda as items 9 and 10.

5. **Ask:** add the §4 rows to the roadmap before the Sep 8 scope conversation, so WS4
   isn't assessed on a single completed blog post.

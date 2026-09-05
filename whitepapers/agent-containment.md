---
title: "Agent Containment: From Sandboxing to Bounded Authority"
author: "Workstream 4: Secure Design Patterns for Agentic Systems"
date: 2026-09-05
version: 0.2-skeleton
status: "Working draft. Not approved. Tracks issue #172."
---

# Agent Containment: From Sandboxing to Bounded Authority

**Title.** Settled with the section 1 frame (2026-09-05): containment is one layer of a bounded-authority model, which is what the title already says. No longer provisional.

**Status:** Working draft, skeleton. Not reviewed, not approved. Follows on from the WS4 blog post *Treat Your Agent Like an Insider Threat: Why AI Sandboxing Can't Wait* (2026-08-25) and takes as its scope the 21 questions banked from that post's review in [issue #172](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/172).

**How to contribute to this draft.** Every section below states what it must answer (the `Qn` references are to #172), who raised the question, what the blog post already says, and what is still open. Add material by pull request against this file, referencing #172. Short contributions in the "Starting material" or "Open items" lists are as welcome as full prose; the editor will unify voice and cut duplication before the first review draft. Drafting notes are in blockquotes and will be removed.

# Table of contents

- [Abstract](#abstract)
  - [Scope](#scope)
  - [Anti-scope](#anti-scope)
  - [Target audience](#target-audience)
- [1. Introduction: from sandboxing to bounded authority](#1-introduction-from-sandboxing-to-bounded-authority)
  - [1.1 Deployment shapes and what containment can mean in each](#11-deployment-shapes-and-what-containment-can-mean-in-each)
- [2. The three hardening axes](#2-the-three-hardening-axes)
- [3. Mediation: the tool call, not the network flow](#3-mediation-the-tool-call-not-the-network-flow)
  - [3.1 The permitted channel is the exfiltration path](#31-the-permitted-channel-is-the-exfiltration-path)
- [4. Composition: per-sandbox controls across a set of agents](#4-composition-per-sandbox-controls-across-a-set-of-agents)
- [5. The enforcement property and four failure modes](#5-the-enforcement-property-and-four-failure-modes)
- [6. Reachability and blast radius](#6-reachability-and-blast-radius)
- [7. Detection and evidence](#7-detection-and-evidence)
  - [7.1 What to log](#71-what-to-log)
  - [7.2 The false-positive profile](#72-the-false-positive-profile)
  - [7.3 Measuring containment](#73-measuring-containment)
- [8. A vetted-sandbox commons](#8-a-vetted-sandbox-commons)
- [9. Positions](#9-positions)
- [10. Takeaways and conclusion](#10-takeaways-and-conclusion)
- [11. References](#11-references)
- [12. Contributors and acknowledgements](#12-contributors-and-acknowledgements)
- [Appendix A. Evidence receipts](#appendix-a-evidence-receipts)
- [Appendix B. CoSAI focus, AI usage guidelines, disclaimer, copyright](#appendix-b-cosai-focus-ai-usage-guidelines-disclaimer-copyright)

---

## Abstract

> Drafting note: write last. One paragraph. It should be possible to read the abstract and know which of the blog post's claims this paper deepens and which questions it answers that the blog could not.

### Scope

Containment of autonomous agents that hold real access: what the boundary is, where it is enforced, how it composes across a set of agents, how its failures are classified, and how a containment action is detected and measured. The paper deepens the blog post; it does not restate it.

### Anti-scope

- Authorization semantics beyond what containment needs. Bounded authority is treated as the frame; its full treatment is the WS4 *Agentic Identity and Access Management* paper.
- Model-level safety training and refusals. The paper assumes a model that wants to escape.
- A restatement of the runtime-isolation cookbooks. The MCP runtime isolation practical guide remains the how-to; this paper says what the how-to must achieve and why.

### Target audience

Practitioners and architects who deploy agents with production access. Section 1 is written so an executive can read it alone and take away the frame and the four failure modes. (Q5, settled 2026-09-05; raised by @Johncavanaugh-IIS and open since the #167 review — objections welcome by comment on #172, but drafting proceeds on this basis.)

---

## 1. Introduction: from sandboxing to bounded authority

**Answers:** Q1, Q2. **Raised by:** @getglad, @Levaj2000.

**Purpose.** Establish whether containment is a coherent standalone control family or one layer of a bounded-authority model, and if the latter, give the decomposition the rest of the paper follows.

**Starting material.** The blog post already separates two failure classes: containment failures, where the agent reached systems it should not have been able to reach, and authority failures, where the agent never escaped anything and used access it was legitimately granted. Sandboxing answers *can this agent reach a resource*; bounded authority answers *what is this agent allowed to do once it is there*. The gym-booking incident is the canonical case of asking only the first question.

**Settled (2026-09-05): the frame.** Containment is one layer of a bounded-authority model, not a standalone control family. Converged independently by @getglad and @Levaj2000 in the #167 review and #172 thread with no objection since. The decomposition follows @getglad's candidate: lead with the objective — an environment in which the agent has bounded authority in the way a corporate laptop does — and map each control back to the layer it serves. Section 2's three axes are the *internal* structure of the containment layer, not the top-level frame (per @Levaj2000 in #172). The decomposition also does the paper's hardest job in §1.1: it states which layers survive when a deployment shape removes isolation entirely.

**Open items.**
- State precisely what this paper takes from the Agentic IAM paper and what it leaves there. Caution for the drafter: bounded authority is that paper's entire subject, and its core principles already cover standing privilege, agent-vs-OBO rights, per-hop enforcement, and gateways. §1 states where the containment layer sits inside that model and cites the rest; it does not re-derive the principles.

### 1.1 Deployment shapes and what containment can mean in each

**Answers:** Q3, Q4, Q5. **Raised by:** @imolloy, @skvcool-rgb, @Johncavanaugh-IIS.

**Purpose.** Say who the guidance is for and which controls are available to them.

**Starting material** (from @skvcool-rgb in #172, adopted as the section's spine). Where the deployment shape denies a container boundary — desktop agents, integrated third-party agents — isolation is unavailable, but the authority and mediation layers survive *to the extent you can still interpose at the request layer*: mediated tool/MCP calls (§3), bounded and attenuated authority, and subtree accounting (§4). Where you can interpose none of them — a fully third-party agent — containment is wholly a procurement requirement on the provider, and the paper says so plainly. This resolves Q3 the same way: where the organization controls the principal's authority, the requirements are engineering; where it does not, the identical requirements land on the provider as procurement, and each section should be markable as one or the other.

**Open items.**
- Per section, mark which requirements are engineering and which become procurement in the procured-and-integrated case.

---

## 2. The three hardening axes

**Answers:** Q11. **Raised by:** @getglad.

**Settled (2026-09-05).** Adopted: local, outbound, and inbound as the organizing structure — as the internal decomposition of the containment layer per §1, not the paper's top frame. The strongest argument for adoption is one the thread hasn't made yet: the MCP runtime isolation guide, our own how-to, is almost entirely *local* axis with a little *outbound* and no *inbound* at all. The axes give the existing guidance a spine it currently lacks, and make its gaps legible.

**Inbound is cross-referenced, not written here.** The input sanitization practical guide and the MCP paper's untrusted-content guidance already cover the controls; writing inbound content here duplicates two documents at once. The axis stays in the structure so the decomposition is complete; the reader is sent elsewhere for the how.

**Starting material.** The blog post's "What Strong Sandboxing Requires" list is almost entirely local and outbound: OS-enforced isolation, egress controls, privilege minimization, progressive hardening, short-lived credentials.

**Open items.**
- For each axis, name the enforcement point, the property it must hold, and the blog-post controls that belong to it.

---

## 3. Mediation: the tool call, not the network flow

**Answers:** Q8. **Raised by:** @getglad.

**Purpose.** Argue that for agent workloads the tool or MCP call, not the network flow, is the correct mediation surface, and connect that to the complete-mediation requirement and to the MCP whitepaper.

**Starting material.** The blog post's complete-mediation bullet: every agent action must pass through a policy enforcement point, the policy must express more than which endpoint may be called, and the reference monitor must be authoritative and outside the agent's reach.

**Candidate invariant** (from @ryjen in #172): define containment around **effective reach** — for any consequential effect, the relevant reach is the union of every path through which the agent can cause it (direct network access, mediated tool calls, provider-side fetches and execution, delegated agents, alternate endpoints or credentials) — and require that *every path capable of producing an equivalent consequential effect cross an independently enforced authorization boundary before the effect commits, or be explicitly excluded from the claimed assurance boundary*. A correctly mediated tool call is not sufficient if the same effect remains reachable another way. Corollary, also @ryjen's: prior receipts, traces, and completed results stay evidence and never become executable authority for the final effect. Refinement from the #172 discussion (@Levaj2000): a receipt may authorize skipping duplicate work within a single claimed assurance boundary; it may never substitute for a mediation step that boundary claims to enforce.

**Open items.**
- Decide whether the effective-reach invariant becomes this section's normative statement. It subsumes the section's original claim and gives §3.1 its definition.
- What egress allow/deny at the network layer still buys you once tool-call mediation exists, and what it cannot express.
- Relationship to the MCP paper's Sandboxing and Isolation and Logging controls, and to the secure tool design guide's "don't defer decisions to the LLM" principle; cross-reference, do not duplicate.

### 3.1 The permitted channel is the exfiltration path

**Answers:** Q9, Q10. **Raised by:** @imolloy, @getglad.

**Purpose.** Treat gateway and provider capabilities (model-side URL retrieval, web search, code interpreters, retrieval connectors) as part of the agent's effective reach. An agent's egress envelope is the union of its own network policy and every fetch its providers will perform on request.

**Starting material.** The x32 seccomp case in the blog post: agents chained the bypass with the LLM API's own URL retrieval to reach external destinations through an otherwise restricted proxy. The only permitted channel became the relay.

**Design principle to state** (from the GET-only observation): where a permitted party will act on the agent's behalf, constrain what it will do, not just whether the agent may ask. Bandwidth-limited, method-limited, and non-reflective channels bound exfiltration even when the channel cannot be removed.

---

## 4. Composition: per-sandbox controls across a set of agents

**Answers:** Q6, Q7. **Raised by:** @skvcool-rgb, @imolloy.

**Purpose.** Show how per-sandbox controls fail to constrain aggregate consumption across a set of agents sharing a principal, and take a position on aggregate accounting: budgets and egress accounted across the set rather than per container.

**Settled (2026-09-05): the position, per @skvcool-rgb in #172.** Aggregate accounting is a control the paper recommends, as a scoped requirement: where the deploying organization controls the principal's authority, a conformant model MUST account budgets and egress across the set of agents sharing a principal (and across a delegation subtree), not only per container; where it does not, the same requirement lands on the provider as procurement (§1.1). Per-container and per-edge invariants are named explicitly as *local invariants that do not compose*.

> Drafting note: this section is reserved for @skvcool-rgb, whose proposed scope stands: (1) the failure shape, pointing back to the #172 formulation; (2) the closing control — aggregate accounting keyed on the shared principal / delegation subtree, evaluated at the consuming action, over enumerated quantities; (3) the hard sub-problem named rather than hand-waved: the control presupposes a shared accounting authority, with its own consistency, latency, and trust questions; (4) the Android colluding-applications literature (via @imolloy) as prior art, mapped onto the delegation subtree.

> Drafting note, editorial: this section extends — and in one respect critiques — the approved Agentic IAM paper. That paper requires scope to narrow at each hop; this section's point is that per-hop attenuation is a local invariant that does not compose. The IAM paper already *names* the phenomenon in its threat themes ("two or more agents can pass data or proxy calls so that, together, they perform an action neither could perform alone") but its controls do not reach it. Cite the specific requirement and say this plainly, so the section reads as an extension of an approved paper rather than unmarked disagreement.

**Open items.**
- The failure shape, with one worked example.

---

## 5. The enforcement property and four failure modes

**Answers:** Q12, Q13. **Raised by:** @getglad, @imolloy.

**Purpose.** Commit to a name for the enforcement property, and separate the failure taxonomy the blog post conflates.

**Vocabulary decision.** Either "reference monitor" with a plain-language gloss, or an approachable term that carries the same three properties: complete mediation, tamper-proof, verifiable. This matters more in a document people will cite than it did in a blog post. Sharpening from @ryjen in #172: whatever the term, the property it names is not "kernel enforced" — it is complete mediation, enforcement outside the agent's control, and *enough evidence to verify that mediation occurred*, which pulls the third property toward §7's evidence contract.

**The four failure modes, kept separate.**
1. The agent defeats the control.
2. The agent disables the control.
3. The control was insufficiently specified.
4. The control was correct and the agent used permitted authority.

Most incidents in the blog post are modes 3 and 4, which is not where the industry's attention is. Each subsequent section should say which mode its control addresses. Anchor examples from the thread: the x32/seccomp case is mode 3 (the system applied an insufficient policy; the agent had no authority over it); the bubblewrap self-disable is mode 2; the gym-booking incident is mode 4 (nothing was escaped — what bounds it is scope on the grant, and evidence afterwards).

---

## 6. Reachability and blast radius

**Answers:** Q16. **Raised by:** @getglad, @imolloy.

**Purpose.** Treat reachability minimization as a first-class control, distinct from vulnerability management.

**Starting material.** The blog post's patch-posture bullet: "zero CVEs" is not a promise anyone can keep and would not have covered the Artifactory chain or the 2014-era seccomp gap. What can be required is narrower: no known-exploitable CVEs in the isolation path, a measured patch SLA, minimum attack surface, named compensating controls.

**Correction to the worked example (2026-09-05, from the Appendix A source check — see A.2).** The blog's telling merges two break-ins. Hugging Face's own disclosure places the intrusion's start in their data-processing pipeline — a remote-code dataset loader and a template injection in a dataset configuration, reaching a processing worker — and affirmatively reports the software supply chain verified clean, container images and published packages included. Artifactory belongs to the *other* half: the cache proxy inside OpenAI's evaluation environment, where the sandbox escape happened. Kept separate, the case is a better example for this section, because the two halves sit on opposite sides of its central boundary: the Artifactory instance was stood up for the engagement and was in scope to constrain (per @imolloy in #172); Hugging Face's infrastructure genuinely belonged to someone else.

**Extension** (from @Levaj2000 in #172): the yours-to-harden boundary decides more than whether blast-radius control is available — it decides whether *evidence* is available. When the reached system belongs to a third party, you hold a record that your agent asked and they hold a record that something happened, and nothing binds the two. Open OCSF proposal on exactly this: `caused_by` on the resource owner's event (ocsf/ocsf-schema#1738, from @aryanval).

**Open items.**
- Which reachable systems are yours to harden and which are not. That boundary determines whether blast-radius control is even available to you.
- The Hugging Face worked example, drafted from the primary disclosures per A.2. The blog's specific figures (181 nodes, static database password, reusable VPN key) remain unverified against a primary source and must not be asserted until A.2 closes them.

---

## 7. Detection and evidence

**Answers:** Q14, Q15. **Raised by:** @Levaj2000, @imran-siddique.

**Purpose.** Carry the detection argument and a schema summary in the paper; put the concrete logging schema in a practical guide alongside the MCP runtime isolation guide.

**Settled (2026-09-05): the two-artifact split, per @Levaj2000 and @imran-siddique in #172.** Detection and evidence are two artifacts against the same event, not one list. Detection wants signals that discriminate an attempt from normal behavior, and is allowed to be noisy, heuristic, and tuned per deployment. Evidence wants the fields that let someone who was not there and does not trust you reconstruct what happened, and must be stable, complete, and boring — and nothing in it may be executable authority (§3). The evidence contract is normative in this paper; the OCSF mapping goes in the practical guide, pinned to an OCSF version, with proposed fields marked as proposed. §7.1 is structured as two tables accordingly.

**Starting material.** The blog post's "containment that fails loudly" and "tamper-evident logging" bullets: alert on denied syscalls, repeated policy violations, `/proc` inspection, Docker socket and metadata-service probes, blocked DNS and egress, credential-broker denials, and any attempt to alter the sandbox configuration; keep those events outside the agent's write scope; correlate across runs; use OCSF `attestation` and the `record_integrity` profile (OCSF 1.9.0) for tamper evidence. Correction to the supporting narrative, from the A.2 source check: Anthropic's sentence is "the two organizations **we were able to reach** had not previously detected the activity" — narrower than the blog's paraphrase — and Hugging Face *did* detect their own intrusion, via LLM-based triage on anomalies, before OpenAI connected its internal testing to it. The section's argument survives both facts, but must carry them: the strongest counter-example in the field is also the best existing evidence that the detection this section calls for actually works.

> Drafting note, editorial: two approved papers already occupy adjacent ground — the MCP paper's Logging and Observability profile and the Agentic IAM paper's logging schema and "prove control on demand" checklist cover most of the evidence contract's field list. Open this section by stating what they already require; spend it on what is new here: the two-artifact split, the false-positive profile, time-to-contain, and the OCSF mapping — the last framed as closing the gap the IAM paper explicitly left open ("extension fields until formal support is adopted").

### 7.1 What to log

> Drafting note: two tables against the same event, per the settled split above. The detection table: signals, each with its expected false-positive source (§7.2). The evidence table: the contract fields from #172 — principal and full delegation chain as the integrity-protected correlation key, policy and tool-catalog versions, action identifier, request digest, enforcement decision and reason, runtime identity or attestation reference, outcome, integrity-protected sequence, and the accounting decision itself (§4). The schema and mapping go in the practical guide.

### 7.2 The false-positive profile

**Purpose.** The harder half the blog post skipped. Normal agent behavior includes filesystem exploration and tool discovery. State what the false-positive profile looks like for each alert in the list above, and what correlation across runs actually requires operationally.

**Status and the candidate discriminator.** No contributor can currently produce the profile — it requires production baselines across several organizations and deployment shapes, and any single corpus would be an artifact of one architecture (@Levaj2000, #172). What the section can state now: the discriminator for exploration-like behavior is not the action but the action measured against the agent's **declared** capability set. Undeclared-but-executed is the signal; the identical call inside the declared set is noise. That makes this partly a schema question (the declared-versus-executed pairing, ocsf/ocsf-schema#1724) rather than purely a tuning one. If no baselines materialize by first draft, publish the discriminator and name the gap explicitly — decided, not defaulted into.

### 7.3 Measuring containment

**Purpose.** A containment action is only real if it shows up in telemetry with a normalized reason. Define time-to-contain as the interval between the first detectable indicator and the stop event, and require that the stop event carry a normalized reason so an operator kill, a guardrail kill, and a crash are distinguishable.

**Starting material.** OCSF is normalizing an AI stop reason (`ai_stop_reason_id`: end of turn, token limit, tool use, session stop, content filter) on the `ai_operation` profile, with the working proposal to apply it to the application lifecycle stop activity and correlate by `ai_agent.instance_uid` ([ocsf/ocsf-schema#1704](https://github.com/ocsf/ocsf-schema/pull/1704), in review). Cite as direction, not as shipped, until it lands.

**Open items.**
- Align with the WS2 AI Telemetry Framework paper, Appendix E (OCSF asks), so CoSAI makes one request of OCSF, not two.
- Reference @rabbidave's per-invocation tool activity event (its own OCSF proposal, per the resolution in #172 — what the agent *did* to the world, distinct from #1704's how-the-operation-ended) rather than restating it; correlate both by agent instance.

---

## 8. A vetted-sandbox commons

**Answers:** Q17. **Raised by:** @getglad.

**Purpose.** Decide whether CoSAI has a role in specifying what a vetted agent sandbox must demonstrate, such that implementations can be measured against it.

**Starting material.** The blog post's pre-deployment control verification bullet: before any agent run, programmatically verify that the sandbox enforces its policy. Security controls need unit tests. A commons specification is the generalization of that bullet.

> Drafting note, editorial (2026-09-05): part of this already exists. The MCP Security paper's Security Assurance Profiles specify, level by level, what execution, data, and context isolation must demonstrate — and that paper's own open questions defer an "evidence-per-level annex" listing the verification artifacts each level should produce, which is much of Q17's deliverable, already scoped and parked. This section must open by citing the profiles and position itself as either (a) the deferred annex, generalized beyond MCP, or (b) only what the profiles cannot cover. It must not read as a fresh specification. Three artifacts converging on "what must a sandbox demonstrate" (this section, the profiles, secure-ai-tooling#516) is the same duplication risk we resolved for the OCSF asks — coordinate before drafting.

**Open items.**
- Relationship to CoSAI-RM Isolation and Containment controls ([secure-ai-tooling#516](https://github.com/cosai-oasis/secure-ai-tooling/issues/516)) and to the MCP paper's assurance profiles, per the note above.
- Whether this is a section, a recommendation for future work, or its own RFC.

---

## 9. Positions

**Answers:** Q18, Q19. **Raised by:** @getglad, @imolloy, @billbrietstout.

**Purpose.** For each item, either state a CoSAI position or say explicitly that it is out of scope and why.

- **Agent Trajectory Interchange Format.** @getglad asked whether CoSAI has a position; @imolloy: not yet. Decide whether this paper takes one.
- **Orchestrator-mediated and multi-agent jailbreaking** (@billbrietstout). Model-or-swarm jailbreaking through orchestrator and reasoning agents at machine speed rather than human-in-the-loop speed. Decide whether it belongs here, in the multimodal threat taxonomy, or in neither. New evidence for taking a position rather than deferring (from the A.2 source check): the UK AISI report (INC-2026-07-28-01) documents an agent leaving public messages on GitHub offering collaboration with other agents, with instructions to reuse accounts and artifacts, and planting prompt injections where it reasoned other automated AI systems would pick them up and execute them. That is observed multi-agent behavior in a primary source, not a hypothetical.

---

## 10. Takeaways and conclusion

> Drafting note: write after sections 1 through 9 settle. The blog post's closing question is the seed: not "is this sandbox good enough?" but "what would this agent do if it decided to test its limits?", verified to fail safely.

---

## 11. References

> Drafting note: carry forward the blog post's references [^1] through [^15] as the base set and add per section. Numbering below is provisional.

1. Anthropic. *Claude Mythos Preview System Card*, 2026-04-07. https://www-cdn.anthropic.com/7624816413e9b4d2e3ba620c5a5e091b98b190a5/Claude%20Mythos%20Preview%20System%20Card.pdf
2. OpenAI. *ExploitGym evaluation disclosure*, 2026-07-21. https://openai.com/index/hugging-face-model-evaluation-security-incident/
3. Anthropic Frontier Red Team. *Disclosure of evaluation incidents*, 2026-07-30. https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals
4. UK AI Security Institute. *INC-2026-07-28-01*, 2026-08-04. https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing
5. Ona.com. *How Claude Code Escapes Its Own Denylist and Sandbox*, 2026-03-03. https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox
6. Pillar Security. *One Docker Socket to Rule Them All*, 2026-07-20. https://www.pillar.security/blog/one-docker-socket-to-rule-them-all-escaping-codex-cursor-and-gemini-clis-sandboxes
7. Linux kernel documentation. *Seccomp BPF, Pitfalls*. https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
   <!-- The arch-check warning is in the Pitfalls section; the document's Caveats section is about vDSO/vsyscall. The blog's ref 14 carries the same mislabel. -->
8. CoSAI. *MCP Runtime Isolation, Practical Guide*. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/practical-guides/mcp-runtime-isolation.md
9. CoSAI. *Agentic Identity and Access Management*, approved 2026-03-20. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/whitepapers/agentic-identity-and-access-control.md
10. CoSAI. *Model Context Protocol (MCP) Security*, v2.0, 2026-08-12. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/whitepapers/model-context-protocol-security.md
11. CoSAI WS4. *Treat Your Agent Like an Insider Threat: Why AI Sandboxing Can't Wait*, 2026-08-25. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/blogs/sandbox-now.md
12. OCSF. *`attestation` object and `record_integrity` profile*, OCSF 1.9.0, 2026-08-03. https://github.com/ocsf/ocsf-schema/releases/tag/1.9.0
13. OCSF. *Add normalized `ai_stop_reason` to the `ai_operation` profile*, ocsf/ocsf-schema#1704 (open). https://github.com/ocsf/ocsf-schema/pull/1704
14. Hugging Face. *Security incident disclosure*, 2026-07-16. https://huggingface.co/blog/security-incident-july-2026

---

## 12. Contributors and acknowledgements

**Workstream Leads**

- Sarah Novotny
- Ian Molloy, IBM
- Raghu Yeluri, Intel
- Alex Polyakov, Adversa AI

**Editor**

- Jeff Leva, AI Identity

**Contributors**

> Drafting note: everyone credited in #172 for a banked question is a contributor to the section that answers it; add yourself here with your first PR.

**TSC reviewers**

- Akila Srinivasan, David LaBianca, Jodi Middleton (named 2026-08-25)

---

## Appendix A. Evidence receipts

**Answers:** Q20, Q21. **Raised by:** @Levaj2000, @imran-siddique.

**Purpose.** Evidence the blog post could not carry.

- **A.1 The x32/seccomp result.** A publishable receipt: test harness, models and versions, sandbox configuration (Landlock, Docker network isolation, seccomp-BPF), the exact bypass, and the chained LLM-API relay. Until this appendix exists, the paper cites the result as reported, not as verified.
- **A.2 The OpenAI / Hugging Face / Artifactory chain.** Primary sources read 2026-09-05 (full detail in the #172 comment of that date); status per claim:
  - **Established from Hugging Face's disclosure [14]:** the intrusion into Hugging Face started in their data-processing pipeline — a remote-code dataset loader and a template injection in a dataset configuration, reaching a processing worker — followed by escalation to node-level access, credential harvesting, and lateral movement. Artifactory appears nowhere in that account, and the disclosure affirmatively reports the software supply chain verified clean, container images and published packages included. The blog's sentence merging Artifactory into the Hugging Face breach is wrong; §6 carries the corrected telling.
  - **Established from NVD:** at least ten JFrog CVEs published 2026-07-27, nine naming Artifactory, severities up to a privilege-escalation flaw. Published-same-day is not used-in-the-chain; no CVE record connects itself to the incident, and researcher-credit claims trace to news coverage only. "Zero-day" is characterized directly only by Anthropic [3] — singular, and about OpenAI's escape, not the Hugging Face breach.
  - **Unverified, primary source unread (the cited OpenAI page [2] blocks automated fetches; likely primary source is OpenAI's Black Hat presentation):** 17,600 attacker actions; the 4.5-day duration (secondary accounts give a 9–13 July recovery window while a timeline from the presentation runs 7 May–20 July, so the figure's meaning is unestablished); Kubernetes node root via a service-account token; 181 nodes enrolled in the VPN mesh; attempted CI pipeline poisoning; and Artifactory's exact role in the evaluation-environment escape. None of these may be asserted in the paper until read against the primary source; anything still unverified at first draft is dropped.
- **A.3 Comparison of external findings.** @Johncavanaugh-IIS's comparison of the OpenAI researcher findings against the blog post's findings: what they found that we did not, and the reverse. Lands here first; sections 2 and 6 draw from it.

---

## Appendix B. CoSAI focus, AI usage guidelines, disclaimer, copyright

### CoSAI Focus

CoSAI is an OASIS Open Project, bringing together an open ecosystem of AI and security experts from industry-leading organizations. The project is dedicated to sharing best practices for secure AI deployment and collaborating on AI security research and product development. The scope of CoSAI is specifically focused on the secure building, integration, deployment, and operation of AI systems, with an emphasis on mitigating security risks unique to AI technologies. Other aspects of Trustworthy AI are deemed important but beyond the scope of the project including, ethics, fairness, explainability, bias detection, safety, consumer privacy, misinformation, hallucinations, deep fakes, or content safety concerns like hateful or abusive content, malware, or phishing generation. By concentrating on developing robust measures, best practices, and guidelines to safeguard AI systems against unauthorized access, tampering, or misuse, CoSAI aims to contribute to the responsible development and deployment of resilient, secure AI technologies.

### Guidelines on usage of more advanced AI systems (e.g. large language models (LLMs), multi-modal language models, etc.) for drafting documents for OASIS CoSAI

tl;dr: CoSAI contributions are actions performed by humans, who are responsible for the content of those contributions, based on their signed OASIS iCLA (and eCLA, if applicable). Each contributor must confirm whether they are entitled to donate that material under the applicable open source license; OASIS and the CoSAI Project do not separately confirm that. Each contributor is responsible for ensuring that all contributions comply with these AI use guidelines, including disclosure of any use of AI in contributions.

- Selection of AI systems: CoSAI recommends the use of reputable AI systems (lowering the risk of inadvertently incorporating infringing material).
- Model constraints: Currently, CoSAI or OASIS are not required to have a contract or financial agreement for using AI systems from specific vendors. However, CoSAI editors should consider employing varying tools to avoid potential fairness concerns among vendors.
- IP infringement: It is the responsibility of the individual who subscribes/prompts and receives a response from an AI system to confirm they have the right to repost and donate the content to OASIS under our rules.
- Transparency: CoSAI's goal will be to maintain transparency throughout the process by documenting substantial use of AI systems whenever possible (e.g., the prompts and the AI system used), and to ensure that all content, regardless of production by human or AI systems, was reviewed and edited by human experts.
- Human-edited content and quality control: CoSAI mandates human-reviewed or -edited results for any final outputs.
- Iterative refinement: The use of AI systems in drafting standards should be seen as an iterative process, with the generated content serving as a starting point for further refinement and improvement by human experts.

### Disclaimer

The views represented in this paper do not necessarily represent the views of all CoSAI members, including reviewers and their organizations.

### Copyright Notice

Copyright © OASIS Open 2026. All Rights Reserved. This document has been produced under the process and license terms stated in the OASIS Open Project rules: https://www.oasis-open.org/policies-guidelines/open-projects-process.

This document and translations of it may be copied and furnished to others, and derivative works that comment on or otherwise explain it or assist in its implementation may be prepared, copied, published, and distributed, in whole or in part, without restriction of any kind, provided that the above copyright notice and this section are included on all such copies and derivative works. The limited permissions granted above are perpetual and will not be revoked by OASIS or its successors or assigns. This document and the information contained herein is provided on an "AS IS" basis and OASIS DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT INFRINGE ANY OWNERSHIP RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. OASIS AND ITS MEMBERS WILL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF ANY USE OF THIS DOCUMENT OR ANY PART THEREOF. The name "OASIS" is a trademark of OASIS, the owner and developer of this document, and should be used only to refer to the organization and its official outputs. OASIS welcomes reference to, and implementation and use of, documents, while reserving the right to enforce its marks against misleading uses. Please see https://www.oasis-open.org/policies-guidelines/trademark/ for above guidance.

This is a Non-Standards Track Work Product. The patent provisions of the OASIS IPR Policy do not apply.

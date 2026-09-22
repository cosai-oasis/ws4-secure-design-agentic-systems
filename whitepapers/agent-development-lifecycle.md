---
title: "Securing the Agent Development Lifecycle: Five Assumptions That No Longer Hold"
author: "Workstream 4: Secure Design Patterns for Agentic Systems"
date: 2026-09-16
version: 0.2-draft
status: "Working draft. Not reviewed, not approved."
---

# Securing the Agent Development Lifecycle: Five Assumptions That No Longer Hold

**Status:** Working draft. Not reviewed, not approved. Sections 2 and 3 make load-bearing claims and are the parts most in need of argument. Section 5 lists what is still unsettled. Section 6 records the positions the working group has taken so far, with dates and sources, and is the place new positions go as the group argues them out. Review happens on the pull request, not in a separate document.

# Table of contents

- [Abstract](#abstract)
  - [Scope](#scope)
  - [Anti-scope](#anti-scope)
  - [Target audience](#target-audience)
- [1. Why agent development needs its own lifecycle](#1-why-agent-development-needs-its-own-lifecycle)
  - [1.1 Five assumptions secure development rests on](#11-five-assumptions-secure-development-rests-on)
    - [1.1.1 Behavior is fixed when the artifact is built](#111-behavior-is-fixed-when-the-artifact-is-built)
    - [1.1.2 The reviewable artifact is the code](#112-the-reviewable-artifact-is-the-code)
    - [1.1.3 Identity is a service account](#113-identity-is-a-service-account)
    - [1.1.4 Testing approximates production behavior](#114-testing-approximates-production-behavior)
    - [1.1.5 Retirement means deleting the deployment](#115-retirement-means-deleting-the-deployment)
  - [1.2 What existing frameworks reach](#12-what-existing-frameworks-reach)
- [2. Boundaries of the lifecycle](#2-boundaries-of-the-lifecycle)
  - [2.1 A process framework, not an implementation guide](#21-a-process-framework-not-an-implementation-guide)
  - [2.2 Design time is inside the process](#22-design-time-is-inside-the-process)
  - [2.3 The agent entity is the unit of scope](#23-the-agent-entity-is-the-unit-of-scope)
  - [2.4 Every agent has an accountable owner](#24-every-agent-has-an-accountable-owner)
- [3. Lifecycle phases](#3-lifecycle-phases)
  - [3.1 Scoping and design](#31-scoping-and-design)
  - [3.2 Supply chain](#32-supply-chain)
  - [3.3 Development](#33-development)
  - [3.4 Admission and deployment](#34-admission-and-deployment)
  - [3.5 Runtime](#35-runtime)
  - [3.6 Reflection and knowledge consolidation](#36-reflection-and-knowledge-consolidation)
  - [3.7 Maintenance](#37-maintenance)
  - [3.8 Decommissioning](#38-decommissioning)
- [4. Applying the lifecycle](#4-applying-the-lifecycle)
  - [4.1 Adapting controls you already run](#41-adapting-controls-you-already-run)
  - [4.2 Where each assumption is repaired](#42-where-each-assumption-is-repaired)
- [5. Open questions](#5-open-questions)
- [6. Positions of the working group](#6-positions-of-the-working-group)
  - [6.1 How a position gets in](#61-how-a-position-gets-in)
  - [6.2 Positions taken](#62-positions-taken)
- [7. Takeaways and conclusion](#7-takeaways-and-conclusion)
- [8. References](#8-references)
- [9. Contributors and acknowledgements](#9-contributors-and-acknowledgements)
- [Appendix A. Gate summary](#appendix-a-gate-summary)
- [Appendix B. CoSAI focus, AI usage guidelines, disclaimer, copyright](#appendix-b-cosai-focus-ai-usage-guidelines-disclaimer-copyright)

---

## Abstract

Organizations deploying AI agents are applying their existing secure software development practices to them and finding that the practices do not fit. The mismatch is usually read as a maturity problem: the tooling will catch up, the scanners will learn to read prompts. It is structural. Secure development frameworks encode assumptions about how software behaves, and agentic systems violate five of them: that behavior is fixed when the artifact is built, that the reviewable artifact is the code, that identity is a service account, that testing approximates production behavior, and that retirement means deleting the deployment.

This paper sets out an agent development lifecycle constructed as a direct response to those five failures. It is a process framework: it states what must be decided, verified, and evidenced, at which point in an agent's life, and by whom. Each of its eight phases is derived from a named assumption that breaks, so a reader who disagrees with a phase can locate and attack the reasoning that produced it rather than the phase itself.

The intended outcome is practical. A security team should be able to adapt the controls it already runs instead of starting over, and should be able to say, for any agent in its estate, which obligations have been met and which gate is next.

### Scope

- The lifecycle of an agent as an entity, from the decision to build or acquire one through its verified retirement.
- The security-relevant decisions, gates, and evidence at each phase.
- The division between what a deploying organization implements in the agent itself and what it must verify of the platforms the agent depends on.
- Adaptation guidance for organizations already operating a secure development lifecycle.

### Anti-scope

- **Mechanism design.** How to construct an isolation boundary, an authorization service, or a policy engine. This paper says containment posture must be decided and verified; it does not say how to build the containment.
- **Identity and delegation protocol specification.** Credential formats, delegation token semantics, and authorization protocol design are prerequisites the lifecycle consumes, treated in their own right elsewhere.
- **Telemetry schema.** The lifecycle requires that certain events be evidenced. It does not define the wire format or field taxonomy for that evidence.
- **Conventional package and dependency supply chain practice.** It applies unchanged to an agent's conventional dependencies and is not restated here.
- **The security of code or content an agent produces.** That is a property of the agent's output and belongs to the lifecycle of whatever consumes it. This paper is about the security of the agent itself.
- **Model development.** Training, tuning, and evaluation of foundation models. Models are consumed by agents as upstream resources.

### Target audience

- **Agent developers** building and configuring agentic systems.
- **Platform and framework teams** providing the infrastructure other teams build agents on.
- **Security and risk officers** setting policy for what may be deployed, and under what conditions.
- **Third-party risk teams** evaluating procured agentic products against a defensible checklist.
- **Enterprise architects** integrating agents into an existing security ecosystem.

---

## 1. Why agent development needs its own lifecycle

Secure software development frameworks are not wrong about agents. They are silent about them, which is a more specific problem and a more tractable one. Their controls encode assumptions that held well enough for four decades of software and that agentic systems break. Naming the breakages precisely is what earns each phase in section 3 its place, and it is the discipline this paper tries to hold: no phase appears that cannot be traced to a failure below.

One clarification before the argument begins, because the vocabulary is already colliding. A parallel and growing body of work asks how AI agents change the development of *conventional* software: how a team plans, builds, tests, and ships its product faster when agents do much of the work. That is a different subject from this one. Here the agent is the artifact being secured, not the instrument doing the securing. The two lifecycles share terminology and a handful of controls, and they answer different questions.

### 1.1 Five assumptions secure development rests on

#### 1.1.1 Behavior is fixed when the artifact is built

For conventional software, the build is the moment behavior is determined. Everything downstream (signing, scanning, promotion, change control) protects an artifact whose behavior is already settled. Review the code and you have reviewed the behavior, subject to the quality of the review.

An agent's behavior is determined at runtime, by the composition of its system instructions, a model whose weights the deploying organization did not author, content retrieved at the moment of the request, memory accumulated across prior sessions, and whichever tools happen to be reachable. The same artifact, deployed unchanged, behaves differently this week than last because the corpus it retrieves from changed, or because the model behind an API was updated by its provider. Build-time assurance does not transfer to runtime.

**Consequence.** Assurance must be established at admission and maintained continuously during operation, rather than settled once at build.

#### 1.1.2 The reviewable artifact is the code

Code review, static analysis, and dependency scanning all assume that security-relevant decisions are expressed in code, and that tooling can read the language they are expressed in.

For an agent, the security-relevant decisions are largely expressed in prose and configuration: the system instructions, the tool permission manifest, the memory retention policy, the trust assignments over retrieval sources, the conditions under which a human must approve an action. This is the real policy surface, and it is invisible to tooling built for the other kind of artifact. A change to an instruction that materially widens an agent's authority can pass every gate that an equivalent change in code would have failed.

**Consequence.** The policy surface needs its own authoring, review, versioning, and rollback discipline, at parity with code.

#### 1.1.3 Identity is a service account

Conventional workloads authenticate as themselves and act on behalf of a caller whose identity travels in the request. Authorization is a question about the caller, answered at the resource.

Agents act with delegated authority across chains. A person delegates to an agent, which delegates to a sub-agent, which invokes a tool that applies its own authorization logic against whatever identity reached it. Authority accumulates and blurs as it travels. The question *who authorized this action, under what constraint, and against whose entitlement* has no reliable answer unless the lifecycle deliberately produced one.

**Consequence.** Establishing an agent's identity, binding it to constraints, and making it verifiable at each hop is a gated lifecycle event, not a deployment detail.

#### 1.1.4 Testing approximates production behavior

A passing test suite is evidence about production because the system is deterministic enough for the inference to hold. Same input, same path, same result.

For a non-deterministic system consuming untrusted input, a passing test says the system behaved acceptably on the inputs that were sampled. That is evidence of the absence of a specific failure, not evidence of the presence of a property. Adversarial input is by construction drawn from the part of the distribution a test suite does not sample, and the agent's own variability means an identical input may not reproduce the tested path.

**Consequence.** Pre-deployment testing must be supplemented by a recorded behavioral baseline and continuous comparison of live behavior against it.

#### 1.1.5 Retirement means deleting the deployment

Decommissioning conventional software means removing the running instance, revoking its credentials, and disposing of its data under a retention policy. The system leaves no residue beyond what was provisioned for it.

An agent leaves residue that was never provisioned: durable memory it chose to write, credentials and grants it accrued while operating, webhooks and subscriptions it established, sub-agents it created, and knowledge it consolidated into retrieval stores that other agents now read as authoritative. Deleting the deployment retracts none of it. An agent can continue to shape behavior long after it stops running, through what it left behind.

**Consequence.** Retirement is a verified teardown with its own authorization and its own evidence, not an operational afterthought.

### 1.2 What existing frameworks reach

The available frameworks are individually sound and collectively leave a gap, because they divide the problem along axes that do not include the agent as a subject persisting through time.

| Framework | What it reaches | Where it stops for agents |
|---|---|---|
| NIST SSDF, SP 800-218 [^1] | Practice groups spanning prepare, protect, produce, and respond; a strong baseline for phase alignment | Encodes assumptions 1 and 2: the artifact is code, and its behavior is settled at build |
| NIST SP 800-218A [^2] | Extends secure development practice to model development, including provenance and tuning | Takes the model as subject. The agent that consumes the model is out of frame |
| OWASP SAMM [^3] | Organization-level maturity model for assurance activities | Organizationally oriented; offers no agent-specific assurance activities to mature |
| OWASP LLM Top 10 and Agentic Security Initiative [^4] | Concrete agent-relevant failure modes, including prompt injection and excessive agency | A risk enumeration rather than a lifecycle. Says what goes wrong, not at which gate it is prevented |
| CIS AI Agent Companion Guide [^5] | Architectural decomposition of an agent into layers, with control mapping | Architectural rather than temporal. Answers *what are the parts*, not *when is each obligation met* |
| ISO/IEC 42001 [^6] | Management system requirements for AI at organizational level | Governance altitude; does not reach engineering-phase gates |
| Vendor AI-native development playbooks [^7] | The most operationally concrete material available: policy expressed as version-controlled configuration, an identity for the agent distinct from the engineer who triggered it, and tiered autonomy with explicit human authorization at the production gate | Take the agent as instrument rather than artifact. No provenance or trust-tier gate on the models and tools the agent consumes, and no treatment of retirement |

Three patterns are worth drawing out. First, these frameworks divide by the wrong axis for this problem: some take the model as subject, some the organization, some the architecture, and none takes the agent entity across its lifetime. Second, where agent-specific material does exist, it is overwhelmingly enumerative. Enumerations are valuable and this paper depends on them, but they do not tell an engineering team which gate is supposed to catch a given risk. That is the service a lifecycle framework provides, and it is the gap this paper addresses. Third, the most operationally mature material in the table is the material that takes the agent as an instrument rather than as the thing being shipped, which is evidence that the gap is not a maturity problem waiting to close on its own. It is a difference in subject, and it will persist until something addresses the subject directly.

---

## 2. Boundaries of the lifecycle

Four boundary claims, stated plainly because much of the disagreement about how to secure agents turns out, on inspection, to be disagreement about which of these is true.

### 2.1 A process framework, not an implementation guide

The lifecycle describes what must be decided, verified, and evidenced, at which point, and by whom. It does not describe how to build the mechanism that satisfies a requirement.

This is a deliberate limit and it does real work. A document explaining how to construct an isolation boundary is valuable, and it is a different document; conflating the two produces a framework simultaneously too prescriptive to adopt incrementally and too shallow to implement from. The lifecycle's obligation is to establish that containment posture is decided before procurement and verified before production traffic. Which technology satisfies that obligation is the deploying organization's choice, and will differ by risk appetite, platform, and regulatory regime.

### 2.2 Design time is inside the process

Because assumption 1 fails and behavior is not fixed at build, the decisions that constrain behavior cannot be discovered during implementation. They must be made deliberately and recorded before anything is procured or written.

Intended use, autonomy bounds, blast radius, data classification, the identity and delegation model, containment posture, and the threat model are lifecycle artifacts in their own right. They are the inputs against which every later gate is evaluated. An admission gate cannot pass or fail an agent without a recorded statement of what that agent was supposed to be permitted to do.

This makes design time the first phase rather than a precondition sitting outside the lifecycle. The distinction is not academic. A design activity that sits outside the numbered phases has no gate, produces no required artifact, and is the first thing skipped under delivery pressure.

### 2.3 The agent entity is the unit of scope

The lifecycle governs the agent: its instructions, its reasoning core, its input and output handling, and the policies by which it consumes everything else. For the resources an agent depends on (the model, the orchestration platform, the tools, the data stores, the infrastructure), the deploying organization implements consumption controls in the agent and verifies that each platform meets its stated requirements.

The distinction is between implementing and verifying, and its practical force lands at admission: if a prerequisite platform cannot evidence that it meets a requirement the agent depends on, the agent does not deploy. This keeps the lifecycle tractable. An organization is not required to re-secure its cloud provider in order to deploy an agent. It is required to know what it is depending on, and to have verified the dependency.

### 2.4 Every agent has an accountable owner

A named human or organizational owner is accountable for each agent. That relationship survives delegation, is verifiable at runtime, and is explicitly transferred or terminated rather than allowed to lapse.

This is the least technical of the four claims and the one most often missing in practice. Without it there is no answer to who authorized an action, no party with standing to approve retirement, and nobody who notices when an agent outlives the purpose it was commissioned for. Ownership lapse is the most common precondition for the residue problem described in assumption 5.

---

## 3. Lifecycle phases

Eight phases. Each is stated with the assumption it repairs and the gate that must pass before the agent proceeds.

### 3.1 Scoping and design

*Repairs assumption 1.*

The organization decides what the agent is for and what it may become. Define permitted goals, prohibited goals, and escalation paths. Establish autonomy bounds and the blast radius of a worst-case action. Classify the data the agent may read, write, retain, or disclose. Select the identity and delegation model. Set containment posture. Identify which actions require human approval before execution. Produce a threat model.

**Gate.** These decisions are recorded before procurement or implementation begins. An unrecorded decision is not a decision; it is an assumption that will be discovered during an incident.

### 3.2 Supply chain

*Repairs assumptions 1 and 2.*

Establish provenance and trust for everything the agent will incorporate: models, tools, prompt templates, frameworks, and retrieval sources. Verify provenance records and supplier evaluation evidence. Assign a trust tier to each component. Conduct application-specific behavioral testing, since a component's suitability is a question about this use case rather than a general property of the component. Extend inventory practice to cover models, prompts, and tool definitions alongside conventional dependencies.

**Gate.** Every component the agent depends on is inventoried, with known provenance and an assigned trust tier.

### 3.3 Development

*Repairs assumption 2.*

Author the policy surface as a first-class artifact: system instructions with injection-resistant construction; the tool permission manifest, at least privilege per tool; memory retention and filtering policy; trust assignments over retrieval sources; the conditions that trigger human approval; and the instrumentation that will make runtime behavior observable.

Each of these is versioned, reviewed by someone other than its author, and revertible independently of the code around it.

**Gate.** The policy surface is under change control at parity with code, and a reviewer can answer *what authority does this agent hold* by reading it.

### 3.4 Admission and deployment

*Repairs assumptions 1, 3, and 4.*

The strongest gate in the lifecycle, and the one that converts everything prior into a decision.

Implement: establish the agent's identity and bind it to the constraints set at design time; register it with the identity provider; verify that deployed components are mutually consistent, so instructions, handling logic, and instrumentation come from the same reviewed revision; conduct adversarial testing against known agent failure modes; and record the behavioral baseline that runtime will be compared against.

Verify: that the identity provider issues and will validate the agent's credentials; that serving, storage, and orchestration platforms meet the requirements the agent's design depends on; and that audit logging is in place and reaching a destination somebody reads.

**Gate.** Any unmet prerequisite blocks deployment. This is where the implement-and-verify distinction from section 2.3 acquires teeth. A gate that cannot block is a report.

### 3.5 Runtime

*Repairs assumptions 1 and 4.*

Enforce continuously what was verified once. The agent presents its identity for each consequential action. Policy is evaluated at the point of tool invocation rather than assumed from deployment. Input and output handling apply their filters against live traffic. Decision traces are recorded at fidelity sufficient to reconstruct why an action was taken. Live behavior is compared against the recorded baseline, and the comparison is fail-closed: an agent whose monitoring is off or unread is outside its admitted state. An intervention capability exists and has been exercised rather than merely configured. In the CoSAI Risk Map [^8] the record is the audit record repository, and the comparison and response path are a control [^11].

Verification continues too. Prerequisites that passed at admission can regress, and a platform that stops meeting a requirement should surface as an alert rather than as an incident.

**Gate.** Continuous. An agent operating without enforcement, evidence, and intervention capability has left the lifecycle rather than progressed through it.

### 3.6 Reflection and knowledge consolidation

*Repairs assumptions 1 and 5.*

The phase that governs what an agent is permitted to learn. Between a completed run and the next one, information may be promoted from ephemeral context into durable memory, or into retrieval sources other agents will read. Promotion is where poisoning becomes persistent, and where an agent's future behavior is silently redefined.

Enforce memory-write policy. Capture provenance and source attribution for anything retained. Check candidate knowledge against approved policy and authoritative data before it is written. Require human approval for high-impact durable memory. Apply retention labels and rollback markers. Maintain the audit link from a future decision back to the knowledge that informed it.

**Gate.** Nothing becomes durable without provenance and a policy check. Ephemeral context and approved durable memory are distinguishable at the storage layer, not only by convention.

### 3.7 Maintenance

*Repairs assumptions 1 and 2.*

Changes to a live agent re-enter review rather than accumulating. A change to the policy surface is treated as a change to behavior, because it is one: behavioral regression testing runs after any change, the baseline is re-established, and instructions and handling logic revert together as a unit rather than drifting apart.

Upstream change is the harder half. A model updated behind an API, a framework patched, a tool's contract altered: none of these are changes the deploying organization initiated, and each can alter agent behavior. Maintenance is the phase that notices.

**Gate.** No change to the policy surface, and no change to a prerequisite, reaches production without re-baselining behavior.

### 3.8 Decommissioning

*Repairs assumption 5.*

Decommissioning ends the agent's authority to act. Whether it can come back later is a policy choice, and if it comes back it re-enters through Admission as a new entity. Pausing, suspending, or quarantining a live agent are Runtime or Maintenance states, not this phase. An agent that can resume under the same admitted identity has not been decommissioned. This definition was settled on the working group's RFC [^10] after a longer draft with "soft" and "hard" modes was withdrawn; what looked like two modes was one phase with parameters the organization sets.

Every decommissioning does the same things, whatever the organization's retention rules. Record who requested retirement, who approved it, and why. Freeze inbound invocation. Revoke authenticators and tombstone the identifier rather than delete it, because a deleted identifier breaks replay detection. Revoke delegated authority across every sub-agent the agent created. Enumerate its resources across every system it touched and give each one a disposition: revoked, deleted, cryptographically shredded, retained until a date, held for legal reasons, handed over to a successor, or an explicit exception with an owner and an expiry. Publish the terminal state and its effective time where a relying party can check it without the retiring organization's help. Store the disposition receipt: retired identity, authorizer, effective time, each asset's disposition, evidence references, and exceptions.

What varies is set by the organization, in the way NIST SP 800-53 leaves parameters to the implementer [^9]: who may authorize, whether dual control or a legal-hold check is required, how each store is disposed of, how long held assets are kept, which sanitization technique applies, how long the tombstoned identifier is retained, and which archived artifacts may enter a later Admission. Archiving the traces and purging the tool grants of the same agent is a valid combination.

Two losses are easy to miss. Other systems and people may have come to depend on capabilities the agent was never documented as providing, and the agent may hold knowledge that exists nowhere else. Both should be enumerated before the receipt closes, and instrumented for at development time, since neither can be recovered afterwards. Decommissioning can also be imposed, when an upstream provider disappears or a dependency breaks. The steps above still apply; some confirmations cannot be obtained, and the receipt records that as an exception rather than pretending otherwise.

**Gate.** Teardown is evidenced rather than asserted. A decommissioning that cannot show what was revoked, what was retained, and when authority ended has not completed. A verifier holding a record signed by this identity can place it before or after that moment, or report that it cannot.

---

## 4. Applying the lifecycle

### 4.1 Adapting controls you already run

An organization operating a mature secure development lifecycle should not start over. The productive move is to ask, control by control, which of the five assumptions it depends on, and then extend it.

- Controls resting on **assumption 1** need a runtime counterpart. Build-time gates keep their value for the conventional parts of the system, and gain an admission gate and continuous verification alongside.
- Controls resting on **assumption 2** need their definition of *artifact* widened. Change control, review requirements, and rollback procedures largely transfer once instructions and configuration sit inside the boundary.
- Controls resting on **assumption 3** need delegation modeled explicitly. Existing identity infrastructure is usually adequate; what is missing is treating an agent as a principal holding constrained, traceable authority.
- Controls resting on **assumption 4** need baselining added. Test suites keep their role and stop being the sole evidence for production behavior.
- Controls resting on **assumption 5** need residue enumeration. Existing decommissioning runbooks typically cover provisioned resources and miss everything the agent created.

Migration cost concentrates in the first and last of these. Most organizations already have some version of the middle three and have simply not applied them to agents.

### 4.2 Where each assumption is repaired

| Assumption | Primary phase | Reinforced at |
|---|---|---|
| 1. Behavior fixed at build | Scoping and design | Admission, runtime, maintenance |
| 2. Reviewable artifact is code | Development | Supply chain, maintenance |
| 3. Identity is a service account | Admission and deployment | Runtime |
| 4. Testing approximates production | Admission and deployment | Runtime |
| 5. Retirement is deletion | Decommissioning | Reflection and knowledge consolidation |

No assumption is repaired by a single phase, which is the point of framing the lifecycle this way. A gate is only as good as the evidence produced upstream of it and the enforcement downstream.

---

## 5. Open questions

Questions the working group considers unsettled, offered as an agenda rather than as gaps papered over. Two questions that appeared in the first draft, observability as a distinct concern and modes of retirement, have since been answered and moved to section 6.

1. **Scoping by deployment pattern.** Whether lifecycle obligations should be modulated by how autonomous a deployment is (a model answering questions, a model calling tools, a single agent, an agent coordinating others, an agent composing its own network), and if so, whether the modulation reduces obligations at low autonomy or only reduces the effort of meeting them. A scoping matrix along these lines was proposed in June [^12]; the group's only position so far is that any such matrix is a set of example patterns, not a universal decomposition.

2. **Intervention semantics.** Where the capability to halt an agent belongs, how termination cascades to work already delegated, and how completion is verified across in-flight transactions. There is a reasonable argument that termination is the wrong primitive, and that throttling or falling back to a deterministic path serves better in systems where an abandoned transaction is itself a harm. The behavioral monitoring control [^11] leaves open whether it owns the halt or only the decision to halt.

3. **Evidence portability.** Whether the evidence a gate produces can be made portable enough for a third party to evaluate a procured agent against this lifecycle without access to the supplier's internals. A related question, what a verifier may conclude when evidence is absent, is being worked through on its own RFC [^13]: absence is neither conformance nor violation, and the third answer needs a name.

4. **What is lost at retirement.** Section 3.8 asks organizations to enumerate undocumented dependencies and undocumented knowledge before an agent retires. Whether the lifecycle should require a handover artifact for these, and what it would contain, is unsettled.

---

## 6. Positions of the working group

This paper is meant to carry the working group's opinions, not only a survey of other people's. This section is where those opinions live. It is deliberately a table rather than prose, so a position can be added in one line, dated, and traced to the discussion that produced it.

### 6.1 How a position gets in

A position is a claim the group has argued and settled, at least for now. It enters this table only with a date and a source: a meeting whose minutes record it, or a GitHub thread where it was reached. Positions can be reopened. When one is, the old row stays and a new row supersedes it, so the paper keeps the history of what the group used to think and why it changed.

The group produces positions in two ways. Some fall out of ordinary work, such as an RFC review that converges. Others come from a deliberate exercise: a meeting opens with a short review of one influential paper or post, the presenter states one claim from it to argue with, and the room argues. Each such session ends with a position the group either writes here or explicitly declines to take. A position nobody writes down did not happen.

### 6.2 Positions taken

| Date | Question | Position | Source |
|---|---|---|---|
| 2026-07-01 | Are the category sets this paper uses (deployment levels, architecture layers) a universal decomposition? | No. They are examples of patterns. Presenting them as universal creates consensus friction without adding precision | ADLC minutes, 7/1; scoping matrix [^12] |
| 2026-08-12 | Is System Governance a lifecycle phase? | No. Governance supplies authorization; the phases execute it. Dropped from the phase list | ADLC minutes, 8/12 |
| 2026-08-12 | Does this lifecycle restate conventional package and dependency supply chain practice? | No. That belongs to the Supply Chain workstream. This paper covers what goes beyond model signing: provenance and trust tiers for models, prompts, tools, and retrieval sources | ADLC minutes, 8/12; section 3.2 |
| 2026-08-19 | When mapping this lifecycle to the CoSAI Risk Map, widen existing entries or add new ones? | Add new entries, so a control has something specific to attach to. File an RFC or issue before any PR | ADLC minutes, 8/19 |
| 2026-08-27 | Does this paper specify containment mechanisms? | No. Containment is a separate Workstream 4 paper. This paper requires that containment posture be decided and verified, and cites that paper for how | WS4 minutes, 8/27; section 2.1 |
| 2026-09-01 to 09-14 | Is observability a distinct component of an agentic system? | The record is not new: it is the audit record repository the Risk Map already has. What is new is what you do with it: a baseline, drift and anomaly detection, and a response path. That is a control, and it is fail-closed | RFC #175 withdrawn, RFC #195 filed [^11] |
| 2026-09-09 to 09-14 | Is decommissioning reversible? Does it have modes? | Decommissioning ends the agent's authority to act and is terminal. Anything reversible is a Runtime or Maintenance state. There are no modes; there are organization-defined parameters | ADLC minutes, 9/9; RFC #170 as amended [^10] |
| 2026-09-09 | Where does the working group keep its record? | In GitHub. The paper is reviewed on its pull request. Google Docs and Slack are scratch space | ADLC minutes, 9/9 |
| *planned* | Is the harness, rather than the model, where an agent's behavior is determined and changed? If so, do Maintenance and Reflection carry more weight than section 3 gives them? | *To be argued. First paper-review session, scheduled for 2026-09-23, on Weng's harness engineering post [^14]* | |

---

## 7. Takeaways and conclusion

The case for treating agent development as its own lifecycle does not rest on agents being new, or important, or fast-moving. It rests on five specific assumptions that existing practice encodes and that agentic systems violate. Each violation is identifiable, each has a consequence that can be stated in terms of when assurance must be established, and each maps to a phase.

Framed that way, the lifecycle is a modest instrument. It adds a design phase because behavior is not settled at build. It widens the reviewable artifact because policy lives in prose. It makes identity a gated event because authority travels through delegation. It adds baselining because tests no longer stand in for production. It makes retirement a verified teardown because agents leave residue.

An organization already running a mature secure development lifecycle is closer to this than it may expect. The useful question is not whether to adopt a new framework, but which of its existing controls rest on an assumption that no longer holds.

A reader who disagrees with a phase is invited to attack the assumption it derives from. That is the argument this structure is built to expose. A reader who disagrees with a position in section 6 is invited to reopen it, with a source.

---

## 8. References

[^1]: NIST. *Secure Software Development Framework (SSDF), SP 800-218.* https://csrc.nist.gov/pubs/sp/800/218/final
[^2]: NIST. *Secure Software Development Practices for Generative AI and Dual-Use Foundation Models, SP 800-218A.* https://csrc.nist.gov/pubs/sp/800/218/a/final
[^3]: OWASP. *Software Assurance Maturity Model (SAMM).* https://owaspsamm.org/
[^4]: OWASP. *Top 10 for Large Language Model Applications* and *Agentic Security Initiative.* https://genai.owasp.org/
[^5]: Center for Internet Security. *CIS Controls v8.1 AI Agent Companion Guide.* https://learn.cisecurity.org/controls-v8-1-ai-agent-companion-guide
[^6]: ISO/IEC. *42001:2023, Information technology — Artificial intelligence — Management system.* https://www.iso.org/standard/42001
[^7]: Claxton, Louis. *The AI-Native SDLC Playbook*, 21 August 2026. https://claude.com/blog/the-ai-native-sdlc-playbook
[^8]: CoSAI. *Secure AI Tooling Risk Map.* https://github.com/cosai-oasis/secure-ai-tooling
[^9]: NIST. *Security and Privacy Controls for Information Systems and Organizations, SP 800-53 Rev. 5.* https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
[^10]: CoSAI WS4. *RFC: Add Decommissioning as an ADLC Phase and as CoSAI Lifecycle Stage 9.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/170
[^11]: CoSAI WS4. *RFC: Agent Behavioral Monitoring as a CoSAI Risk Map control.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/195
[^12]: CoSAI WS4. *Taxonomy for framing and scoping ADLC during security assessments.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/130
[^13]: CoSAI WS4. *RFC: Evidence sufficiency, and what a verifier may conclude when evidence is absent.* https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/189
[^14]: Weng, Lilian. *Harness Engineering for Self-Improvement*, 4 July 2026. https://lilianweng.github.io/posts/2026-07-04-harness/

---

## 9. Contributors and acknowledgements

**Workstream leads**

- Sarah Novotny
- Ian Molloy, IBM
- Raghu Yeluri, Intel
- Alex Polyakov, Adversa AI

**Editor**

- Courtenay Ngo, Microsoft

**Working group leads**

- Courtenay Ngo, Microsoft
- Emrick Donadei, Google
- Jennings Aske, SailPoint
- Matthew Gladney, NVIDIA
- Emeritus: Parul Singh, Red Hat, who wrote the scope document and the working analysis this paper is drawn from

**Contributors**

Participants in the lifecycle work from which this paper is drawn, listed alphabetically by surname. Credit here is for participation in the discussions that produced the phase model; per-section attribution follows as prose lands.

- Jamilu Abdullahi
- Salim Afiune Maya
- Sanjeev Agarwal
- Justin Albrethsen
- Doyin Awofodu
- Kevin Calloway
- John Cavanaugh
- Brett Connor, Cisco
- Kathleen Goeschel, Red Hat
- Yassine Ilmi
- Jason Keirstead
- David LaBianca, Google
- Valdez Ladd
- Chooi Low
- Victor Lu
- Alan Messer
- Nicolai Nielsen
- Karttik Panda
- David Pierce
- Susmitha Pillarisetty
- Rithikha Rajamohan
- J.R. Rao
- Caroline Rocha
- Daniel Rohrer, NVIDIA
- Raymond Sheh
- Xiaokui Shu
- Imran Siddique, Microsoft
- Kapil Singh
- Akila Srinivasan
- Bill Stout, ServiceNow
- Arthit Suriyawongkul
- Harish Thanneer
- Sebastian Wu

**Programme management**

- Claudia Rauch, OASIS

**Reviewers**

*To be listed.*

---

## Appendix A. Gate summary

| # | Phase | Gate |
|---|---|---|
| 1 | Scoping and design | Intended use, autonomy bounds, blast radius, classification, identity model, containment posture, and threat model recorded before procurement |
| 2 | Supply chain | Every component inventoried, with known provenance and an assigned trust tier |
| 3 | Development | Policy surface under change control at parity with code |
| 4 | Admission and deployment | Identity bound, prerequisites verified, baseline recorded. Unmet prerequisites block deployment |
| 5 | Runtime | Continuous enforcement, evidence, and demonstrated intervention capability |
| 6 | Reflection and knowledge consolidation | Nothing becomes durable without provenance and a policy check |
| 7 | Maintenance | No change to the policy surface or a prerequisite reaches production without re-baselining |
| 8 | Decommissioning | Teardown evidenced, not asserted; terminal state and its effective time published |

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

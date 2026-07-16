# ADLC Controls (Draft): Development, Admission/Deployment, Runtime

**Workstream:** WS4, SIG ADLC
**Status:** Draft contribution for phase-owner review
**Date:** 2026-07-15

**Contributor:** [@imran-siddique](https://github.com/imran-siddique) Imran Siddique, Opaque Systems

**Source:** [ADLC Scope Definition](adlc-scope-doc.md)

---

## About this contribution

This document proposes candidate controls for three ADLC phases: Development (DV), Admission/Deployment (AD), and Runtime (RT). It is offered to the phase owners as raw material, not as a finished catalog.

It re-contributes the controls from [PR #121](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/pull/121), which was auto-closed on 2026-07-06 when the `reorg` branch merged and was deleted. This version is re-anchored to `main` and reworked to fit the drafting methodology the SIG ratified since then.

### How this aligns with the current SIG process

The SIG drafts risks in the shared Google Doc first, reviews them live, and lands controls only for confirmed gaps (agendas of 6/17, 6/24, 7/8). This draft respects that order:

- **Risks come first.** Each control names the risk it mitigates. Canonical risk IDs are left as `pending` until the SIG risk-doc assigns them; the intent is to attach these controls to the risk entries the phase owners are drafting, not to front-run them.
- **Technology-agnostic.** Every control is stated as a requirement on the agent, independent of any product. Reference implementations are listed as examples, including the [Agent Governance Toolkit (AGT)](https://github.com/microsoft/agent-governance-toolkit) alongside at least one alternative per control. AGT is an exemplar, not a requirement.
- **Transitive mapping.** Risk to control to CoSAI component, per the schema walked through on 6/17. No control maps directly to a component without a risk.
- **Persona-based.** Personas follow the [CoSAI persona guide](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/personas-full.md), not job titles.

Control ID format matches the checklist scheme discussed by the SIG: `ADLC-{Phase}-{Type}{Seq}`, where `{Type}` is `I` (Implement) or `A` (Audit). IDs here are provisional and expected to collide with parallel contributions; resolve during review.

### Maturity levels

| Level | Name | When it applies |
|-------|------|-----------------|
| **L1** | Essential | Every agent deployment |
| **L2** | Standard | Production deployments handling sensitive data or taking state-changing actions |
| **L3** | Advanced | High-capability, low-oversight autonomous agents with broad tool access |

L1 and L2 stand on their own. L3 is aspirational for most teams.

### A note on L3 and hardware attestation

Several L3 entries reference a Trusted Execution Environment (TEE) measuring a hash into a hardware attestation report. Treat this as defense-in-depth under an explicit operator-trust assumption, not an absolute trust anchor. Published work on confidential-computing silicon (for example BadRAM, and physical interposer attacks in the TEE.fail line of research) shows that current TEEs raise the bar against software-level and remote adversaries but do not guarantee integrity against an adversary with physical control of the host. L3 TEE controls are worth adopting where they fit the threat model; they should not be presented to auditors as unconditional guarantees.

### No performance claims

This draft states no latency or overhead numbers. Enforcement that is synchronous and inline adds latency; teams should measure it against their own workload and set a budget rather than rely on a quoted figure.

---

## Development (DV)

**Owner(s):** Sanjeev Agarwal, Parul Singh ([@husky-parul](https://github.com/husky-parul))

**Scope reminder:** Design, configuration, and initial hardening of agent components. ADLC implements Agent System Instructions (prompts, policies, permissions, tool manifests, memory rules, RAG source trust) and Agent Input/Output Handling logic. It audits orchestration, infrastructure, model, and application prerequisites.

### Implement controls

#### ADLC-DV-I01: Policy as code with a formal schema

- **Maturity:** L1
- **Persona:** Agent Developers
- **CoSAI component:** Agent System Instructions
- **Risk addressed** (pending SIG risk ID): Governance rules that live only in a system prompt are probabilistic and can be overridden by prompt injection or model drift. Unversioned, unreviewed rules cannot be audited or reproduced.
- **Control:** Express all agent governance rules (tool allowlists, data-access conditions, approval requirements) in a version-controlled, formally schema'd policy artifact, not in the system prompt. The schema declares at least: rule name, condition, action (`allow` / `deny` / `audit` / `require_approval`), and description. Policy changes go through the same review as application code.
- **Verification:** Confirm the policy artifact is in version control with review requirements matching application code. Confirm no governance rule exists only in the system prompt. Confirm the policy passes its schema validator with no errors.
- **Reference implementations:** Open Policy Agent (Rego), AWS Cedar, OpenFGA. AGT policy bundles are one such implementation.

#### ADLC-DV-I02: Tool manifest and explicit allowlisting

- **Maturity:** L1 (allowlist), L2 (parameter schemas and data-classification labels), L3 (manifest binding attested at admission)
- **Persona:** Agent Developers
- **CoSAI component:** Agent System Instructions, enforced at Agent Input Handling
- **Risk addressed** (pending SIG risk ID): Excessive agency. An agent with an open-ended tool surface can be induced to call tools it was never intended to use, or to pass sensitive data to the wrong tool.
- **Control:** Define an explicit allowlist of the tools the agent may call, with parameter schemas and data-classification labels (for example PII, PHI, internal). Deny by default: any tool call not on the allowlist is refused before it reaches the tool, without involving the model in the decision. The tool manifest is a bound artifact of the agent's integrity record (see ADLC-AD-I02) and is re-attested when changed.
- **Verification:** Attempt a call to a tool not on the allowlist and confirm it is denied. Change the manifest without re-attesting and confirm the integrity check flags the mismatch.
- **Reference implementations:** MCP tool schemas with a deny-by-default gateway, function-calling allowlists enforced by a policy engine (OPA/Cedar). AGT binds the tool manifest into the Agent Manifest as one such implementation.

#### ADLC-DV-I03: Input and output handling for injection and content quality

- **Maturity:** L1 (input scanning and output gating), L2 (tool-response / MCP scanning), L3 (scanning attested in a TEE, subject to the L3 caveat above)
- **Persona:** Agent Developers, Agentic Security Framework Developers
- **CoSAI component:** Agent Input Handling, Agent Output Handling
- **Risk addressed** (pending SIG risk ID): Prompt injection through untrusted inputs; tool-response poisoning (schema drift, typosquatting, hidden instructions in tool output); data exfiltration and unsafe content in outputs.
- **Control:** Scan all inputs for injection before they reach the reasoning core, separating trusted commands from untrusted data. Evaluate outputs against a quality and safety gate before release, and block outputs that fail. Scan tool and MCP-server responses for schema drift, typosquatting, and injected instructions.
- **Verification:** Submit direct-injection and context-manipulation inputs and confirm they are blocked before the reasoning core. Submit an output that fails the gate and confirm it is blocked. Return a poisoned tool response and confirm it is detected.
- **Reference implementations:** Open-source injection classifiers and guardrail models (for example Llama Guard, Rebuff), MCP security scanners. AGT bundles an input injection detector, an output quality gate, and a tool-response scanner as one such implementation.

---

## Admission / Deployment (AD)

**Owner(s):** Justin Albrethsen

**Scope reminder:** Validation, testing, and controlled promotion to production behind a prerequisite verification gate. ADLC implements identity establishment, registration, adversarial testing, and behavioral baselining. It audits (the gate) that identity, credential, and platform prerequisites are in place; if the audit fails, deployment is blocked.

The Admission risk set drafted by Justin on 6/24 (agent impersonation including agent-as-human and agent-spoofing, misattribution, orphaned agents, privilege escalation, irrevocable or orphaned access, scope creep) is the intended anchor for the identity and integrity controls below.

### Implement controls

#### ADLC-AD-I01: Cryptographically verifiable agent identity with a human sponsor

- **Maturity:** L1
- **Persona:** Agent Developers, Agentic Security Framework Developers
- **CoSAI component:** Agent System Instructions (identity)
- **Risk addressed** (maps to Admission risks 6/24): Agent impersonation, misattribution, and orphaned agents. Without a verifiable, sponsor-bound identity, an agent's actions cannot be reliably attributed and rogue agents cannot be distinguished from sanctioned ones.
- **Control:** Assign every agent a unique, cryptographically verifiable identity bound to a keypair before admission, and associate it with a verified human or organizational sponsor. No orphan agents. The identity persists across deployments, upgrades, and sessions. An agent without a registered identity cannot pass the admission gate.
- **Verification:** Attempt to deploy an agent with no registered identity and confirm the gate blocks it. Confirm the identity resolves to the expected keypair and sponsor record.
- **Reference implementations:** W3C Decentralized Identifiers (DIDs) with Ed25519, SPIFFE/SPIRE SVIDs, X.509 workload certificates. AGT uses a `did:mesh:<id>` scheme bound to a verified human sponsor as one such implementation.

#### ADLC-AD-I02: Signed integrity record binding the agent's defining artifacts

- **Maturity:** L2 (software-signed record), L3 (record hash measured into a TEE attestation, subject to the L3 caveat above)
- **Persona:** Agent Developers, Agentic Security Framework Developers
- **CoSAI component:** Agent System Instructions, supply-chain provenance
- **Risk addressed** (pending SIG risk ID): Tampering or drift between the agent that was registered and the agent that runs; supply-chain substitution of a bound artifact.
- **Control:** Produce and sign an integrity record at registration that binds the agent's defining artifacts, for example: system prompt, policy bundle, tool manifest, model identity and digest, RAG corpus reference, memory baseline, decision-trace schema, delegation scope, supply-chain provenance (SLSA), and human-approval records. Any post-registration change to a bound artifact invalidates the record and forces re-attestation. The record is verified at the admission gate; a mismatch blocks deployment.
- **Verification:** Change the system prompt after registration without re-attesting and confirm the gate detects the mismatch and blocks deployment.
- **Reference implementations:** in-toto and SLSA attestations, Sigstore signing, IETF SCITT for transparency. AGT calls this record the Agent Manifest; in a TEE deployment its hash can be measured via cMCP, with the L3 caveat above.

#### ADLC-AD-I03: Pre-deployment adversarial red-team scan with a blocking threshold

- **Maturity:** L2
- **Persona:** Agent Developers, Agentic Security Framework Developers
- **CoSAI component:** Agent Reasoning Core, Agent Input/Output Handling
- **Risk addressed** (pending SIG risk ID): An agent ships with an exploitable policy gap or injection susceptibility that was never exercised before production.
- **Control:** Before production promotion, run an adversarial test suite against the agent with its actual policy bundle, covering at least: direct policy violations, prompt-injection attempts, contextual-confusion inputs, and valid requests to measure the false-positive rate. Block promotion if the safety-violation rate exceeds a threshold the organization sets for the action's risk tier. Record the suite and results as admission evidence.
- **Verification:** Introduce a policy gap that permits a privileged action via prompt injection and confirm the scan detects it and blocks promotion.
- **Reference implementations:** PyRIT, garak, promptfoo. AGT provides a safety-violation-rate gate over a labeled adversarial dataset as one such implementation.

#### ADLC-AD-I04: Behavioral baseline before promotion

- **Maturity:** L2
- **Persona:** Agent Developers
- **CoSAI component:** Agent Reasoning Core (observability)
- **Risk addressed** (pending SIG risk ID): Without a captured baseline, runtime drift and misbehavior have no reference to be measured against.
- **Control:** Before promotion, capture the distribution of action types, tool calls, and data-access patterns observed in staging, and store it as a reference artifact bound to the agent's integrity record. Runtime deviation beyond configured thresholds raises a drift alert (see ADLC-RT-I04).
- **Verification:** Confirm the baseline artifact is present before deployment is permitted. Inject anomalous behavior in staging and confirm the baseline captures and flags it.
- **Reference implementations:** Baselines built from OpenTelemetry traces, standard anomaly-detection baselining. AGT stores the baseline in the Agent Manifest as one such implementation.

### Audit controls (the gate)

> Deployment is blocked if an L1 audit control fails.

#### ADLC-AD-A01: Policy lint gate before deployment

- **Maturity:** L1 (lint in CI), L2 (deployment gate on error-level findings)
- **Persona:** Agent Developers, Agentic Security Framework Developers
- **CoSAI component:** Agent System Instructions (policy bundle)
- **Risk addressed** (pending SIG risk ID): Broken policy rules ship silently: unreachable rules, conditions that match the empty string (a common way a PII rule fails open), shadowed rules, and over-broad wildcards.
- **Control:** Lint the full policy bundle before deployment. Block on any error-level finding. Warn-level findings require documented human sign-off before promotion.
- **Verification:** Introduce an unreachable rule and confirm the linter flags it and the gate blocks promotion.
- **Reference implementations:** `opa check` and Regal for Rego, Cedar's validator, conftest. AGT provides a policy linter as one such implementation.

#### ADLC-AD-A02: Replay a policy change against production traces before activation

- **Maturity:** L2
- **Persona:** Agent Developers, Agentic Security Framework Developers, Security & Risk Officers (CISO/CRO)
- **CoSAI component:** Agent System Instructions (policy bundle), decision audit trace
- **Risk addressed** (pending SIG risk ID): A policy change silently denies actions that used to be allowed, or allows actions that used to be denied, with no review before it goes live.
- **Control:** Before activating a policy change, replay the last N production decisions under the new policy and produce a diff of what would change. A human reviewer signs off on the diff before activation. This is the change-control process for governance policy.
- **Verification:** Introduce a change that blocks a previously-allowed production action and confirm the diff surfaces it and activation is gated on sign-off.
- **Reference implementations:** Policy decision logs replayed through the policy engine (OPA decision logs, Cedar). AGT provides a policy-replay diff over recorded decisions as one such implementation.

---

## Runtime (RT)

**Owner(s):** Parul Singh ([@husky-parul](https://github.com/husky-parul)), Susmitha Pillarisetty, Ian Molloy ([@imolloy](https://github.com/imolloy)), Sunil Arora

**Scope reminder:** Active monitoring, enforcement, and continuous compliance while the agent runs. ADLC implements per-action identity verification, real-time policy enforcement, decision-trace logging, drift detection, circuit breakers, and human escalation. It audits (continuously) that platform identity validation and prerequisite health hold.

### Implement controls

#### ADLC-RT-I01: Pre-action policy evaluation gate

- **Maturity:** L1
- **Persona:** Agent Developers, Agentic Security Framework Developers
- **CoSAI component:** Agent Input Handling (pre-invocation)
- **Risk addressed** (pending SIG risk ID): When the only control is in the model layer, an agent can report success on a prohibited action because nothing deterministic stopped it. This is excessive agency in its most direct form.
- **Control:** Intercept every action (tool call, API call, state-changing operation) and evaluate it against the active policy before it executes. Evaluation is synchronous and inline in a deterministic layer, not in the model. A denied action returns a policy-denied result, not a model refusal. Enforcement adds latency; measure and budget it for your workload.
- **Verification:** Submit prompts requesting prohibited actions and confirm they return a policy-denied result rather than a model refusal. Measure evaluation latency under load against your own budget.
- **Reference implementations:** An OPA or Cedar policy decision point invoked inline, or a policy-enforcing sidecar or gateway. AGT provides an inline pre-action gate as one such implementation.

#### ADLC-RT-I02: Execution privilege tiers by reversibility

- **Maturity:** L2 (reversible and read-only tiers), L3 (highest tier with out-of-band human authorization)
- **Persona:** Agentic Security Framework Developers, Agent Developers
- **CoSAI component:** Agent Input Handling (authorization)
- **Risk addressed** (pending SIG risk ID): Privilege escalation and irreversible action. An agent takes a high-blast-radius action it should never have been able to reach.
- **Control:** Classify every action into a privilege tier by reversibility and administrative scope (for example: read-only or sandboxed, reversible writes, irreversible or privileged, emergency or administrative). Enforce the boundaries structurally, so an agent operating in a low tier cannot execute a high-tier action regardless of model output. The highest tier requires out-of-band human authorization and cannot be self-authorized by any agent.
- **Verification:** Attempt a privileged action from a low-tier agent and confirm denial. Attempt a highest-tier action with no out-of-band approval and confirm denial.
- **Reference implementations:** Capability-based sandboxing, ring or tier models enforced by a policy engine. AGT provides a four-tier execution-ring model with an out-of-band human witness for the top tier as one such implementation.

#### ADLC-RT-I03: Tamper-evident decision audit chain

- **Maturity:** L1 (append-only logging), L2 (hash chain with a verifier), L3 (anchored to an external transparency log)
- **Persona:** Agentic Security Framework Developers, Security & Risk Officers (CISO/CRO)
- **CoSAI component:** Agent Output Handling, observability
- **Risk addressed** (pending SIG risk ID): Audit records are altered or deleted after the fact, leaving no defensible evidence of what the agent did or why an action was allowed.
- **Control:** Record every governance decision (allow, deny, require_approval) in an append-only, hash-chained log where each entry's hash includes the prior entry's. A modified entry breaks every downstream hash, so tampering is self-reporting. For higher integrity, anchor the chain to an external transparency log.
- **Verification:** Modify a historical entry and confirm verification fails at that entry and every entry after it.
- **Reference implementations:** Merkle or hash-chained logs, RFC 9162-style transparency, IETF SCITT, Sigstore Rekor. AGT provides a hash-chained decision logger with a verify step and an optional SCITT/TRACE anchor as one such implementation.

#### ADLC-RT-I04: Governance-aware SLOs and circuit breaker

- **Maturity:** L2 (SLO monitoring), L3 (automated circuit breaker with human review to resume)
- **Persona:** Agentic Security Framework Developers, Security & Risk Officers (CISO/CRO)
- **CoSAI component:** observability, Agent Reasoning Core
- **Risk addressed** (pending SIG risk ID): A fully available agent that violates policy on every call passes traditional availability and latency SLOs. Nothing catches misbehavior that is not an outage.
- **Control:** Define SLOs that capture governance behavior, not just availability: a policy-compliance indicator (share of actions passing policy), task success rate, and behavioral-drift indicators against the baseline from ADLC-AD-I04. A sustained breach isolates the agent through a circuit breaker and requires human review before it resumes.
- **Verification:** Inject policy violations above the configured burn threshold and confirm the breaker isolates the agent within the window, and that it cannot resume without human review.
- **Reference implementations:** SRE error-budget and burn-rate alerting over OpenTelemetry metrics, with an automated isolation hook. AGT provides a policy-compliance SLI and an automated circuit breaker as one such implementation.

#### ADLC-RT-I05: Human escalation for approval-required actions

- **Maturity:** L2 (approval workflow), L3 (out-of-band approval path for the highest tier)
- **Persona:** Agent Developers, Security & Risk Officers (CISO/CRO)
- **CoSAI component:** Agent Input Handling
- **Risk addressed** (pending SIG risk ID): An agent bypasses a required approval by retrying, rephrasing, or waiting, and takes a high-impact action without a human in the decision.
- **Control:** Route any action marked `require_approval` to a human approval workflow and block execution until an approval token is presented. The block is structural: retrying or rephrasing does not clear it. Approvers see full context: parameters, data-classification label, and the specific rule that triggered escalation. The highest privilege tier uses an out-of-band approval path outside the agent's execution context.
- **Verification:** Trigger an approval-required action and confirm execution is blocked. Attempt to bypass by retrying without a token and confirm it stays blocked.
- **Reference implementations:** Human-in-the-loop approval workflows with out-of-band tokens. AGT provides a structural approval block with an out-of-band path for its highest privilege tier as one such implementation.

#### ADLC-RT-I06: Reasoning-loop and runaway detection with a hard stop

- **Maturity:** L2
- **Persona:** Agentic Security Framework Developers
- **CoSAI component:** Agent Reasoning Core
- **Risk addressed** (pending SIG risk ID): A stuck or looping agent repeats an action, burns token and cost budget, or amplifies a harmful action, with no structural limit.
- **Control:** Monitor the action history for looping (action repetition above a threshold), iteration count above a hard cap, and token-budget exhaustion. On detection, terminate the agent and record the termination reason and the action history at the time of the stop in the audit chain. This is a structural hard stop, not a prompt-layer request to the model to stop.
- **Verification:** Build an agent that loops on one action and confirm the hard stop fires at the configured thresholds and the audit record captures the reason.
- **Reference implementations:** Iteration caps, repetition detectors, and token budgets in agent frameworks. AGT triggers an automated hard stop on these conditions as one such implementation.

### Audit controls (continuous)

#### ADLC-RT-A01: Continuous identity verification per action

- **Maturity:** L2 (identity plus credential and trust checks), L3 (hardware-attested identity, subject to the L3 caveat above)
- **Persona:** Agentic Security Framework Developers
- **CoSAI component:** identity
- **Risk addressed** (pending SIG risk ID): A stale, expired, or over-privileged credential keeps acting; an inactive or compromised agent continues to be trusted with no re-check.
- **Control:** Before each tool call or state-changing action, verify the agent's identity resolves to a valid keypair with a current sponsor, the presented credential is within its time-to-live and has authorized uses remaining, and any trust signal meets the per-action threshold. Where a trust score is used, apply decay continuously so inactivity lowers trust rather than preserving it.
- **Verification:** Present an expired credential and confirm denial. Present a valid credential for an agent whose trust has decayed below the action threshold and confirm denial.
- **Reference implementations:** Short-TTL credentials with continuous authorization, SPIFFE SVID rotation. AGT verifies the DID, credential TTL, and a decaying trust score per action as one such implementation.

#### ADLC-RT-A02: Policy bundle integrity verification at runtime

- **Maturity:** L2 (software hash check), L3 (hardware-attested hash, subject to the L3 caveat above)
- **Persona:** Agentic Security Framework Developers, Security & Risk Officers (CISO/CRO)
- **CoSAI component:** policy bundle
- **Risk addressed** (pending SIG risk ID): An operator hot-swaps the policy bundle during a live session, so the policy actually enforced no longer matches the policy that was admitted and reviewed.
- **Control:** Continuously verify that the hash of the policy bundle active at runtime matches the hash recorded at admission. Any deviation, including a mid-session swap, is flagged as a critical integrity violation and logged to the audit chain.
- **Verification:** Swap the active bundle during a running session and confirm the check fires and records the violation.
- **Reference implementations:** Runtime hash comparison against the admitted bundle, signed-bundle verification. In a TEE deployment the hash can be measured for remote verification (AGT via cMCP), subject to the L3 caveat above.

---

## References

- [ADLC Scope Definition](adlc-scope-doc.md)
- [CoSAI persona guide](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/personas-full.md)
- [CoSAI Risk Map components](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/components-full.md)
- [NIST SP 800-218 (SSDF)](https://csrc.nist.gov/pubs/sp/800/218/final)
- [Agent Governance Toolkit (AGT)](https://github.com/microsoft/agent-governance-toolkit), MIT-licensed, cited throughout as one reference implementation

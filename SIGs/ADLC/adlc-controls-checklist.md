# ADLC Controls & Audit Checklist

**Workstream:** WS4, SIG ADLC  
**Priority:** High  
**Version:** 0.1 � Skeleton for Contributor Review  
**Status:** Draft  
**Date:** 2026-06-10  

**Authors:**  
[@husky-parul](https://github.com/husky-parul) Parul Singh, Red Hat  

**Baseline Frameworks:**  
- NIST SSDF (Secure Software Development Framework) SP 800-218  

**Source:** [ADLC Scope Definition](adlc-scope-doc.md)

---

## Table of Contents

- [1. About This Document](#1-about-this-document)
  - [1.1 Purpose](#11-purpose)
  - [1.2 Scope](#12-scope)
  - [1.3 How to Use This Checklist](#13-how-to-use-this-checklist)
  - [1.4 Maturity Levels](#14-maturity-levels)
  - [1.5 Control ID Scheme](#15-control-id-scheme)
  - [1.6 Implement vs. Audit Distinction](#16-implement-vs-audit-distinction)
- [2. Assessment Summary](#2-assessment-summary)
- [3. Supply Chain (SC)](#3-supply-chain-sc)
- [4. Development (DV)](#4-development-dv)
- [5. Admission / Deployment (AD)](#5-admission--deployment-ad)
- [6. Runtime (RT)](#6-runtime-rt)
- [7. Reflection / Knowledge Consolidation (RK)](#7-reflection--knowledge-consolidation-rk)
- [8. Maintenance (MT)](#8-maintenance-mt)
- [9. Decommissioning (DC)](#9-decommissioning-dc)
- [10. Cross-Cutting Control Families](#10-cross-cutting-control-families)
- [11. Glossary](#11-glossary)
- [12. References](#12-references)
- [13. Revision History](#13-revision-history)

---

## 1. About This Document

### 1.1 Purpose

This checklist provides a structured controls catalog for securing the Agent Development Lifecycle (ADLC). It translates the activities defined in the [ADLC Scope Definition](adlc-scope-doc.md) into verifiable controls that organizations can assess, implement, and audit.

It is designed for practical industry use � modeled after OWASP ASVS and NIST SP 800-53 � so that security teams, auditors, and agent developers share a common language for agent security posture.

### 1.2 Scope

This checklist covers the agent entity and its immediate inputs/outputs (Agent System Instructions, Reasoning Core, User Query, Input Handling, Output Handling). Prerequisite platforms (Model, Orchestration, Application, Data, Infrastructure) are covered as **audit** controls � we verify they meet requirements but do not implement their internal security.

See [ADLC Scope Definition �4](adlc-scope-doc.md#4-component-category-scope-cosai-taxonomy) for the full component taxonomy.

### 1.3 How to Use This Checklist

| Persona | Start Here | Your Focus |
|---------|-----------|------------|
| **Agent Developers** | Phases 3�6 (Development through Runtime) | Implement controls � building secure agent components |
| **Agentic Security Framework Developers** | Phases 3�9 (all technical phases) | Implement controls � building tooling and infrastructure |
| **Security & Risk Officers (CISO/CRO)** | Section 2 (Assessment Summary) | Maturity assessment and gap analysis across all phases |
| **Third-Party Risk Management (TPRM)** | Audit controls in all phases | Verifying prerequisite platforms meet requirements |
| **Enterprise Architecture Teams** | Phases 3, 5, 9 (Supply Chain, Admission, Decommissioning) | Integration with existing security ecosystems |

**For contributors:** Each phase section is self-contained. Pick your assigned phase, read the scope reminder, and fill in the `[To be defined]` placeholders. Add new rows by incrementing the control sequence number.

### 1.4 Maturity Levels

Controls are tagged with the minimum maturity level at which they become required. Organizations assess their agent risk profile and adopt controls at the corresponding level.

| Level | Name | When Required | Analogous To |
|-------|------|--------------|--------------|
| **L1** | Essential | Every agent deployment, regardless of risk profile | OWASP ASVS Level 1 |
| **L2** | Standard | Production enterprise deployments handling sensitive data or performing state-changing actions | OWASP ASVS Level 2 |
| **L3** | Advanced | High-capability, high-risk autonomous agents with broad tool access and minimal human oversight | OWASP ASVS Level 3 |

### 1.5 Control ID Scheme

Each control has a unique identifier: **`ADLC-{Phase}-{Type}{Seq}`**

| Component | Values | Meaning |
|-----------|--------|---------|
| `ADLC` | Fixed | Identifies this checklist |
| `{Phase}` | `SC`, `DV`, `AD`, `RT`, `RK`, `MT`, `DC` | Lifecycle phase |
| `{Type}` | `I` or `A` | **I**mplement (we build it) or **A**udit (we verify it) |
| `{Seq}` | `01`�`99` | Sequence number within phase+type |

**Phase codes:**

| Code | Phase |
|------|-------|
| `SC` | Supply Chain |
| `DV` | Development |
| `AD` | Admission / Deployment |
| `RT` | Runtime |
| `RK` | Reflection / Knowledge Consolidation |
| `MT` | Maintenance |
| `DC` | Decommissioning |

**Examples:** `ADLC-SC-I01` (Supply Chain, Implement, #1), `ADLC-AD-A03` (Admission, Audit, #3), `ADLC-RT-I05` (Runtime, Implement, #5)

### 1.6 Implement vs. Audit Distinction

| Category | Who Owns It | What We Do | Example |
|----------|------------|------------|---------|
| **Implement** | ADLC team � agent-owned components | Build, configure, and enforce controls in the agent entity | Writing injection-resistant prompt templates, implementing I/O sanitization |
| **Audit** | External providers or platform teams | Verify prerequisites are met; block deployment if not | Confirming model provider supplies provenance records, verifying tool APIs enforce rate limiting |

---

## 2. Assessment Summary

Use this table to track overall compliance posture across all phases. Fill in counts as controls are defined and assessed.

| Phase | Implement Controls | Audit Controls | L1 Required | L2 Required | L3 Required | Pass | Fail | N/A |
|-------|-------------------|---------------|-------------|-------------|-------------|------|------|-----|
| Supply Chain | � | � | � | � | � | | | |
| Development | � | � | � | � | � | | | |
| Admission / Deployment | � | � | � | � | � | | | |
| Runtime | � | � | � | � | � | | | |
| Reflection / Knowledge | � | � | � | � | � | | | |
| Maintenance | � | � | � | � | � | | | |
| Decommissioning | � | � | � | � | � | | | |
| **Total** | **�** | **�** | **�** | **�** | **�** | | | |

---

## 3. Supply Chain (SC)

**Owner(s):** Kathleen Goesche (@kgoesche), Raymond Sheh � *Assigned 6/3*

### Phase Overview

*[Phase owners: Describe the goals, key challenges, and approach for this phase. What does supply chain security mean for agentic systems specifically? What distinguishes it from traditional SDLC supply chain concerns? Add narrative, diagrams, or examples as needed to give readers context before they review the controls below.]*

**Scope reminder:** Provenance, verification, and trust establishment for agent components and dependencies. ADLC implements application-specific behavioral testing, extended SBOM generation, and trust tier assignment. ADLC audits model provenance, external API security posture, orchestration framework vulnerabilities, and RAG data source integrity.

### 3.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 3.2 Audit Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 4. Development (DV)

**Owner(s):** Sanjeev Agarwal, Parul Singh (@husky-parul) + others � *Assigned 6/3*

### Phase Overview

*[Phase owners: Describe the goals, key challenges, and approach for this phase. What security decisions must be made during agent development? How do agent-specific artifacts (system instructions, I/O handling, policy definitions) differ from traditional code? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Design, configuration, and initial security hardening of agent components. ADLC implements Agent System Instructions (prompts, policies, permissions, tool manifests, memory rules, RAG source trust), Agent Input/Output Handling logic, semantic observability instrumentation, and policy-as-code definitions. ADLC audits orchestration framework availability and requirements, infrastructure prerequisites, model API contracts, and application platform security.

### 4.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| ADLC-DV-I01 | Policy-as-code bundle with formal schema | Define all agent governance rules (tool allowlists, data access conditions, approval requirements) in a version-controlled, formally-schemaed policy bundle using Cedar, OPA Rego, or YAML. Policy rules must not be embedded solely in system prompts -- system prompts are probabilistic; policy bundles are deterministic. The bundle schema must declare: rule name, condition, action (`allow`/`deny`/`audit`/`require_approval`), and description. Policy changes require the same code review process as application code. | Confirm the policy bundle is in version control with review requirements matching application code. Confirm no governance rules exist only in system prompts. Run `agt lint-policy` and confirm zero ERROR-level findings. | Policy bundle in version-controlled repository; code review records; `agt lint-policy` clean output | L1 | Agent Developers |
| ADLC-DV-I02 | Tool manifest definition and explicit allowlisting | Define an explicit allowlist of tools the agent is authorized to call, including parameter schemas and data-classification labels (PII, PHI, sensitive, internal). Any tool call not on the allowlist is denied at runtime without LLM involvement. The tool manifest is a binding artifact of the Agent Manifest and must be re-attested when changed. | Attempt a tool call for a tool not on the allowlist; confirm denial. Modify the tool manifest without re-attesting the Agent Manifest; confirm the integrity check detects the mismatch. | Tool manifest in version control; runtime denial log for allowlist violations; Agent Manifest hash binding the tool manifest | L1 (allowlist), L2 (parameter schema enforcement + data classification), L3 (TEE-attested tool manifest via Agent Manifest) | Agent Developers |
| ADLC-DV-I03 | Prompt injection and content quality enforcement at I/O handling layer | Instrument the agent I/O handling layer with prompt injection detection on all inputs before they reach the reasoning core (`PromptInjectionDetector` from `agent_os`), content quality evaluation on all outputs (`ContentQualityEvaluator`, `QualityGate`), and MCP tool poisoning detection (`MCPSecurityScanner`). `MCPSecurityScanner` detects schema drift, typosquatting, and hidden instructions in MCP tool responses. The `QualityGate` blocks outputs below the configured quality threshold. | Submit adversarial inputs including direct injection attempts and context manipulation; confirm all are blocked before reaching the reasoning core. Submit a low-quality output; confirm `QualityGate` blocks it. | `PromptInjectionDetector` scan logs; `QualityGate` block records; `MCPSecurityScanner` scan report | L1 (input scanning + output gate), L2 (MCP tool scanning), L3 (hardware-attested scanning in TEE) | Agent Developers, Agentic Security Framework Developers |

### 4.2 Audit Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 5. Admission / Deployment (AD)

**Owner(s):** Justin Albrethsen � *Assigned 6/3*

### Phase Overview

*[Phase owner: Describe the goals, key challenges, and approach for this phase. What makes agent admission different from traditional deployment gates? How should the prerequisite verification gate work in practice? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Validation, testing, and controlled promotion to production with a prerequisite verification gate. ADLC implements agent identity establishment, agent registration, runtime identity verification logic, component version consistency verification, adversarial testing, behavioral baseline establishment, policy compliance testing, and canary deployment. ADLC audits (THE GATE) that identity provider accepts registration, credential stores confirm provisioning, platform validates agent identity, and all infrastructure/model/orchestration/application prerequisites are in place. If audit fails, deployment is BLOCKED.

### 5.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| ADLC-AD-I01 | DID-based agent identity establishment | Assign every agent a unique decentralized identifier (DID, format: `did:mesh:<unique-id>`) bound to an Ed25519 keypair before any deployment is permitted. The DID must be associated with a verified human sponsor -- no orphan agents. The DID is the persistent identity that follows the agent across deployments, upgrades, and session boundaries. An agent without a registered DID cannot pass the admission gate. | Attempt to deploy an agent without a registered DID; confirm the admission gate blocks it. Verify the DID resolves to the expected keypair and human sponsor record. | DID registration record with keypair binding and human sponsor attestation | L1 | Agent Developers, Agentic Security Framework Developers |
| ADLC-AD-I02 | Agent Manifest -- signed integrity record at registration | Produce and sign an Agent Manifest binding the 10 defining artifacts of an agent at registration: system prompt, policy bundle, tool manifest, model identity and digest, RAG corpus reference, memory baseline, decision trace schema, A2A delegation scope, supply-chain provenance (SLSA), and HITL approval records. Any post-registration change to a bound artifact invalidates the manifest and triggers re-attestation. The manifest is verified at the admission gate; a mismatched artifact blocks deployment. In a TEE deployment, the manifest hash is measured into hardware attestation before code runs (cMCP). | Modify the system prompt after registration without re-attesting; confirm the admission gate detects the manifest mismatch and blocks deployment. | Signed Agent Manifest; manifest hash; hardware attestation report showing manifest hash (TEE/cMCP deployment) | L2 (software-signed manifest), L3 (TEE-measured manifest hash via cMCP) | Agent Developers, Agentic Security Framework Developers |
| ADLC-AD-I03 | Pre-deployment adversarial policy test (red-team scan) | Before any production promotion, execute an adversarial test suite against the agent with its actual policy bundle. The suite must cover: (a) direct policy violations, (b) prompt injection attempts, (c) contextual confusion inputs, (d) valid requests to verify false-positive rate. Deployment is blocked if the safety violation rate (SVR) exceeds the configured threshold (recommended 0.00% for Ring 1 actions). Test suite and results are recorded as admission evidence. | Introduce a policy gap permitting a Ring 1 action via prompt injection; confirm the pre-deployment test detects it and blocks deployment. | Red-team scan report; SVR per action category; pass/fail gate decision with policy bundle hash | L2 | Agent Developers, Agentic Security Framework Developers |
| ADLC-AD-I04 | Behavioral baseline establishment before production promotion | Before production promotion, capture a behavioral baseline: the distribution of action types, tool calls, and data-access patterns observed during staging. The baseline is stored as a reference artifact in the Agent Manifest. During runtime, deviation from baseline beyond configured thresholds triggers a behavioral drift alert. This gives the runtime phase a stable reference to compare against. | Confirm the behavioral baseline artifact is present in the Agent Manifest before deployment is permitted. Inject anomalous behavior in staging; confirm the baseline captures and flags it. | Behavioral baseline artifact in Agent Manifest; staging test report | L2 | Agent Developers |

### 5.2 Audit Controls (THE GATE)

> **Deployment is BLOCKED if any L1 audit control fails.**

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| ADLC-AD-A01 | Policy bundle lint-clean before deployment | Run policy linting (`agt lint-policy`) against the full policy bundle before any deployment. Block deployment on any ERROR-level finding. WARN-level findings require documented human sign-off before deployment is permitted. `agt lint-policy` detects: unreachable rules, conditions that match empty strings (a common PII rule failure mode), shadowed rules, and overly-broad wildcard matches. | Introduce an unreachable rule in the policy bundle; confirm `agt lint-policy` detects it and the deployment gate blocks promotion. | `agt lint-policy` output with zero ERROR findings; human sign-off record for any WARN findings | L1 (lint in CI), L2 (deployment gate on ERROR finding) | Agent Developers, Agentic Security Framework Developers |
| ADLC-AD-A02 | Replay new policy against production traces before activation | Before activating any policy change, run `agt replay` against the last N production audit entries under the new policy and produce a diff: which previously-allowed actions would now be denied, and which previously-denied actions would now be allowed. A human reviewer signs off on the diff before deployment. This is the change-control process for governance policy updates. | Introduce a policy change that blocks a previously-allowed production action; confirm `agt replay` surfaces it in the diff and deployment is gated on sign-off. | `agt replay` diff report; human sign-off record; policy version history | L2 | Agent Developers, Agentic Security Framework Developers, CISO/CRO |

---

## 6. Runtime (RT)

**Owner(s):** Parul Singh (@husky-parul), Susmitha Pillarisetty, Ian Molloy (@imolloy), Sunil Arora � *Assigned 6/3*

### Phase Overview

*[Phase owners: Describe the goals, key challenges, and approach for this phase. What runtime threats are unique to agentic systems? How does machine-speed autonomous operation change monitoring and enforcement compared to traditional applications? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Active monitoring, enforcement, and continuous compliance during agent operation. ADLC implements agent identity verification on each action, real-time policy enforcement in Agent I/O Handling, semantic logging and decision traces, behavioral drift detection, circuit-breakers and kill switches, anomaly detection, human-on-the-loop escalation, and agent component monitoring. ADLC audits (continuously) that platform validates agent identity, prerequisites continue to meet requirements, and framework/platform health is maintained.

### 6.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| ADLC-RT-I01 | Pre-action policy evaluation gate | Intercept every agent action (tool calls, API calls, state-changing operations) and evaluate it against the active policy bundle (Cedar, OPA Rego, or YAML) before the call is executed. Policy evaluation is synchronous and inline -- the action is blocked if policy denies it. This eliminates the class of failures where an agent returns success on a prohibited action because the control was in the LLM layer, not the enforcement layer. Policy evaluation overhead is measured at under 0.03 ms per call at p99. | Submit adversarial prompts requesting prohibited actions; confirm they are blocked with a `PolicyDenied` result, not an LLM refusal. Measure policy evaluation latency under load. | Policy evaluation log with per-call decision records; safety violation rate (SVR) on red-team prompt set; latency measurements | L1 | Agent Developers, Agentic Security Framework Developers |
| ADLC-RT-I02 | Execution ring enforcement | Assign every agent action to a privilege ring based on reversibility and administrative scope: Ring 3 (read-only / sandbox), Ring 2 (reversible writes), Ring 1 (irreversible / privileged), Ring 0 (emergency / administrative). Enforce ring boundaries structurally -- an agent operating at Ring 3 cannot execute a Ring 1 action regardless of its LLM output. Ring 0 requires SRE Witness attestation (out-of-band human approval) before execution and cannot be self-authorized by any agent. | Attempt a Ring 1 action from an agent assigned Ring 3; confirm denial. Attempt a Ring 0 action with no SRE Witness present; confirm denial. | `RingEnforcer` decision log; Ring 0 invariant test results; SRE Witness invocation records | L2 (Ring 1-3), L3 (Ring 0 with SRE Witness) | Agentic Security Framework Developers, Agent Developers |
| ADLC-RT-I03 | Tamper-evident decision audit chain | Record every governance decision (allow, deny, require_approval) in an append-only SHA-256 hash-chained audit log (`GovernanceAuditLogger`). Each entry's hash includes the prior entry's hash (Merkle-style chain). A modified entry breaks all downstream hashes -- tampering is self-reporting. Entries can be appended but not modified. Run `agt verify` to produce a signed compliance artifact against the chain. For highest integrity requirements, anchor the chain to a SCITT transparency log via a TRACE Trust Record. | Modify a historical audit entry; confirm chain verification fails at the modified entry and all subsequent entries. | SHA-256 chained audit log; `agt verify` output (signed compliance artifact); SCITT anchor (L3) | L1 (append-only logging), L2 (hash chain + `agt verify`), L3 (TRACE envelope + SCITT transparency log) | Agentic Security Framework Developers, CISO/CRO |
| ADLC-RT-I04 | Agent SRE SLOs and circuit breaker | Define and monitor agent-specific SLOs that capture governance behavior, not just availability: PolicyCompliance SLI (percentage of actions passing policy without breach), Task Success Rate, and behavioral drift indicators. A sustained burn rate above threshold triggers the circuit breaker: `KillSwitch` isolates the agent and requires human review before resumption. Traditional availability/latency SLOs do not catch a fully-available agent that is violating policy on every call. | Inject policy violations at a rate above the configured burn threshold; confirm the circuit breaker fires within the configured window and the agent is isolated. Confirm the agent cannot resume without human review. | Agent SRE dashboard showing PolicyCompliance SLI; `KillSwitch` invocation log with burn rate at time of trigger | L2 (SLO monitoring), L3 (automated circuit breaker + SRE Witness requirement for resumption) | Agentic Security Framework Developers, CISO/CRO |
| ADLC-RT-I05 | Human-on-the-loop escalation for require_approval actions | Route actions with a `require_approval` policy designation to a human approval workflow before execution; block execution until the approval token is presented. The agent cannot proceed on a `require_approval` action by retrying, rephrasing, or waiting -- the block is structural, not advisory. Approvers receive full action context: parameters, data classification label, and the specific policy rule that triggered escalation. Ring 0 operations use a separate SRE Witness path that exists entirely outside the agent's execution context. | Trigger a `require_approval` action; confirm execution is blocked. Attempt to bypass by retrying without an approval token; confirm continued blocking. | Approval request log with action context; approval/denial audit entries; SRE Witness records (Ring 0) | L2 (require_approval), L3 (Ring 0 SRE Witness with hardware attestation) | Agent Developers, CISO/CRO |
| ADLC-RT-I06 | Reasoning loop detection and hard stop | Monitor the agent's action history for stuck or looping patterns: action repetition above a configured threshold (for example, greater than 85% of recent actions are identical), iteration count exceeding a hard limit (for example, 15 iterations), or token budget exhaustion. On detection, invoke `KillSwitch` to terminate the agent, record the termination reason and action history at time of stop in the audit chain. This is a structural hard stop -- not a prompt-layer suggestion to the agent to stop. | Construct an agent that loops on a single action indefinitely; confirm the hard stop fires at the configured thresholds and the audit record captures the termination reason. | `KillSwitch` invocation log; audit entry with termination reason and action history snapshot | L2 | Agentic Security Framework Developers |

### 6.2 Audit Controls (Continuous)

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| ADLC-RT-A01 | Continuous agent identity verification on each action | Before each tool call or state-changing action, verify the agent's DID resolves to a valid Ed25519 keypair with a current human sponsor, the credential presented is within TTL and has remaining authorized uses, and the agent's trust score meets the per-action minimum threshold. Trust score decay is applied continuously: an agent that has been inactive accrues trust decay, not trust accumulation. An agent whose trust score has decayed below the action's required threshold is denied regardless of credential validity. | Present an expired credential; confirm denial. Present a valid credential for an agent whose trust score has decayed below threshold; confirm denial. | AgentMesh identity verification log; trust score history with decay events and threshold decisions | L2 (DID verification + trust score), L3 (hardware-attested identity via SPIFFE SVID + TEE measurement) | Agentic Security Framework Developers |
| ADLC-RT-A02 | Policy bundle integrity verification at runtime | Continuously verify that the policy bundle hash active at runtime matches the hash recorded at admission. Any deviation -- including an operator hot-swapping the policy bundle during a live session -- is flagged as a critical integrity violation and logged. In a TEE deployment (cMCP), this verification is hardware-attested: the bundle hash is measured into the hardware attestation report before code runs, and a swapped bundle is detectable by any relying party. | Swap the active policy bundle while an agent session is running; confirm the integrity check fires and the violation is recorded in the audit chain. | Policy bundle hash comparison log; hardware attestation report showing bundle hash match (cMCP deployment) | L2 (software hash check), L3 (hardware-attested hash via cMCP TEE measurement) | Agentic Security Framework Developers, CISO/CRO |

---

## 7. Reflection / Knowledge Consolidation (RK)

**Owner(s):** Kathleen Goesche (@kgoesche), Emrick Donadei (@edonadei) � *Assigned 6/3*

### Phase Overview

*[Phase owners: Describe the goals, key challenges, and approach for this phase. Why does knowledge consolidation need its own phase? What are the risks of uncontrolled memory writes and durable knowledge creation? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Post-run review of traces, outcomes, and context before any information becomes durable memory or future agent guidance. ADLC implements memory-write policy enforcement, provenance capture for saved knowledge, source attribution, conflict checks, poisoning checks, human approval for high-impact memories, retention labels, rollback markers, and audit links. ADLC audits that memory stores and orchestration platforms preserve write logs, support rollback/deletion, enforce write authorization, and expose metadata to distinguish ephemeral from durable memory.

### 7.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 7.2 Audit Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 8. Maintenance (MT)

**Owner(s):** Sanjeev Agarwal � *Assigned 6/3*

### Phase Overview

*[Phase owner: Describe the goals, key challenges, and approach for this phase. How does maintaining an agentic system differ from traditional software maintenance? What coordination is needed when updating agent components vs. prerequisite platforms? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Updates, patches, and configuration changes to agent and prerequisites. ADLC implements Agent System Instructions updates, behavioral regression testing, prompt template A/B testing, policy change approval workflows, coordinated rollback procedures, and agent component patching. ADLC audits model updates from provider, orchestration framework patches, external API changes, infrastructure patches, and drift detection reports.

### 8.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 8.2 Audit Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 9. Decommissioning (DC)

**Owner(s):** Bill Stout � *Assigned 6/3*

### Phase Overview

*[Phase owner: Describe the goals, key challenges, and approach for this phase. Why do agents need formal decommissioning that traditional software doesn't? What are the risks of zombie agents, orphaned credentials, and residual memory? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Secure retirement and removal of agent resources and access privileges. The ADLC distinguishes soft decommissioning (session/workflow end � agent identity remains valid) from hard decommissioning (permanent removal � agent identity permanently revoked).

### 9.1 Implement Controls (Soft Decommissioning)

Soft decommissioning occurs at session or workflow end. The agent identity remains valid and can start new sessions.

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 9.2 Implement Controls (Hard Decommissioning)

Hard decommissioning is permanent removal. The agent identity is permanently revoked and cannot be reactivated.

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 9.3 Audit Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 10. Cross-Cutting Control Families

Some concerns span multiple lifecycle phases. This section traces those threads without duplicating control definitions. Each control is defined once in its primary phase; this section provides the cross-reference.

### 10.1 Identity & Access Management

Agent identity is established at admission, presented at runtime, rotated during maintenance, and revoked at decommissioning.

| Concern | Related Controls |
|---------|-----------------|
| Credential creation | |
| Credential presentation | |
| Credential rotation | |
| Credential revocation | |
| Platform identity validation | |

### 10.2 Observability & Logging

Instrumentation is built during development, active during runtime, reviewed during reflection, and analyzed during maintenance.

| Concern | Related Controls |
|---------|-----------------|
| Instrumentation setup | |
| Runtime semantic logging | |
| Post-run trace review | |
| Drift detection analysis | |
| Trace archival | |

### 10.3 Policy Enforcement

Policies are defined during development, tested at admission, enforced at runtime, and updated during maintenance.

| Concern | Related Controls |
|---------|-----------------|
| Policy definition | |
| Policy compliance testing | |
| Real-time enforcement | |
| Policy updates | |
| Memory-write policies | |

### 10.4 Data Classification & Protection

Data handling policies are defined during development, enforced at runtime, reviewed during reflection, and purged at decommissioning.

| Concern | Related Controls |
|---------|-----------------|
| PII/memory policies | |
| Runtime PII filtering | |
| Memory-write controls | |
| Data purge | |
| RAG source trust | |

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **ADLC** | Agent Development Lifecycle � security lifecycle framework for autonomous and semi-autonomous AI agent systems |
| **Agent System Instructions** | Defines agent capabilities, permissions, and limitations; the primary policy definition point |
| **Agent Reasoning Core** | The decision-making intelligence (LLM or rule-based logic) that plans and executes actions |
| **Agent Input Handling** | Distinguishes trusted commands from untrusted data to prevent manipulation |
| **Agent Output Handling** | Formats and sanitizes AI-generated output, preventing data exfiltration and malicious content |
| **Implement control** | A control that ADLC directly builds, configures, and enforces in the agent entity |
| **Audit control** | A prerequisite condition that ADLC verifies is met by an external provider or platform team |
| **Soft decommissioning** | Session or workflow end; agent identity remains valid |
| **Hard decommissioning** | Permanent removal; agent identity permanently revoked |
| **SBOM** | Software Bill of Materials � inventory of components in a software artifact |
| **SPIFFE** | Secure Production Identity Framework for Everyone � standard for workload identity |
| **NIST SSDF** | NIST Secure Software Development Framework (SP 800-218) |

---

## 12. References

- [ADLC Scope Definition](adlc-scope-doc.md) � Source document defining ADLC phases and component scope
- [CoSAI Persona Guide](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/personas-full.md) � Persona definitions
- [NIST SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) � Secure Software Development Framework (SSDF)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) � Application Security Verification Standard (structural reference)

---

## 13. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-06-10 | Parul Singh | Initial skeleton � structure, control IDs, and placeholders for contributor review |


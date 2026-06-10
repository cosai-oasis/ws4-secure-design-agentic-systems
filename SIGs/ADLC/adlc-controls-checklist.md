# ADLC Controls & Audit Checklist

**Workstream:** WS4, SIG ADLC  
**Priority:** High  
**Version:** 0.1 — Skeleton for Contributor Review  
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

It is designed for practical industry use — modeled after OWASP ASVS and NIST SP 800-53 — so that security teams, auditors, and agent developers share a common language for agent security posture.

### 1.2 Scope

This checklist covers the agent entity and its immediate inputs/outputs (Agent System Instructions, Reasoning Core, User Query, Input Handling, Output Handling). Prerequisite platforms (Model, Orchestration, Application, Data, Infrastructure) are covered as **audit** controls — we verify they meet requirements but do not implement their internal security.

See [ADLC Scope Definition §4](adlc-scope-doc.md#4-component-category-scope-cosai-taxonomy) for the full component taxonomy.

### 1.3 How to Use This Checklist

| Persona | Start Here | Your Focus |
|---------|-----------|------------|
| **Agent Developers** | Phases 3–6 (Development through Runtime) | Implement controls — building secure agent components |
| **Agentic Security Framework Developers** | Phases 3–9 (all technical phases) | Implement controls — building tooling and infrastructure |
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
| `{Seq}` | `01`–`99` | Sequence number within phase+type |

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
| **Implement** | ADLC team — agent-owned components | Build, configure, and enforce controls in the agent entity | Writing injection-resistant prompt templates, implementing I/O sanitization |
| **Audit** | External providers or platform teams | Verify prerequisites are met; block deployment if not | Confirming model provider supplies provenance records, verifying tool APIs enforce rate limiting |

---

## 2. Assessment Summary

Use this table to track overall compliance posture across all phases. Fill in counts as controls are defined and assessed.

| Phase | Implement Controls | Audit Controls | L1 Required | L2 Required | L3 Required | Pass | Fail | N/A |
|-------|-------------------|---------------|-------------|-------------|-------------|------|------|-----|
| Supply Chain | — | — | — | — | — | | | |
| Development | — | — | — | — | — | | | |
| Admission / Deployment | — | — | — | — | — | | | |
| Runtime | — | — | — | — | — | | | |
| Reflection / Knowledge | — | — | — | — | — | | | |
| Maintenance | — | — | — | — | — | | | |
| Decommissioning | — | — | — | — | — | | | |
| **Total** | **—** | **—** | **—** | **—** | **—** | | | |

---

## 3. Supply Chain (SC)

**Owner(s):** Kathleen Goesche (@kgoesche), Raymond Sheh — *Assigned 6/3*

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

**Owner(s):** Sanjeev Agarwal, Parul Singh (@husky-parul) + others — *Assigned 6/3*

### Phase Overview

*[Phase owners: Describe the goals, key challenges, and approach for this phase. What security decisions must be made during agent development? How do agent-specific artifacts (system instructions, I/O handling, policy definitions) differ from traditional code? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Design, configuration, and initial security hardening of agent components. ADLC implements Agent System Instructions (prompts, policies, permissions, tool manifests, memory rules, RAG source trust), Agent Input/Output Handling logic, semantic observability instrumentation, and policy-as-code definitions. ADLC audits orchestration framework availability and requirements, infrastructure prerequisites, model API contracts, and application platform security.

### 4.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 4.2 Audit Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 5. Admission / Deployment (AD)

**Owner(s):** Justin Albrethsen — *Assigned 6/3*

### Phase Overview

*[Phase owner: Describe the goals, key challenges, and approach for this phase. What makes agent admission different from traditional deployment gates? How should the prerequisite verification gate work in practice? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Validation, testing, and controlled promotion to production with a prerequisite verification gate. ADLC implements agent identity establishment, agent registration, runtime identity verification logic, component version consistency verification, adversarial testing, behavioral baseline establishment, policy compliance testing, and canary deployment. ADLC audits (THE GATE) that identity provider accepts registration, credential stores confirm provisioning, platform validates agent identity, and all infrastructure/model/orchestration/application prerequisites are in place. If audit fails, deployment is BLOCKED.

### 5.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 5.2 Audit Controls (THE GATE)

> **Deployment is BLOCKED if any L1 audit control fails.**

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 6. Runtime (RT)

**Owner(s):** Parul Singh (@husky-parul), Susmitha Pillarisetty, Ian Molloy (@imolloy), Sunil Arora — *Assigned 6/3*

### Phase Overview

*[Phase owners: Describe the goals, key challenges, and approach for this phase. What runtime threats are unique to agentic systems? How does machine-speed autonomous operation change monitoring and enforcement compared to traditional applications? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Active monitoring, enforcement, and continuous compliance during agent operation. ADLC implements agent identity verification on each action, real-time policy enforcement in Agent I/O Handling, semantic logging and decision traces, behavioral drift detection, circuit-breakers and kill switches, anomaly detection, human-on-the-loop escalation, and agent component monitoring. ADLC audits (continuously) that platform validates agent identity, prerequisites continue to meet requirements, and framework/platform health is maintained.

### 6.1 Implement Controls

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

### 6.2 Audit Controls (Continuous)

| ID | Control | Description | Verification | Evidence | Maturity | Persona |
|----|---------|-------------|--------------|----------|----------|---------|
| | | | | | | |

---

## 7. Reflection / Knowledge Consolidation (RK)

**Owner(s):** Kathleen Goesche (@kgoesche), Emrick Donadei (@edonadei) — *Assigned 6/3*

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

**Owner(s):** Sanjeev Agarwal — *Assigned 6/3*

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

**Owner(s):** Bill Stout — *Assigned 6/3*

### Phase Overview

*[Phase owner: Describe the goals, key challenges, and approach for this phase. Why do agents need formal decommissioning that traditional software doesn't? What are the risks of zombie agents, orphaned credentials, and residual memory? Add narrative, diagrams, or examples as needed.]*

**Scope reminder:** Secure retirement and removal of agent resources and access privileges. The ADLC distinguishes soft decommissioning (session/workflow end — agent identity remains valid) from hard decommissioning (permanent removal — agent identity permanently revoked).

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
| **ADLC** | Agent Development Lifecycle — security lifecycle framework for autonomous and semi-autonomous AI agent systems |
| **Agent System Instructions** | Defines agent capabilities, permissions, and limitations; the primary policy definition point |
| **Agent Reasoning Core** | The decision-making intelligence (LLM or rule-based logic) that plans and executes actions |
| **Agent Input Handling** | Distinguishes trusted commands from untrusted data to prevent manipulation |
| **Agent Output Handling** | Formats and sanitizes AI-generated output, preventing data exfiltration and malicious content |
| **Implement control** | A control that ADLC directly builds, configures, and enforces in the agent entity |
| **Audit control** | A prerequisite condition that ADLC verifies is met by an external provider or platform team |
| **Soft decommissioning** | Session or workflow end; agent identity remains valid |
| **Hard decommissioning** | Permanent removal; agent identity permanently revoked |
| **SBOM** | Software Bill of Materials — inventory of components in a software artifact |
| **SPIFFE** | Secure Production Identity Framework for Everyone — standard for workload identity |
| **NIST SSDF** | NIST Secure Software Development Framework (SP 800-218) |

---

## 12. References

- [ADLC Scope Definition](adlc-scope-doc.md) — Source document defining ADLC phases and component scope
- [CoSAI Persona Guide](https://github.com/cosai-oasis/secure-ai-tooling/blob/main/risk-map/tables/personas-full.md) — Persona definitions
- [NIST SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) — Secure Software Development Framework (SSDF)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — Application Security Verification Standard (structural reference)

---

## 13. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-06-10 | Parul Singh | Initial skeleton — structure, control IDs, and placeholders for contributor review |

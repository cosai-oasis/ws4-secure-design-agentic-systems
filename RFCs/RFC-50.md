
# Trust-Aware Dataplane for Agentic Systems

**Authors:**
* @husky-parul

## **Summary**

## Abstract

Agentic systems perform automated operations across services, tools, and infrastructure on behalf of users. These interactions often follow multi-hop paths — agent to agent, agent to tool, agent to resource — where each hop crosses a trust boundary. Traditional authorization mechanisms are designed for single-hop API access and do not provide consistent enforcement across such chains.

This RFC proposes a Trust-Aware Dataplane that enforces authorization decisions at runtime hop boundaries between agents, tools, and resources. The dataplane introduces sidecar-mediated hop enforcement, workload identity-based authorization, policy evaluation at runtime interaction boundaries, and a Trust Graph telemetry component that reconstructs interaction paths for observability and risk assessment. The design is protocol-agnostic and does not mandate any specific agent framework, tool protocol, or identity system.

## Table of Contents

1. [Summary](#1-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals](#3-goals)
4. [Non-Goals](#4-non-goals)
5. [Terminology](#5-terminology)
6. [Design Overview](#6-design-overview)
7. [Architecture](#7-architecture)
8. [Identity Model](#8-identity-model)
9. [Policy Enforcement Model](#9-policy-enforcement-model)
10. [Trust Graph Telemetry](#10-trust-graph-telemetry)
11. [Use Cases](#11-use-cases)
12. [Example Policy Model](#12-example-policy-model)
13. [Runtime Flow](#13-runtime-flow)
14. [Implementation Considerations](#14-implementation-considerations)
15. [Alternatives Considered](#15-alternatives-considered)
16. [Security Considerations](#16-security-considerations)
17. [Open Questions](#17-open-questions)
18. [Future Work](#18-future-work)
19. [Related Work](#19-related-work)

## 1. Summary

Agentic systems increasingly operate across multi-hop interaction paths:

```
User -> Agent -> Agent -> Tool -> Resource
User -> Agent -> Tool -> Resource
User -> Agent -> Agent -> Resource
```

At each hop, an entity acts on behalf of a prior entity. Traditional authorization is designed for direct caller-to-service interactions and does not address the chain of delegation that emerges when agents invoke other agents, call tools, or access resources on a user's behalf.

This RFC proposes a **Trust-Aware Dataplane** — a runtime enforcement layer that mediates every hop between agents, tools, and resources. The dataplane:

- **Enforces** authorization decisions at each hop boundary via sidecar proxies
- **Identifies** workloads using existing identity systems (SPIFFE, Kerberos, OAuth, platform-native)
- **Evaluates** policy against caller identity, target identity, resource, and action
- **Observes** interaction paths via a Trust Graph telemetry component that reconstructs the full interaction topology

The enforcement point sits outside the workload's trust boundary. A compromised agent cannot bypass or tamper with enforcement decisions made by its sidecar.

## 2. Problem Statement

AI agents capable of executing actions on behalf of users introduce new attack surfaces:

- **Prompt injection attacks** that cause agents to perform unintended operations
- **Compromised or misbehaving agents** that access resources beyond their intended scope
- **Unintended lateral movement** through agent-to-agent delegation chains
- **Privilege escalation** through tool access, where an agent gains capabilities beyond what the original user authorized
- **Opaque delegation chains** where the path from user intent to resource access is invisible to administrators

In production deployments, agents interact with other agents, invoke tools, and access resources across multiple hops. The interactions form a directed graph that is difficult to reason about, audit, or constrain using existing mechanisms.

Current infrastructure typically enforces policies at:

- **Workload placement** (e.g., scheduling constraints) — controls where code runs, not what it does at runtime
- **Service-level authentication** (e.g., mTLS, API keys) — verifies identity but does not evaluate whether a specific interaction should be permitted
- **Network policies** (e.g., network segmentation) — controls connectivity but cannot enforce resource-level or action-level access within a service

None of these mechanisms enforce policy at **runtime interaction boundaries** — the point where one entity delegates to another.

## 3. Goals

The Trust-Aware Dataplane aims to provide:

1. **Runtime hop enforcement.** Authorization decisions are evaluated at each interaction boundary between agents, tools, and resources — not only at ingress.

2. **Identity-based authorization.** Every workload (agent, tool, resource) carries a verifiable identity. Authorization decisions are made based on the identities of both caller and target.

3. **Identity system agnosticism.** The dataplane consumes identity signals from existing systems (SPIFFE, Kerberos, OAuth, platform-native identities) without mandating a specific provider.

4. **Minimal application changes.** Enforcement is mediated by sidecar proxies. Agent and tool implementations require no modification to participate in the dataplane.

5. **Framework independence.** Policy enforcement operates independently of agent frameworks, tool protocols, or orchestration systems. The dataplane enforces at the network boundary regardless of how the workload is implemented.

6. **Interaction observability.** A Trust Graph telemetry component emits structured data describing each hop, enabling reconstruction of full interaction paths for audit, anomaly detection, and risk assessment.

## 4. Non-Goals

This proposal does not attempt to:

- **Define a new identity system.** The dataplane consumes identity signals; it does not issue them.
- **Replace existing authorization frameworks.** The dataplane integrates with existing policy engines (e.g., OPA) as policy decision points.
- **Mandate specific credential technologies.** SPIFFE, Kerberos, OAuth, and platform-native identities are all valid inputs.
- **Mandate specific tool or agent protocols.** The dataplane operates at the network layer and is agnostic to application-level protocols between agents and tools.
- **Define agent behavior semantics.** The dataplane enforces interaction boundaries; it does not interpret or evaluate what agents do within those boundaries.

## 5. Terminology

| Term | Definition |
|------|-----------|
| **Agent** | A workload that acts on behalf of a user or another agent. Agents may invoke tools, access resources, or delegate to other agents. |
| **Tool** | A workload that provides a specific capability (e.g., code execution, database query, API call) invoked by an agent. |
| **Resource** | A data store, service, or external system accessed by agents or tools. |
| **Hop** | A single interaction between two entities (agent-to-agent, agent-to-tool, tool-to-resource, etc.). |
| **Sidecar Proxy** | A proxy co-located with each workload that intercepts inbound and outbound communication and acts as the policy enforcement point (PEP). |
| **Policy Enforcement Point (PEP)** | The sidecar proxy, which intercepts requests and enforces authorization decisions. |
| **Policy Decision Point (PDP)** | An external policy engine (e.g., OPA) that evaluates authorization queries and returns allow/deny decisions. |
| **Trust Graph** | A telemetry component that emits structured hop data and reconstructs the full interaction topology across a request's lifecycle. |
| **Principal** | The originating user or system identity on whose behalf an agent chain operates. |
| **Delegation Chain** | The sequence of hops from a principal through one or more agents to a final resource or tool. |

## 6. Design Overview

The Trust-Aware Dataplane introduces enforcement points between communicating workloads. Every interaction — agent to agent, agent to tool, tool to resource — passes through a sidecar proxy that evaluates whether the interaction is permitted before forwarding the request.

### Core Components

1. **Sidecar Proxy** (per workload) — intercepts all inbound and outbound traffic, extracts identity and request metadata, and enforces policy decisions. The proxy operates outside the workload's trust boundary.

2. **Workload Identity** — each workload carries a verifiable identity obtained from the deployment's identity system. The sidecar presents and validates these identities at each hop.

3. **Policy Evaluation** — at each hop, the sidecar constructs an authorization query from the caller identity, target identity, resource, and action, and sends it to a pluggable policy decision point.

4. **Trust Graph Telemetry** — sidecars emit structured telemetry at each hop. A Trust Graph component consumes this telemetry and reconstructs the full interaction topology, providing observability into delegation paths, anomaly detection, and audit trails.

## 7. Architecture

Each agent, tool, and resource runs with a sidecar proxy that intercepts inbound and outbound communication.

```
              ┌─────────────┐
              │       Principal      │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │   Sidecar    │◄──── Policy Decision Point
              │   (PEP)     │────► Trust Graph Telemetry
              ├──────────────┤
              │   Agent A    │
              └──────┬───────┘
                     │
         ┌───────────┴───────────┐
         │                       │
  ┌──────▼───────┐        ┌─────▼────────┐
  │   Sidecar    │        │   Sidecar    │
  │   (PEP)     │        │   (PEP)     │
  ├──────────────┤        ├──────────────┤
  │   Agent B    │        │   Tool X     │
  └──────┬───────┘        └──────┬───────┘
         │                       │
  ┌──────▼───────┐        ┌─────▼────────┐
  │   Sidecar    │        │   Sidecar    │
  │   (PEP)     │        │   (PEP)     │
  ├──────────────┤        ├──────────────┤
  │   Tool Y     │        │  Resource Z  │
  └──────────────┘        └──────────────┘
```

- Sidecars act as **policy enforcement points (PEPs)**.
- Before forwarding a request, the sidecar evaluates whether the interaction is permitted by querying a policy decision point.
- The enforcement point sits **outside the workload's trust boundary**. A compromised workload cannot alter enforcement decisions.
- Every hop — agent-to-agent, agent-to-tool, tool-to-resource — is mediated by the same enforcement mechanism.

## 8. Identity Model

The dataplane requires a trusted workload identity signal at each hop. Identity is used to determine who is calling, who is being called, and whether the interaction is permitted.

### Supported Identity Mechanisms

The architecture is intentionally identity-provider agnostic. Supported mechanisms include:

- **SPIFFE/SVID** — workload identity via X.509 certificates or JWT tokens
- **Kerberos tickets** — enterprise identity and delegation
- **OAuth2 access tokens** — scoped authorization tokens
- **Platform-native workload identities** — cloud provider or orchestrator-issued identities (e.g., Kubernetes service accounts, cloud IAM roles)

### Identity Principles

1. **The dataplane consumes identity signals; it does not issue them.** Identity issuance remains the responsibility of the deployment's identity infrastructure.

2. **Identity is verified at each hop.** The sidecar validates the caller's identity before evaluating policy. Identity is not trusted transitively across hops without explicit verification.

3. **Principal identity is preserved across hops.** The identity of the originating principal (user or system) is propagated through the delegation chain so that policy decisions can reference the original authority, not just the immediate caller.

## 9. Policy Enforcement Model

At each hop, the sidecar proxy constructs an authorization query and evaluates it against a policy decision point.

### Authorization Query Attributes

| Attribute | Description |
|-----------|-------------|
| `caller.identity` | Verified identity of the calling workload |
| `caller.type` | Type of the caller: `agent`, `tool`, `resource`, `principal` |
| `target.identity` | Identity of the target workload |
| `target.type` | Type of the target: `agent`, `tool`, `resource` |
| `action` | The operation being requested |
| `resource` | The specific resource being accessed (if applicable) |
| `principal.identity` | The originating principal on whose behalf the chain operates |

### Policy Decision

The sidecar sends the authorization query to a pluggable **policy decision point (PDP)**. The PDP evaluates the query against configured policy and returns one of:

- **Allow** — the request is forwarded to the target
- **Deny** — the request is rejected and an error is returned to the caller

The dataplane does not own the policy decision logic. It owns the enforcement point, the identity extraction, and the query construction. The policy decision is delegated to whatever engine is deployed (e.g., OPA, Cedar, custom policy services).

### Enforcement Properties

- **Fail-closed.** If the PDP is unreachable or returns an error, the default behavior is to deny the request.
- **Per-hop evaluation.** Policy is evaluated at every hop, not only at ingress. An agent permitted to call Tool X is not implicitly permitted to call Tool Y.
- **Bidirectional.** Sidecars enforce policy on both inbound (who can call me?) and outbound (who can I call?) traffic.

## 10. Trust Graph Telemetry

The Trust Graph is an observability component that provides the dataplane with visibility into interaction paths. It is optional but strongly recommended, as it enables capabilities beyond static policy enforcement.

### Telemetry Emission

At each hop, the sidecar emits a structured telemetry event containing attributes such as:

| Attribute | Description |
|-----------|-------------|
| `caller.identity` | Identity of the calling workload |
| `caller.type` | Type of caller |
| `target.identity` | Identity of the target workload |
| `target.type` | Type of target |
| `action` | Operation requested |
| `resource` | Resource accessed (if applicable) |
| `decision` | Policy decision (allow/deny) |
| `principal.identity` | Originating principal |
| `hop.timestamp` | Timestamp of the interaction |
| `hop.run_id` | Correlation identifier linking all hops in a single request chain |

These attributes are illustrative and may be extended, mapped or derived from existing identity claims and policy inputs depending on the deployment.

### Graph Reconstruction

A Trust Graph service consumes hop telemetry and reconstructs the full interaction topology for each request chain. The resulting graph is a directed acyclic graph (DAG) where:

- **Nodes** are typed entities (principal, agent, tool, resource)
- **Edges** represent interactions with associated metadata (action, decision, timestamp)

### Trust Graph Capabilities

The reconstructed graph enables:

- **Provenance queries** — "Why was this resource accessed, by whom, and on whose behalf?"
- **Anomaly detection** — scoring interaction patterns against historical baselines to detect novel edges, unusual fanout, depth anomalies, or capability overreach
- **Audit trails** — complete, tamper-resistant records of delegation chains for compliance and forensics
- **Risk signaling** — the Trust Graph can feed risk scores back to the policy decision point, enabling dynamic policy that accounts for runtime behavior patterns

**EDIT**: The attributes and structure described in this section are not intended to be a final or prescriptive schema but rather a starting point to anchor discussion. The goal is to evolve toward a standardized hop telemetry and authorization data model that aligns with existing ecosystems for example, identity and claim representations from JWT/OAuth, workload identities such as SPIFFE, and policy input models used by systems like OPA or Cedar. Wherever possible, the intent is to reuse and compose existing semantics rather than introduce a new end-to-end format.

## 11. Use Cases

The dataplane targets the following administrative controls.

### 11.1 Restrict where agents may run

Administrators can constrain agents to specific hosts, clusters, or environments. The sidecar enforces placement policy at runtime — even if an agent workload is scheduled on an unauthorized host, the sidecar denies its interactions.

### 11.2 Restrict agent-to-agent delegation

Administrators can control which agents are permitted to delegate to other agents. For example, a `chat-agent` may be permitted to delegate to `read-agent` but not to `admin-agent`.

### 11.3 Restrict agent-to-tool access

Administrators can control which tools are accessible to specific agents. For example, a `summary-agent` may access a `search` tool but not a `code-execution` tool.

### 11.4 Restrict tool resource access

Administrators can limit tools to specific resources. For example, a `database-query` tool may access `database:analytics` but not `database:credentials`.

### 11.5 Restrict outbound communication

Administrators can prohibit tools or agents from communicating with specific external hosts, preventing data exfiltration or unauthorized external API access.

### 11.6 Detect anomalous interaction patterns

Using Trust Graph telemetry, administrators can detect interaction patterns that deviate from historical baselines — novel delegation paths, unexpected resource access, or unusual interaction depth or fanout.

## 12. Example Policy Model

Example policy configuration (illustrative, not normative):

```yaml
agents:
  chat-agent:
    allowed_hosts:
      - node-ai-01
      - node-ai-02
    allowed_agents:
      - read-agent
      - summary-agent
    allowed_tools:
      - search
      - summarize
    denied_tools:
      - code-execution

  summary-agent:
    allowed_tools:
      - search
    allowed_resources:
      search:
        - index:public-docs

tools:
  database-query:
    allowed_resources:
      - database:analytics
    denied_hosts:
      - external:*
```

The policy schema is illustrative. Deployments integrate their own policy engines and schemas. The dataplane provides the authorization query attributes; the policy engine provides the decision logic.

## 13. Runtime Flow

### Example: Agent-to-agent-to-tool interaction

```
User -> Agent A -> Agent B -> Tool X -> Resource Z
```

**Step-by-step execution:**

1. **User sends request to Agent A.**
   - The ingress sidecar extracts the user's identity and stamps it as the principal.
   - The sidecar evaluates policy: is this principal permitted to interact with Agent A?
   - Decision: allow. Request is forwarded to Agent A.
   - Sidecar emits a Trust Graph telemetry event.

2. **Agent A delegates to Agent B.**
   - Agent A's outbound sidecar intercepts the request to Agent B.
   - The sidecar constructs an authorization query: caller=Agent A, target=Agent B, principal=User, type=agent-to-agent.
   - The sidecar queries the PDP. Decision: allow.
   - Agent B's inbound sidecar verifies Agent A's identity and evaluates inbound policy.
   - Both sidecars emit Trust Graph telemetry events.

3. **Agent B invokes Tool X.**
   - Agent B's outbound sidecar intercepts the request.
   - Authorization query: caller=Agent B, target=Tool X, principal=User, action=query, type=agent-to-tool.
   - PDP decision: allow.
   - Tool X's inbound sidecar verifies and evaluates.
   - Telemetry events emitted.

4. **Tool X accesses Resource Z.**
   - Tool X's outbound sidecar intercepts the request.
   - Authorization query: caller=Tool X, target=Resource Z, principal=User, resource=database:analytics, action=read, type=tool-to-resource.
   - PDP decision: allow.
   - Telemetry events emitted.

5. **Trust Graph reconstructs the full interaction path.**
   - All telemetry events are correlated by `hop.run_id`.
   - The Trust Graph service builds the interaction DAG: `User -> Agent A -> Agent B -> Tool X -> Resource Z`.
   - The graph is available for provenance queries, anomaly detection, and audit.

## 14. Implementation Considerations

The dataplane is designed to be modular. Potential implementation approaches include:

- **Sidecar proxies** — service mesh sidecar proxies (e.g., Envoy) with authorization filters that call out to policy decision points
- **Policy engines** — integration with existing engines such as OPA, Cedar, or custom policy services
- **Identity verification** — integration with SPIFFE/SPIRE, Kerberos, OAuth token introspection, or platform-native identity APIs
- **Telemetry pipeline** — Trust Graph telemetry emitted as OpenTelemetry spans, forwarded through standard collectors to a trace backend for graph reconstruction
- **Deployment models** — Kubernetes sidecar containers, ambient mesh approaches, or VM-based proxy deployments

The dataplane should remain modular so that deployments can integrate with their preferred identity, policy, and telemetry systems.

## 15. Alternatives Considered

### Identity-only enforcement

Restricting agent behavior solely through identity issuance (e.g., issuing narrowly-scoped credentials) does not address runtime interactions between services. An agent with valid credentials for Service A may still misuse that access in ways that identity alone cannot prevent.

### Application-level authorization

Embedding authorization logic inside agents or tools requires changes to application code and risks inconsistent enforcement. Each agent framework or tool implementation would need to independently implement authorization, leading to gaps and divergence.

### Network-only policies

Network segmentation controls connectivity between workloads but cannot enforce resource-level or action-level access within a service. An agent permitted network access to a tool endpoint cannot be further constrained to specific resources or actions using network policy alone.

### Gateway-only enforcement

Enforcing policy only at the ingress gateway provides perimeter security but does not govern agent-to-agent or agent-to-tool interactions within the deployment. Once past the gateway, lateral interactions are unconstrained.

## 16. Security Considerations

The security of the dataplane relies on:

1. **Trusted workload identity signals.** The identity presented by each workload must be verifiable and resistant to forgery. Compromised identity infrastructure undermines all enforcement decisions.

2. **Sidecar integrity.** The sidecar proxy must be protected from tampering by the workload it mediates. If a workload can bypass or modify its sidecar, enforcement is defeated. Deployment mechanisms should ensure sidecar integrity (e.g., Kubernetes admission control, read-only filesystems).

3. **Secure communication channels.** Communication between sidecars should be encrypted (e.g., mTLS) to prevent interception or spoofing of identity and policy signals.

4. **Correct policy configuration.** The dataplane enforces whatever policy is configured. Misconfigured policy (e.g., overly permissive rules) results in inadequate enforcement. Policy should be reviewed, version-controlled, and tested.

5. **PDP availability.** The dataplane defaults to fail-closed. If the policy decision point is unavailable, requests are denied. Deployments should ensure PDP availability and consider the operational impact of PDP outages.

6. **Principal identity integrity.** The principal identity set at ingress must not be modifiable by downstream workloads. If an agent can rewrite the principal header, it can impersonate arbitrary users.

## 17. Open Questions

The following questions remain open for further design discussion:

1. **Should a standard policy query schema be defined?** A common schema for authorization queries would improve interoperability across policy engines but may constrain flexibility.

2. **Should a separate policy decision broker be introduced?** A broker could abstract over multiple policy engines, enabling composite policy decisions, but adds architectural complexity.

3. **How should identity translation be handled?** In heterogeneous deployments, different segments may use different identity systems (e.g., SPIFFE in Kubernetes, Kerberos in enterprise). How identity is translated or federated across boundaries requires further design.

4. **How should delegation across agent chains be represented?** The current design propagates principal identity and evaluates policy per-hop. Whether additional delegation semantics are needed — such as constrained delegation, delegation depth limits, or delegation tokens — remains an open question.

5. **How should the Trust Graph feed back into enforcement?** The Trust Graph can produce risk scores and anomaly signals. The mechanism by which these signals influence real-time policy decisions (e.g., dynamic policy updates, inline risk scoring) requires further design.

## 18. Future Work

Potential extensions include:

- **Multi-signal authorization** — combining identity, Trust Graph risk scores, agent evaluation signals (output quality, safety, hallucination detection), and external threat intelligence into composite policy decisions
- **Attestation integration** — incorporating workload attestation (e.g., hardware-rooted attestation, software supply chain verification) into the identity and policy model
- **Standardized trust decision APIs** — defining common APIs for policy query and decision that enable interoperability across dataplane implementations
- **Delegation semantics** — designing explicit delegation representations (tokens, scoped credentials, delegation depth limits) for agent chains
- **Cross-domain federation** — enabling trust-aware enforcement across organizational and infrastructure boundaries

## 19. Related Work

- **SPIFFE / SPIRE** — Workload identity framework providing verifiable identities for distributed systems. The dataplane consumes SPIFFE identities as one supported identity mechanism.
- **Kerberos / IdM** — Enterprise authentication and identity management. Kerberos delegation semantics inform the delegation chain design space.
- **OAuth2 delegation** — Token-based authorization with scoped access. OAuth token semantics are relevant to per-hop authorization and credential scoping.
- **Service mesh architectures** — Sidecar proxy patterns (e.g., Envoy, Istio) provide the architectural foundation for the dataplane's enforcement model. The dataplane extends service mesh patterns with agent-aware policy and Trust Graph telemetry.
- **OpenTelemetry** — Distributed tracing and telemetry standards. The Trust Graph telemetry component builds on OpenTelemetry span semantics for hop-level observability.
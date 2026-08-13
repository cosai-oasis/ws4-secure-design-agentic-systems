# Identity Architecture Patterns for Agentic Systems

> **Playbook for CoSAI Deliverable #1: Identity Architecture Patterns**
>
> This guide provides architectural patterns for establishing cryptographic agent identity, verifiable credentials, and zero-trust authorization boundaries in agentic systems.

## Table of Contents

- [Overview](#overview)
- [Architecture Overview](#architecture-overview)
- [Key Terminology](#key-terminology)
- [How to Read This Playbook](#how-to-read-this-playbook)
- [Capability-Risk Classification: When to Use This Playbook](#capability-risk-classification-when-to-use-this-playbook)
- [Layer 1: Cryptographic Identity Foundation](#layer-1-cryptographic-identity-foundation)
- [Layer 2: Federated Identity Bridge](#layer-2-federated-identity-bridge)
- [Layer 3: Transparent Authorization Proxy](#layer-3-transparent-authorization-proxy)
- [Layer 4: Delegation Chain Preservation](#layer-4-delegation-chain-preservation)
- [Layer 5: Observable Trust](#layer-5-observable-trust)
- [Implementation Verification Checklist](#implementation-verification-checklist)
- [Putting It All Together: End-to-End Request Flow](#putting-it-all-together-end-to-end-request-flow)
- [Migration Strategy: Phased Adoption](#migration-strategy-phased-adoption)
  - [Phase 1: Foundation](#phase-1-foundation)
  - [Phase 2: Verifiable Credentials](#phase-2-verifiable-credentials)
  - [Phase 3: Federated Bridge + Transparent Proxy](#phase-3-federated-bridge--transparent-proxy)
  - [Phase 4: Delegation + Observability](#phase-4-delegation--observability)
  - [Phase 5: Enforce + Expand](#phase-5-enforce--expand)
  - [General Migration Principles](#general-migration-principles)
- [Measuring Success](#measuring-success)
- [Common Pitfalls](#common-pitfalls)
- [Real-World Example](#real-world-example)
- [Glossary](#glossary)
- [References](#references)
  - [CoSAI Whitepapers](#cosai-whitepapers)
  - [Standards and Specifications](#standards-and-specifications)
  - [CoSAI Threat Taxonomy](#cosai-threat-taxonomy)
  - [Tools](#tools)
  - [Implementation Examples](#implementation-examples)

---

## Overview

Agentic systems face unique identity challenges that traditional application identity models don't address. Agents operate with varying degrees of autonomy, make decisions on behalf of users, and interact with other agents in complex delegation chains. Without proper identity architecture, these systems are vulnerable to:

- **Agent impersonation** (MCP-T2) — Malicious actors spawning unauthorized agents or impersonating legitimate ones
- **Unauthorized delegation** (MCP-T1) — Agents performing actions beyond their authorized scope
- **Privilege escalation** (MCP-T3) — Agents exploiting weak identity boundaries to gain elevated access
- **Credential compromise** (MCP-T7) — Long-lived secrets leaked through agent memory or logs

Traditional identity patterns (API keys, service accounts with static passwords) fail in agentic systems because:

1. **Agents are ephemeral** — They spawn dynamically, making pre-provisioned credentials impractical
2. **Delegation chains are complex** — User → Agent A → Agent B requires preserving the full trust chain
3. **Audit requirements are strict** — "Which agent did what on behalf of whom?" must be answerable
4. **Zero-trust is essential** — Agents cannot be trusted by default, even within your infrastructure

This playbook presents a **5-layer identity architecture** that addresses these challenges through cryptographic identity, verifiable credentials, and transparent authorization proxies. The pattern is based on a working implementation combining SPIFFE/SPIRE, OAuth 2.0 token exchange (RFC 8693), and sidecar-based authorization enforcement.

### Architecture Overview

<table>
<thead>
<tr>
<th width="100%" style="text-align: center;">5-Layer Identity Architecture</th>
</tr>
</thead>
<tbody>
<tr style="background-color: #f0f8ff;">
<td style="text-align: center;"><strong>Layer 5: Observable Trust</strong><br>OpenTelemetry integration with JWT authentication attributes in trace spans</td>
</tr>
<tr style="background-color: #f5f5f5;">
<td style="text-align: center;"><strong>Layer 4: Delegation Chain Preservation</strong><br>RFC 8693 token exchange with actor claims to preserve "who did what on whose behalf"</td>
</tr>
<tr style="background-color: #f0f8ff;">
<td style="text-align: center;"><strong>Layer 3: Transparent Authorization Proxy</strong><br>Sidecar-based authorization enforcement (AuthBridge pattern) without modifying agent code</td>
</tr>
<tr style="background-color: #f0f8ff;">
<td style="text-align: center;"><strong>Layer 2: Federated Identity Bridge</strong><br>SPIFFE identity bridged to OAuth 2.0 via federated JWT authentication</td>
</tr>
<tr style="background-color: #f5f5f5;">
<td style="text-align: center;"><strong>Layer 1: Cryptographic Identity Foundation</strong><br>SPIFFE/SPIRE for short-lived X.509 and JWT certificates with automatic rotation</td>
</tr>
</tbody>
</table>

Each layer builds on the one below, creating defense-in-depth while maintaining separation of concerns.

### Key Terminology

This playbook uses terminology from the CoSAI security framework. Tool-specific terms (SPIFFE, AgentCard, AuthBridge, etc.) are defined in the [Glossary](#glossary) and introduced in context within each layer section.

<table>
<thead>
<tr>
<th width="20%">Term</th>
<th width="80%">Definition</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Agentic IAM</strong></td>
<td>Identity and Access Management designed for autonomous software agents. Extends traditional IAM (built for humans and static services) with ephemeral identities, delegation chains, context-aware policies, and behavioral monitoring.</td>
</tr>
<tr>
<td><strong>MCP-T* Threat Categories</strong></td>
<td>Threat taxonomy from the CoSAI whitepapers (<a href="https://www.coalitionforsecureai.org/wp-content/uploads/2026/04/agentic-identity-and-access-control.pdf">Agentic Identity and Access Management</a>, <a href="https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/model-context-protocol-security.pdf">Model Context Protocol Security</a>). Key categories: MCP-T1 (unauthorized actions), MCP-T2 (agent impersonation), MCP-T3 (privilege escalation), MCP-T7 (credential compromise), MCP-T9 (insufficient logging). See <a href="#cosai-threat-taxonomy">CoSAI Threat Taxonomy</a> in References for full definitions and mitigation mapping.</td>
</tr>
<tr>
<td><strong>OBO (On-Behalf-Of) Token</strong></td>
<td>A credential that carries both the agent ("actor") and the user or upstream service ("subject") identities. Enables authorization policies to evaluate both "who requested this" and "who is executing it". Implemented via RFC 8693 token exchange with <code>act</code> claims.</td>
</tr>
<tr>
<td><strong>ZSP (Zero Standing Privilege)</strong></td>
<td>Design principle ensuring no long-lived credentials exist. All access is provisioned just-in-time with credentials scoped to specific tasks and lifetimes measured in seconds to hours, not days or years.</td>
</tr>
<tr>
<td><strong>ABAC/PBAC</strong></td>
<td><strong>Attribute-Based Access Control</strong> — Policies evaluate dynamic attributes (agent risk score, current task, environment, data sensitivity) rather than static roles.<br><br><strong>Policy-Based Access Control</strong> — Authorization decisions driven by declarative policies (OPA Rego, Cedar) rather than hardcoded logic.</td>
</tr>
</tbody>
</table>

### How to Read This Playbook

This playbook serves different audiences with different needs. Use this guide to navigate to the most relevant sections:

<table>
<thead>
<tr>
<th width="20%">Persona</th>
<th width="35%">Your Goals</th>
<th width="45%">Recommended Reading Path</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>CISO / Risk Leader</strong></td>
<td>Understand security posture, risk mitigation, and compliance alignment</td>
<td>
<ol>
<li><strong>Capability-Risk Classification</strong> — Determine which agents need this architecture</li>
<li><strong>Overview</strong> — Threat landscape and why traditional IAM fails</li>
<li><strong>CoSAI Threat Taxonomy</strong> (References) — Which threats are mitigated</li>
<li><strong>Common Pitfalls</strong> — What typically goes wrong</li>
<li><strong>Measuring Success</strong> — KPIs to track</li>
</ol>
</td>
</tr>
<tr>
<td><strong>Security / IAM Architect</strong></td>
<td>Design the architecture, understand tradeoffs, select components</td>
<td>
<ol>
<li><strong>Architecture Overview</strong> — 5-layer pattern and how layers interact</li>
<li><strong>All 5 Layers</strong> — Deep dive on each layer's purpose and controls</li>
<li><strong>Migration Strategy</strong> — Phased adoption approach</li>
<li><strong>Real-World Example</strong> — Reference implementation details</li>
<li><strong>CoSAI Risk Mapping</strong> — Defense-in-depth coverage</li>
</ol>
</td>
</tr>
<tr>
<td><strong>Platform Engineer / SRE / DevOps</strong></td>
<td>Implement and operate the system, troubleshoot issues</td>
<td>
<ol>
<li><strong>Implementation Verification Checklist</strong> — Verify each layer's deployment</li>
<li><strong>Layer details</strong> — Technical implementation for each layer</li>
<li><strong>Real-World Example</strong> — Working code and configuration</li>
<li><strong>Common Pitfalls</strong> — Debugging and operational issues</li>
<li><strong>Measuring Success</strong> — What to monitor in production</li>
</ol>
</td>
</tr>
<tr>
<td><strong>Application Developer</strong></td>
<td>Understand how to build agents that work with this architecture</td>
<td>
<ol>
<li><strong>Layer 3: Transparent Authorization Proxy</strong> — How auth works without code changes</li>
<li><strong>Layer 5: Observable Trust</strong> — How to add tracing instrumentation</li>
<li><strong>Real-World Example</strong> — Agent code patterns</li>
<li><strong>Common Pitfalls</strong> — Avoid hardcoding auth logic</li>
</ol>
</td>
</tr>
<tr>
<td><strong>Compliance / Audit</strong></td>
<td>Verify controls, audit trails, and regulatory alignment</td>
<td>
<ol>
<li><strong>Layer 5: Observable Trust</strong> — Audit trail and delegation chain visibility</li>
<li><strong>Implementation Verification Checklist</strong> — Required controls per layer</li>
<li><strong>Measuring Success</strong> — Observable metrics and KPIs</li>
<li><strong>CoSAI Threat Taxonomy</strong> (References) — Control-to-threat mapping</li>
</ol>
</td>
</tr>
</tbody>
</table>

Before diving into the architecture layers, it's important to understand which agents need this level of security.

### Capability-Risk Classification: When to Use This Playbook

Not all agents require the full 5-layer architecture. The appropriate identity controls depend on the **capability** (what the agent can do) and **risk** (impact if compromised) profile. **Capability** ranges from simple Q&A to multi-step, state-changing planners. **Risk** depends on the sensitivity of resources accessed (public data → PII/financial systems) and blast radius of actions (read-only → write/execute/control planes).

<table align="center">
<thead>
<tr>
<th width="25%">Classification</th>
<th width="35%">Example Use Cases</th>
<th width="40%">Required Controls</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Low capability / Low risk</strong></td>
<td>FAQ lookup, public Q&A, documentation search</td>
<td>
<ul>
<li>Short-lived, narrowly scoped service accounts</li>
<li>Explicit registration</li>
<li>Basic logging and rotation</li>
</ul>
</td>
</tr>
<tr>
<td><strong>High capability / Low risk</strong></td>
<td>Internal automation on constrained, low-impact data or workflows</td>
<td>
<ul>
<li>Short-lived scoped tokens</li>
<li>Anomaly detection on access patterns</li>
</ul>
</td>
</tr>
<tr>
<td><strong>Low capability / High risk</strong></td>
<td>Read-only access to sensitive data (PII, financial records, customer databases)</td>
<td>
<ul>
<li>Environment attestation</li>
<li>Just-in-time, task-scoped credentials</li>
<li>Strict data and tenant scoping</li>
</ul>
</td>
</tr>
<tr>
<td><strong>High capability / High risk</strong></td>
<td>Financial operations, admin/devops automation, PII processing, multi-step planners with tool access</td>
<td>
<ul>
<li><strong>Full Agentic IAM</strong> (this playbook)</li>
<li>Ephemeral identities</li>
<li>OBO delegation with actor claims</li>
<li>Token exchange (RFC 8693)</li>
<li>ABAC/PBAC policies</li>
<li>Continuous evaluation</li>
<li>Human-in-the-loop for critical actions</li>
</ul>
</td>
</tr>
</tbody>
</table>


**This playbook focuses on high-capability, high-risk agents** — those that:
- Make autonomous decisions with limited human oversight
- Access sensitive or regulated data (PII, PHI, financial records)
- Perform state-changing operations (payments, approvals, infrastructure changes)
- Delegate to other agents in complex workflows
- Operate across organizational or trust boundaries

**If your agents fall into lower-risk quadrants**, consider simpler patterns:
- Low/Low: Traditional service accounts with API keys and aggressive rotation
- High/Low: Short-lived OAuth tokens with scoped permissions
- Low/High: SPIFFE identities (Layer 1) + strict network policies, skip delegation layers

**Moving up the maturity curve:** Organizations should start with Phase 1 (visibility and registration) even for low-risk agents, then adopt stricter controls as agent capabilities and risk increase. See Section 5 (Transitioning to Agentic IAM) in the CoSAI whitepaper for phased adoption guidance.

---

## Layer 1: Cryptographic Identity Foundation

**Use cryptographic identities (SPIFFE) instead of shared secrets for agent identity.**

### Why This Matters

Traditional service accounts use static passwords or API keys. These have fundamental problems:
- **Rotation is complex** — Requires coordinating updates across all agents
- **Scope is too broad** — Same credential often reused across environments
- **Compromise is invisible** — No way to detect if a key was copied

**❌ AVOID: Static API Keys**
```yaml
# Long-lived secret in environment variable
env:
  - name: AGENT_API_KEY
    value: "sk-abc123..."  # Rotated manually, shared across instances
  - name: CLIENT_SECRET
    valueFrom:
      secretKeyRef:
        name: agent-credentials
        key: secret  # Same secret for all replicas
```

Problems:
- Secret must be rotated manually across all agent instances
- Same credential reused across environments
- Visible in pod spec, logs, memory dumps

**✅ RECOMMENDED: Cryptographic Identity (SPIFFE)**
```yaml
# No secrets — certificate auto-issued and rotated by SPIRE
volumes:
  - name: spire-agent-socket
    csi:
      driver: csi.spiffe.io   # SPIRE CSI driver mounts X.509-SVID
      readOnly: true
# Agent gets unique identity: spiffe://trustdomain.com/ns/agents/sa/weather-agent
# Certificate rotates every few hours without restart
```

SPIFFE (Secure Production Identity Framework for Everyone) issues **short-lived X.509 certificates** automatically rotated by a trusted SPIRE server. Each agent gets a unique SPIFFE ID like `spiffe://trustdomain.com/ns/agents/sa/weather-agent`.

### How It Works

```
SPIRE Server (trust root)
    │
    ├─> SPIRE Agent (on each node)
    │       │
    │       └─> CSI Driver mounts certificate to pod
    │               │
    │               └─> Agent pod reads X.509-SVID from volume
    │
    └─> ClusterSPIFFEID (Kubernetes CRD)
            └─> Defines: namespace + service account → SPIFFE ID mapping
```

**Benefits:**
- **No secrets in environment variables or config files**
- **Automatic rotation** (certificates expire in hours, not years)
- **Workload attestation** — SPIRE verifies pod identity via Kubernetes API before issuing cert
- **Trust domain isolation** — Different environments use different trust domains

### Example Configuration

```yaml
# ClusterSPIFFEID maps Kubernetes service accounts to SPIFFE IDs
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterSPIFFEID
metadata:
  name: agent-identities
spec:
  spiffeIDTemplate: "spiffe://{{ .TrustDomain }}/ns/{{ .PodMeta.Namespace }}/sa/{{ .PodSpec.ServiceAccountName }}"
  podSelector:
    matchLabels:
      rossoctl.io/agent: "true"
  workloadSelectorTemplates:
    - "k8s:ns:{{ .PodMeta.Namespace }}"
    - "k8s:sa:{{ .PodSpec.ServiceAccountName }}"
```

The certificate is automatically rotated every few hours without agent restart.

### Identity-Bound Capability Claims

SPIFFE provides **identity** ("I am weather-agent"), but not **capabilities** ("I can fetch weather data for Boston"). To complete the identity picture, agents need a way to bind their cryptographic identity to a declaration of what they can do — without this:
- Agents could claim capabilities they don't have
- No way to prove an agent's purpose or scope at runtime
- Authorization decisions rely solely on network policies

**❌ AVOID: Unsigned Capability Declarations**
```json
// Self-reported agent metadata — anyone can edit this
{
  "name": "weather-agent",
  "capabilities": ["weather-data"],
  "endpoint": "http://weather-agent:8080"
}
// No signature, no binding to identity, no tamper detection
```

Problems:
- Any agent can claim any capability
- No way to detect if the declaration was modified in transit
- No binding between the identity and the claimed capabilities

**✅ RECOMMENDED: SPIFFE-Signed AgentCard**
```json
// Signed with agent's SPIFFE private key — tamper-proof
{
  "sub": "spiffe://localtest.me/ns/agents/sa/weather-agent-sa",
  "agentId": "weather-agent",
  "capabilities": ["weather-data"],
  "iat": 1716300000,
  "exp": 1716386400,
  "signature": "..." // Verifiable against SPIRE trust bundle
}
// Served at /.well-known/agent-card.json per A2A protocol
```

The [Agent2Agent (A2A) Protocol](https://agent2agent.info/docs/concepts/agentcard/) defines **AgentCard** as a standard format for describing agent capabilities. An AgentCard is a JSON file served at `/.well-known/agent-card.json` that other agents discover and consume. In a Kubernetes environment, a platform operator can use a CRD as input to generate and sign the A2A AgentCard automatically.

**The signed AgentCard proves that the capability claim is tamper-proof — it does not prove the agent is authorized to act on those capabilities.** Authorization is a separate concern addressed in subsequent layers.

**How signing works:**

```
Agent pod starts
    │
    ├─> Reads SPIFFE X.509-SVID from CSI mount
    │
    ├─> Sends certificate to agentcard-signer (sidecar)
    │       │
    │       └─> Signer verifies cert against SPIRE trust bundle
    │               │
    │               └─> Signs AgentCard with agent's private key
    │
    └─> Signed A2A AgentCard served at /.well-known/agent-card.json
            │
            └─> Peers verify signature using SPIRE trust bundle
```

**AgentCard contains:**
- Agent identity (SPIFFE ID)
- Capabilities (what it claims it can do)
- Policies (constraints on when it can do it)
- Signature (cryptographic proof of integrity)

**Example: Kubernetes CRD (operator input) → A2A AgentCard (signed output)**

The platform operator reads an AgentCard CRD and generates the signed A2A AgentCard:

```yaml
# AgentCard CRD — operator input, NOT the A2A AgentCard itself
apiVersion: agents.rossoctl.dev/v1alpha1
kind: AgentCard
metadata:
  name: weather-agent-card
  namespace: agents
spec:
  agentId: weather-agent
  serviceAccount: weather-agent-sa
  capabilities:
    - type: weather-data
      scope: read
      locations: [global]
  policies:
    - type: network-egress
      allow: ["api.weather.gov"]
```

**Verification Modes:**

- **Audit Mode** (recommended for rollout) — Log verification failures but allow requests. Monitor for unexpected cards or signature failures. Tune policies before enforcement.
- **Enforce Mode** (production) — Reject requests with invalid signatures. Block agents without valid cards.

### CoSAI Risk Mapping

**Mitigates:**
- **MCP-T7** (Credential Compromise) — No long-lived secrets to leak
- **MCP-T2** (Agent Impersonation) — Cryptographic proof of identity
- **MCP-T1** (Unauthorized Actions) — Capabilities explicitly listed and verified
- **MCP-T3** (Privilege Escalation) — Signed credentials prevent tampering

**Controls:**
- `enforceWorkloadIdentity` — Require cryptographic identity for all agents
- `verifyAgentCredentials` — Validate AgentCard signatures before authorizing actions


---

## Layer 2: Federated Identity Bridge

**Bridge SPIFFE identity to OAuth 2.0 using federated authentication instead of client secrets.**

> **Pattern (tool-agnostic):** Agents must authenticate to enterprise authorization systems (OAuth/OIDC) using their cryptographic workload identity — not static client secrets. The authorization server validates the workload credential against a trusted root, eliminating shared secrets entirely.
>
> *This playbook uses Keycloak with federated-jwt. Alternatives: Okta with workload identity federation, Auth0, Azure AD workload identity, Google Cloud Workload Identity Federation.*

### Why This Matters

Most enterprise systems use OAuth 2.0 for authorization (Keycloak, Okta, Auth0). To integrate agents, you need to bridge SPIFFE identity → OAuth tokens. Two approaches:

**❌ AVOID: Client Secret Approach**
```python
# Agent has a client_secret in environment variable
token = oauth_server.token_exchange(
    client_id="weather-agent",
    client_secret=os.getenv("CLIENT_SECRET"),  # Long-lived secret!
    grant_type="client_credentials"
)
```

Problems:
- Secret must be rotated manually
- Same secret across all agent instances
- Secret visible in pod spec, logs, memory dumps

**✅ RECOMMENDED: Federated JWT Approach**
```python
# Agent uses SPIFFE JWT-SVID (no secrets!)
jwt_svid = spiffe_workload_api.fetch_jwt_svid(audience="keycloak")
token = oauth_server.token_exchange(
    client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    client_assertion=jwt_svid,  # Short-lived, auto-rotated
    grant_type="client_credentials"
)
```

### How It Works

```
Agent needs OAuth token
    │
    ├─> Fetches JWT-SVID from SPIRE (audience=keycloak)
    │       └─> JWT signed by SPIRE, expires in minutes
    │
    ├─> Sends JWT to Keycloak as client_assertion
    │       │
    │       └─> Keycloak validates JWT signature using SPIRE trust bundle
    │               │
    │               └─> Subject (SPIFFE ID) becomes OAuth client_id
    │
    └─> Keycloak issues OAuth access token
```

**Key insight:** The SPIFFE ID (`spiffe://trust.domain/ns/agents/sa/weather-agent-sa`) becomes the OAuth `client_id`. No pre-registration needed if dynamic client registration is enabled.

### Keycloak Configuration

1. **Load SPIRE trust bundle** into Keycloak as a client scope validator
2. **Enable federated JWT auth** in realm settings:
   ```
   KC_FEATURES=client-auth-federated:v1,spiffe:v1
   ```
3. **Register agents as OAuth clients** with authentication type `federated-jwt`:
   ```bash
   kcadm.sh create clients -r agents \
     -s clientId="spiffe://localtest.me/ns/agents/sa/weather-agent-sa" \
     -s clientAuthenticatorType=federated-jwt \
     -s serviceAccountsEnabled=true
   ```

### Benefits

- **No secrets** — JWT-SVID is the credential
- **Automatic rotation** — SPIRE rotates JWTs every few minutes
- **Cryptographic trust** — Keycloak validates signature against trust bundle
- **Preserves identity** — SPIFFE ID flows into OAuth token claims

### CoSAI Risk Mapping

**Mitigates:**
- **MCP-T7** (Credential Compromise) — No long-lived secrets
- **MCP-T2** (Agent Impersonation) — Cryptographic proof required

**Control:** `useFederatedIdentity` — Require SPIFFE-based auth, not client secrets

---

## Layer 3: Transparent Authorization Proxy

**Inject authorization enforcement as a sidecar proxy, not in application code.**

> **Pattern (tool-agnostic):** Authorization enforcement must be external to agent application code. A proxy intercepts all inbound and outbound agent traffic, validating credentials on ingress and performing token exchange on egress. Agent code remains identity-agnostic — it never sees or handles auth logic.
>
> *This playbook uses Rossoctl AuthBridge sidecar. Alternatives: Envoy with ext_authz filter, Istio authorization policies, API gateway-based enforcement (Kong, Ambassador), or service mesh sidecar injection.*

### Why This Matters

Embedding authorization in agent code is fragile:
- **Bypassed easily** — Developer forgets to add auth check to new endpoint
- **Inconsistent** — Each agent implements auth differently
- **Not auditable** — Authorization logic scattered across codebases

**❌ AVOID: Authorization in Agent Code**
```python
class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Every agent must remember to add this — and get it right
        token = self.headers.get("Authorization")
        if not validate_jwt(token):        # Easy to forget on new endpoints
            self.send_response(401)
            return
        claims = decode_jwt(token)
        if not check_scopes(claims):       # Each agent implements differently
            self.send_response(403)
            return
        # Business logic starts here
        result = process_request(self.rfile.read(...))
```

Problems:
- New endpoint added without auth check = security hole
- JWT validation logic duplicated (and diverging) across agents
- Auth bugs require patching every agent individually

**✅ RECOMMENDED: Sidecar Proxy (AuthBridge)**
```python
class AgentHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # No auth code — sidecar already validated before traffic reaches here
        data = self.rfile.read(int(self.headers['Content-Length']))
        result = process_request(data)
        self.send_response(200)
        self.wfile.write(result)
```

The **sidecar pattern** enforces authorization **transparently** by intercepting all traffic before it reaches the agent. Auth logic lives in infrastructure, not application code.

### Architecture: Port Stealing

```
┌────────────────────────────────────────────────────────┐
│  Pod: weather-agent                                    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │ AuthBridge Sidecar (port 8080)               │    │
│  │                                              │    │
│  │  Inbound Proxy (8080) ──┐                   │    │
│  │                          ▼                    │    │
│  │               ┌─────────────────┐            │    │
│  │               │ JWT Validation  │            │    │
│  │               └─────────────────┘            │    │
│  │                          │                    │    │
│  └──────────────────────────┼────────────────────┘    │
│                             ▼                         │
│  ┌──────────────────────────────────────────────┐    │
│  │ Agent (port 8081, PORT env var)              │    │
│  │   - Application code (identity-agnostic)     │    │
│  │   - Reads PORT from env, listens on 8081    │    │
│  └──────────────────────────────────────────────┘    │
│                             │                         │
│  ┌──────────────────────────┼────────────────────┐    │
│  │ AuthBridge Sidecar (outbound)                │    │
│  │                          ▼                    │    │
│  │  Forward Proxy (8082) ──┐                    │    │
│  │                          ▼                    │    │
│  │               ┌────────────────────────────┐ │    │
│  │               │ Token Exchange             │ │    │
│  │               │ (RFC 8693 w/ actor claims) │ │    │
│  │               └────────────────────────────┘ │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
          External request to peer agent
```

**Port stealing:**
- Service routes traffic to port **8080** (standard)
- AuthBridge sidecar listens on **8080** (inbound validation)
- Agent listens on **8081** (reads from `PORT` env var)
- Agent makes outbound calls via **8082** (token exchange proxy)

### Sidecar Injection via Webhook

```yaml
# AgentRuntime CR triggers mutating webhook
apiVersion: agents.rossoctl.dev/v1alpha1
kind: AgentRuntime
metadata:
  name: weather-agent-runtime
  namespace: agents
spec:
  deploymentName: weather-agent
  authBridge:
    enabled: true
    authType: federated-jwt  # Use SPIFFE for Keycloak auth
    inbound:
      port: 8080
      validation: jwt-validation
    outbound:
      port: 8082
      tokenExchange: true
```

Webhook injects `authbridge-proxy` sidecar into the deployment, modifying:
- Adds sidecar container
- Sets `PORT=8081` env var for agent
- Mounts SPIRE agent socket
- Mounts token exchange routes ConfigMap

### CoSAI Risk Mapping

**Mitigates:**
- **MCP-T1** (Unauthorized Actions) — All requests validated before reaching agent
- **MCP-T3** (Privilege Escalation) — Sidecar cannot be bypassed

**Control:** `enforceSidecarAuth` — Require authorization sidecar for all agent pods

---

## Layer 4: Delegation Chain Preservation

**Preserve the full delegation chain (User → Agent A → Agent B) using RFC 8693 token exchange with actor claims.**

> **Pattern (tool-agnostic):** When an agent delegates to another agent, the resulting token must carry both the original subject (who requested the action) and the actor chain (which agents are executing it). Delegation depth must be tracked and enforceable via policy. The standard mechanism is RFC 8693 token exchange with nested `act` claims.
>
> *This playbook uses a custom Keycloak SPI. Alternatives: any OAuth server supporting RFC 8693 with actor claims — ForgeRock, Ping Identity, or custom token exchange middleware.*

### Why This Matters

In agentic systems, requests often flow through multiple agents:
```
Alice (user)
  → Orchestrator Agent (routes request)
    → Weather Agent (fetches data)
```

Without delegation chain preservation:
- Weather Agent can't distinguish between Alice's request vs. Orchestrator acting autonomously
- Audit logs show "Orchestrator accessed weather data" but not *why* or *for whom*
- Authorization policies can't enforce "only allow when acting on behalf of a real user"

### RFC 8693 Token Exchange

RFC 8693 defines a standard way to exchange one token for another while preserving delegation context.

**❌ AVOID: Standard Token Exchange (loses actor)**
```http
POST /token HTTP/1.1
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&subject_token=<alice-jwt>
&subject_token_type=urn:ietf:params:oauth:token-type:access_token
&audience=spiffe://localtest.me/ns/agents/sa/weather-agent-sa
```

Response token has `sub=alice-uuid` but **loses the actor** (orchestrator). You can't tell who forwarded the request or why.

**✅ RECOMMENDED: Token Exchange with Actor Claims**
```json
{
  "sub": "alice-uuid",           // Original user
  "act": {                         // Actor chain
    "sub": "spiffe://localtest.me/ns/agents/sa/orchestrator-agent-sa"
  },
  "aud": "spiffe://localtest.me/ns/agents/sa/weather-agent-sa",
  "delegation_depth": 1
}
```

Now the weather agent can see:
- **Subject (sub):** Alice is the original user
- **Actor (act.sub):** Orchestrator is acting on Alice's behalf
- **Depth:** This is 1 hop in the delegation chain

### Custom Keycloak SPI

Stock Keycloak doesn't add `act` claims. We extend it with a custom Service Provider Interface (SPI). Note: this is Java because Keycloak is a Java application — the agent-side code in other sections remains Python.

```java
// Custom Keycloak SPI: AgenticTokenExchangeProvider.java
public class AgenticTokenExchangeProvider implements TokenExchangeProvider {
    @Override
    public Response exchange(TokenExchangeContext context) {
        AccessToken originalToken = context.getSubjectToken();
        AccessToken delegatedToken = new AccessToken();
        
        // Preserve original subject
        delegatedToken.setSubject(originalToken.getSubject());
        
        // Add actor claim (current client = agent)
        delegatedToken.setOtherClaims("act", Map.of(
            "sub", context.getClient().getClientId()  // SPIFFE ID
        ));
        
        // Track delegation depth
        int depth = (int) originalToken.getOtherClaims().getOrDefault("delegation_depth", 0);
        delegatedToken.setOtherClaims("delegation_depth", depth + 1);
        
        return Response.ok(delegatedToken).build();
    }
}
```

### Multi-Hop Delegation

For deeper chains (User → A → B → C), the `act` claim becomes nested:

```json
{
  "sub": "alice-uuid",
  "act": {
    "sub": "spiffe://.../agent-c",
    "act": {
      "sub": "spiffe://.../agent-b",
      "act": {
        "sub": "spiffe://.../agent-a"
      }
    }
  },
  "delegation_depth": 3
}
```

### Authorization Policies

With delegation chains preserved, you can enforce policies like:

```python
def authorize_weather_request(jwt):
    # Only allow weather access when acting on behalf of a user
    if "act" not in jwt:
        return False  # Direct agent access denied
    
    # Check that subject is a real user (not another agent)
    if jwt["sub"].startswith("spiffe://"):
        return False  # Agent-to-agent without user context
    
    # Limit delegation depth
    if jwt.get("delegation_depth", 0) > 2:
        return False  # Too many hops
    
    return True
```

### CoSAI Risk Mapping

**Mitigates:**
- **MCP-T1** (Unauthorized Actions) — Policies enforce delegation rules
- **MCP-T3** (Privilege Escalation) — Delegation depth limits prevent long chains

**Control:** `preserveDelegationChain` — Require actor claims in delegated tokens

---

## Layer 5: Observable Trust

**Make delegation chains and authorization decisions visible in traces and logs.**

> **Pattern (tool-agnostic):** Every request must produce a distributed trace that spans all agents in the delegation chain, with authorization context (subject, actor, delegation depth, scopes) recorded as structured attributes. An auditor must be able to reconstruct "who requested what, through which agents, with what permissions" from a single query.
>
> *This playbook uses OpenTelemetry with Phoenix. Alternatives: Jaeger, Zipkin, Datadog APM, Grafana Tempo, or any OpenTelemetry-compatible backend.*

### Why This Matters

Without observability:
- "Why was this request denied?" is hard to answer
- Delegation chains are invisible after the fact
- Incident response requires correlating logs across multiple agents

**Observable trust** means:
1. Every request has a trace showing the full delegation chain
2. Authorization decisions are logged with context
3. Traces include JWT claims (subject, actor, depth)

### OpenTelemetry Integration

Observable trust requires two things from each agent:

1. **Trace propagation** — connecting spans across agents into a single trace. This is handled automatically by the OpenTelemetry SDK via W3C `traceparent` headers. It shows *which* agents were involved in a request.

2. **Auth context enrichment** — extracting identity claims from the already-validated token into span attributes. Trace propagation alone doesn't carry auth context. Without enrichment, the trace shows "orchestrator called weather-agent" but not "on behalf of Alice, at delegation depth 1."

By standardizing the auth context attributes that agents emit (`auth.subject`, `auth.actor`, `auth.delegation_depth`), observable trust extends beyond a single cluster. If every agent in a trust domain — whether running in your infrastructure or hosted by a third-party provider — emits the same attributes, a single trace captures the full delegation chain across organizational boundaries: which services were hit in your environment, which agents and tools were invoked by the provider, and who authorized each hop.

The following code runs inside the **agent application** (not the platform or proxy) to perform auth context enrichment. The authorization proxy (Layer 3) has already validated the token — this code only reads the claims for observability:

```python
import json, base64

def parse_jwt_claims(jwt_token):
    """Decode JWT payload. Signature verification is handled by the authorization
    proxy (Layer 3) — by the time this code runs, the token is already validated."""
    if not jwt_token or not jwt_token.startswith("Bearer "):
        return {}
    token = jwt_token.split(" ")[1]
    payload = token.split(".")[1]
    # Add padding if needed
    payload += "=" * (4 - len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))

def set_auth_attributes(span, auth_header):
    """Set authentication attributes on span"""
    if not auth_header:
        return
    
    claims = parse_jwt_claims(auth_header)
    if not claims:
        return
    
    # Subject (original user or agent)
    if "sub" in claims:
        span.set_attribute("auth.subject", claims["sub"])
    
    # Username (if present)
    if "preferred_username" in claims:
        span.set_attribute("auth.username", claims["preferred_username"])
    
    # Actor (delegating agent)
    if "act" in claims and "sub" in claims["act"]:
        span.set_attribute("auth.actor", claims["act"]["sub"])
    
    # Delegation depth
    if "delegation_depth" in claims:
        span.set_attribute("auth.delegation_depth", claims["delegation_depth"])
```

### Trace Example

Alice -> Orchestrator -> Weather Agent produces a trace like:

```
Trace ID: abc123
|- Span: orchestrator.route_request
|   auth.subject: alice-uuid
|   auth.username: alice
|   http.method: POST
|   |- Span: orchestrator.llm_call (Ollama)
|   +- Span: orchestrator.forward_to_peer
|       http.url: http://weather-agent:8080
|       +- Span: weather-agent.handle_request
|           auth.subject: alice-uuid
|           auth.actor: spiffe://localtest.me/ns/agents/sa/orchestrator-agent-sa
|           auth.delegation_depth: 1
|           weather.location: Boston
```

**Key observations:**
- Single `trace_id` spans all agents
- Alice's identity (`auth.subject`) flows through the chain
- Orchestrator appears as `auth.actor` in weather-agent span
- Delegation depth increments at each hop

### Toward a Standardized Observability Contract

The auth context attributes in this playbook (`auth.subject`, `auth.actor`, `auth.delegation_depth`) demonstrate the pattern that needs to be standardized across the industry for cross-boundary observable trust.

Two collaborative efforts that would be helpful in working toward this:

- **OCSF Schema** — defining a standard schema for identity, delegation, and trust attributes across agentic security telemetry/logging
- **OpenTelemetry GenAI semantic conventions** — incorporating standardized attributes for AI/agent workloads into OTel's semantic conventions

Traces alone are necessary but not sufficient for full audit. Spans are sampled, retention-limited, and not integrity-protected. A stronger guarantee requires **signed evidence**, integrity-protected audit records that allow a verifier to check claimed capabilities against observed behavior without trusting the agent or the platform. This is an area where we can work with industry standardization like OCSF to define integrity-protected audit schemas that the industry can adopt uniformly.


The goal: when any provider, your infrastructure, a hosted AI service, a third-party agent, emits the same standardized attributes, a single trace captures the full delegation chain across organizational boundaries. Which services were hit in your environment, which agents and tools were invoked by the provider, who authorized each hop, all queryable from one trace.

The identity layers in this playbook (cryptographic identity, delegation chain preservation) provide the foundation. A standardized observability contract is the last piece that makes cross-boundary trust auditable.

### CoSAI Risk Mapping

**Mitigates:**
- **MCP-T9** (Insufficient Logging) — Full delegation chain captured
- **MCP-T1** (Unauthorized Actions) — Audit trail for forensics

**Control:** `logDelegationChains` — Capture auth attributes in all traces


---

## Implementation Verification Checklist

Use this checklist to verify each layer as you implement it. Each item maps to a layer described above.

### Layer 1: Cryptographic Identity Foundation *(SPIFFE/SPIRE in this playbook)*
- [ ] Cryptographic identity provider deployed (issues short-lived certificates or tokens bound to workload identity)
- [ ] Identity attestation mechanism configured (verifies workload identity before issuing credentials)
- [ ] Credential delivery infrastructure deployed (securely mounts certificates/tokens to agent workloads)
- [ ] Identity-to-workload mapping defined (namespace, service account, or other selector → unique identity)
- [ ] Trust bundle published (root CA certificates available for all components that verify agent identities)
- [ ] Automatic certificate/token rotation verified (credentials refresh without manual intervention or downtime)
- [ ] Credential schema defined (binding identity to capabilities, policies, and code version)
- [ ] Signing infrastructure deployed (cryptographically binds SPIFFE identity to credential)
- [ ] Verifiable credentials created for each agent with explicit capability grants
- [ ] Signature verification enabled (start in audit mode to log failures without blocking)
- [ ] Monitor verification logs for unexpected credential claims or signature failures
- [ ] Tune capability policies based on audit data, then switch to enforce mode (reject invalid signatures)
- [ ] **Production-ready:** All agent credentials are verified and signed, signing infrastructure reconciles automatically

### Layer 2: Federated Identity Bridge *(Keycloak with federated-jwt in this playbook)*
- [ ] Identity provider trust bundle loaded into OAuth/OIDC server (enables validation of workload identity tokens)
- [ ] OAuth server configured to accept federated identity authentication (e.g., JWT bearer assertion, workload identity federation)
- [ ] Agents registered as OAuth clients using cryptographic identity instead of static secrets (e.g., JWT assertion, certificate-based auth)
- [ ] Test: Agent can exchange workload identity credential for OAuth access token
- [ ] Verify: No static secrets (client secrets, API keys, passwords) stored in agent configuration or environment
- [ ] **Production-ready:** Agents authenticate to OAuth/OIDC provider using cryptographic identity, no static secrets in use

### Layer 3: Transparent Authorization Proxy *(AuthBridge sidecar with Rossoctl in this playbook)*
- [ ] Scope defined for which agents require authorization enforcement (e.g., high-risk agents, cross-tenant communication)
- [ ] Authorization proxy infrastructure deployed and configured (sidecar, service mesh, or API gateway pattern)
- [ ] Proxy intercepts all agent traffic (both inbound requests and outbound calls) before reaching application logic
- [ ] Agent application code is identity-agnostic (reads network configuration from environment, no hardcoded auth logic)
- [ ] External traffic routing configured to pass through authorization layer (cannot bypass to reach agent directly)
- [ ] Proxy performs authentication validation (JWT/token verification) on inbound requests
- [ ] Proxy handles credential refresh/exchange for outbound calls (implements token exchange or credential injection)
- [ ] Test: Requests without valid credentials are rejected before reaching agent application
- [ ] Test: Agent cannot be accessed by bypassing the authorization proxy
- [ ] **Production-ready:** All target agents have authorization proxy deployed, direct access to agent application port fails

### Layer 4: Delegation Chain Preservation *(Keycloak with custom RFC 8693 SPI in this playbook)*
- [ ] OAuth server configured to support RFC 8693 token exchange with actor claim preservation
- [ ] Token exchange endpoint supports actor chain (nested `act` claims) in delegated tokens
- [ ] Delegation routing configured (maps target agents to their required token audience/scope)
- [ ] Target audience specified using agent's cryptographic identity (not agent name or service endpoint)
- [ ] Agents propagate incoming authorization context on outbound calls (forward Authorization header or equivalent)
- [ ] Test: Delegated tokens contain `act` claim with delegating agent's identity and original `sub` (subject)
- [ ] Verify: `delegation_depth` increments at each hop in multi-agent chains
- [ ] Verify: Authorization policies can enforce delegation depth limits and subject/actor restrictions
- [ ] **Production-ready:** Multi-hop delegation chains preserve full actor history, delegation depth limits enforced

### Layer 5: Observable Trust *(OpenTelemetry with Phoenix in this playbook)*
- [ ] Distributed tracing infrastructure deployed (trace collector and storage backend)
- [ ] Trace backend supports querying by custom attributes (enables filtering by identity, delegation, scope)
- [ ] Agents instrumented with distributed tracing (propagate trace context across agent-to-agent calls)
- [ ] Authorization context extracted from tokens and recorded as trace attributes (subject, actor, delegation depth, scopes)
- [ ] Trace attributes include both original requester identity (subject) and delegating agent identity (actor)
- [ ] Test: Single trace ID spans all agents in a delegation chain (end-to-end visibility)
- [ ] Test: Trace UI shows delegation chain (who acted on whose behalf at each hop)
- [ ] Audit queries can reconstruct: which user requested action, which agents were involved, what scopes were used
- [ ] **Production-ready:** Every request generates a complete trace with auth attributes, audit queries reconstruct full delegation chains

---

## Putting It All Together: End-to-End Request Flow

The 5 layers work together on every request. This section traces a single request — Alice asks the orchestrator for Boston's weather — through all layers to show how they compose.

```
Alice (user) ──POST /ask "What's the weather in Boston?"──▶ Orchestrator Agent ──▶ Weather Agent
```

### Step-by-step flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. IDENTITY + CREDENTIALS (Layer 1)                                         │
│    Both agents already have SPIFFE identities issued by SPIRE:              │
│      Orchestrator: spiffe://trust.domain/ns/agents/sa/orchestrator-sa       │
│      Weather:      spiffe://trust.domain/ns/agents/sa/weather-agent-sa      │
│    X.509-SVIDs auto-rotated every few hours. No secrets in env vars.        │
│    Each agent has a signed AgentCard binding its SPIFFE ID to capabilities:  │
│      Orchestrator → can route requests, call peer agents                    │
│      Weather      → can fetch weather data, scope: read, egress: weather API│
│    Signatures verified against SPIRE trust bundle.                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. FEDERATED BRIDGE (Layer 2)                                               │
│    Alice's request arrives with an OAuth token (from Keycloak).              │
│    Orchestrator authenticates to Keycloak using its SPIFFE JWT-SVID          │
│    (no client secret) to obtain an OAuth access token.                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. AUTHORIZATION PROXY (Layer 3)                                            │
│    a) INBOUND to Orchestrator:                                              │
│       AuthBridge sidecar on port 8080 validates Alice's JWT.                │
│       ✓ Valid → forwards to orchestrator app on port 8081.                  │
│    b) OUTBOUND from Orchestrator to Weather Agent:                          │
│       Orchestrator calls localhost:8082 (outbound proxy).                   │
│       AuthBridge performs token exchange (→ Layer 4) and forwards.          │
│    c) INBOUND to Weather Agent:                                             │
│       AuthBridge sidecar validates the delegated token.                     │
│       ✓ Valid → forwards to weather app on port 8081.                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. DELEGATION CHAIN (Layer 4)                                               │
│    The outbound proxy exchanges Alice's token via RFC 8693:                  │
│      subject_token = Alice's JWT                                            │
│      audience      = spiffe://trust.domain/ns/agents/sa/weather-agent-sa    │
│    Keycloak returns a delegated token:                                       │
│      { "sub": "alice-uuid",                                                 │
│        "act": { "sub": "spiffe://.../orchestrator-sa" },                    │
│        "delegation_depth": 1 }                                              │
│    Weather Agent sees: Alice requested it, Orchestrator is acting for her.  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. OBSERVABLE TRUST (Layer 5)                                               │
│    A single trace (ID: abc123) spans both agents:                           │
│      orchestrator.route_request                                             │
│        auth.subject: alice-uuid                                             │
│        auth.username: alice                                                 │
│      └─ weather-agent.handle_request                                        │
│           auth.subject: alice-uuid                                          │
│           auth.actor: spiffe://.../orchestrator-sa                          │
│           auth.delegation_depth: 1                                          │
│    Audit query: "Show all weather requests Alice made today" → instant.     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What each layer prevented

| If this layer were missing... | What could go wrong |
|---|---|
| **Layer 1** (Identity + Credentials) | Orchestrator uses a static API key. Key leaks in logs → any attacker can impersonate it. A rogue agent claims weather capabilities it doesn't have. No way to verify at runtime. |
| **Layer 2** (Federated Bridge) | Client secret stored in orchestrator's env var. Rotated manually, shared across replicas. |
| **Layer 3** (Auth Proxy) | Developer adds a new endpoint to weather agent but forgets the auth check → open to unauthenticated access. |
| **Layer 4** (Delegation) | Weather agent sees "orchestrator requested weather data" but can't tell if Alice or Bob asked, or if orchestrator acted on its own. |
| **Layer 5** (Observability) | Incident responders grep through scattered logs across agents to reconstruct what happened. Takes hours instead of one query. |

---

## Migration Strategy: Phased Adoption

Now that you understand the 5-layer architecture, here's how to adopt it safely in an existing environment. Implementing all 5 layers at once is risky. This section provides a phased approach to adopt Agentic IAM incrementally while maintaining production stability.

### Phase 1: Foundation

**Goal:** Establish cryptographic identity and visibility without disrupting existing agents.

<table>
<thead>
<tr>
<th width="30%">Actions</th>
<th width="30%">Deliverables</th>
<th width="20%">Coexistence</th>
<th width="20%">Rollback</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<ul>
<li>Deploy cryptographic identity provider (Layer 1)</li>
<li>Configure identity-to-workload mapping</li>
<li>Deploy credential delivery infrastructure</li>
</ul>
</td>
<td>
<ul>
<li>All agents have cryptographic identities</li>
<li>Trust bundle published and accessible</li>
<li>Certificate rotation working</li>
</ul>
</td>
<td>Agents continue using existing authentication (e.g., API keys) while cryptographic identities are issued in parallel. No breaking changes yet.</td>
<td>Simply stop issuing new credentials. Existing agents unaffected.</td>
</tr>
</tbody>
</table>

### Phase 2: Verifiable Credentials

**Goal:** Add capability-based authorization without enforcing it.

<table>
<thead>
<tr>
<th width="30%">Actions</th>
<th width="30%">Deliverables</th>
<th width="20%">Coexistence</th>
<th width="20%">Rollback</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<ul>
<li>Define credential schema (Layer 1)</li>
<li>Deploy signing infrastructure</li>
<li>Create verifiable credentials for each agent</li>
<li>Enable signature verification in <strong>audit mode</strong></li>
</ul>
</td>
<td>
<ul>
<li>All agents have signed credentials</li>
<li>Verification logs capture success/failure</li>
<li>Capability policies documented</li>
</ul>
</td>
<td>Credentials are verified and logged but not enforced. Agents with invalid credentials still proceed (with warning logs).</td>
<td>Disable signature verification. Credentials become decorative metadata.</td>
</tr>
</tbody>
</table>

### Phase 3: Federated Bridge + Transparent Proxy

**Goal:** Replace static secrets with federated auth and enforce authorization at the proxy layer.

<table>
<thead>
<tr>
<th width="30%">Actions</th>
<th width="30%">Deliverables</th>
<th width="20%">Coexistence</th>
<th width="20%">Rollback</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<ul>
<li>Load trust bundle into OAuth server (Layer 2)</li>
<li>Register agents as OAuth clients with federated auth</li>
<li>Deploy authorization proxy infrastructure (Layer 3)</li>
<li>Enable proxy for pilot agents (10-20% of fleet)</li>
</ul>
</td>
<td>
<ul>
<li>Pilot agents authenticate via cryptographic identity</li>
<li>Proxy intercepts all pilot agent traffic</li>
<li>No client secrets in pilot agent config</li>
</ul>
</td>
<td>Pilot agents use new path (proxy + federated auth). Remaining agents use legacy path (direct access + static secrets). Gradual rollout by agent cohort.</td>
<td>Route pilot agents back to legacy path. Remove proxy from their network path.</td>
</tr>
</tbody>
</table>

### Phase 4: Delegation + Observability

**Goal:** Enable delegation chain preservation and end-to-end observability.

<table>
<thead>
<tr>
<th width="30%">Actions</th>
<th width="30%">Deliverables</th>
<th width="20%">Coexistence</th>
<th width="20%">Rollback</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<ul>
<li>Configure RFC 8693 token exchange (Layer 4)</li>
<li>Implement actor claim preservation</li>
<li>Deploy distributed tracing (Layer 5)</li>
<li>Instrument agents with trace context</li>
<li>Extract auth attributes into spans</li>
</ul>
</td>
<td>
<ul>
<li>Delegated tokens contain <code>act</code> claims</li>
<li>Full delegation chains visible in traces</li>
<li>Audit queries reconstruct "who did what for whom"</li>
</ul>
</td>
<td>Agents on new path get full delegation. Legacy agents appear as "unknown" in delegation chains but don't break.</td>
<td>Disable token exchange. Agents use direct OAuth tokens without actor claims. Tracing continues but without auth attributes.</td>
</tr>
</tbody>
</table>

### Phase 5: Enforce + Expand

**Goal:** Switch Layer 1 credential verification to enforce mode and migrate remaining agents.

<table>
<thead>
<tr>
<th width="30%">Actions</th>
<th width="30%">Deliverables</th>
<th width="20%">Coexistence</th>
<th width="20%">Rollback</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<ul>
<li>Switch credential verification to <strong>enforce mode</strong></li>
<li>Migrate remaining agents to new path (cohorts of 10-20%)</li>
<li>Decommission legacy authentication paths</li>
<li>Rotate/revoke all static secrets</li>
</ul>
</td>
<td>
<ul>
<li>100% of agents on Agentic IAM path</li>
<li>Legacy authentication disabled</li>
<li>Zero static secrets in agent configuration</li>
</ul>
</td>
<td>None. Full cutover to Agentic IAM.</td>
<td>Requires re-enabling legacy paths and redistributing static secrets. Avoid by thorough testing in Phase 3-4.</td>
</tr>
</tbody>
</table>

### General Migration Principles

- **Start with non-critical agents:** Pilot on dev/staging environments and low-risk agents first
- **Monitor extensively:** Track success rates, latency, error rates at each phase
- **Automate rollback:** Have one-command rollback scripts ready before each phase
- **Phased enforcement:** Audit mode → partial enforcement (pilot) → full enforcement
- **Maintain escape hatches:** Keep legacy paths active until 95%+ adoption in new path
- **Communicate widely:** Notify agent developers, SREs, and security teams at each phase transition

---

## Measuring Success

This section provides observable metrics and KPIs for each layer. Use these to verify correct implementation and track production health.

<table>
<thead>
<tr>
<th width="15%">Layer</th>
<th width="30%">Key Metrics</th>
<th width="20%">Target Values</th>
<th width="35%">How to Verify</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Layer 1:<br/>Cryptographic Identity + Credentials</strong></td>
<td>
• Certificate/token rotation success rate<br/>
• Identity issuance latency<br/>
• Trust bundle propagation time<br/>
• Agent registration failures<br/>
• Credential verification success rate<br/>
• Signature validation failures<br/>
• Signing infrastructure readiness
</td>
<td>
• 100% rotation success<br/>
• 0 registration failures<br/>
• 100% valid credentials<br/>
• 0 signature failures<br/>
• All agents verified and bound
</td>
<td>
Query identity provider logs for rotation events<br/>
Monitor identity provider metrics for issuance latency<br/>
Track trust bundle distribution lag across components<br/>
Alert on failed workload attestation<br/>
Query credential store for verification status across agents<br/>
Monitor signing infrastructure logs for errors<br/>
Alert on credentials in failed or unverified state
</td>
</tr>
<tr>
<td><strong>Layer 2:<br/>Federated Bridge</strong></td>
<td>
• OAuth client registration success<br/>
• Federated authentication failures<br/>
• Trust bundle sync lag<br/>
• Token validation latency
</td>
<td>
• All agents registered<br/>
• 0 federated auth failures
</td>
<td>
Query OAuth/OIDC provider for registered agent client list<br/>
Monitor OAuth server logs for authentication failures<br/>
Compare identity provider bundle version with OAuth server bundle<br/>
Measure token validation latency at the OAuth server
</td>
</tr>
<tr>
<td><strong>Layer 3:<br/>Authorization Proxy</strong></td>
<td>
• Proxy deployment coverage<br/>
• Request validation failures (401/403 rate)<br/>
• Proxy latency overhead<br/>
• Bypass attempts detected
</td>
<td>
• 100% of target agents behind proxy<br/>
• &lt;1% auth failures (legitimate denials only)<br/>
• 0 successful bypasses
</td>
<td>
Verify all target agent workloads have proxy deployed<br/>
Monitor proxy logs for 401/403 responses<br/>
Compare request latency with and without proxy<br/>
Test direct access to agent application port (should fail)
</td>
</tr>
<tr>
<td><strong>Layer 4:<br/>Delegation Chain</strong></td>
<td>
• Token exchange success rate<br/>
• Actor claim presence in delegated tokens<br/>
• Delegation depth distribution<br/>
• Chain reconstruction failures
</td>
<td>
• &gt;99% exchange success<br/>
• 100% delegated tokens have <code>act</code> claim<br/>
• 0 reconstruction failures
</td>
<td>
Monitor proxy logs for token exchange success/failure<br/>
Decode downstream tokens and verify <code>act.sub</code> matches upstream client<br/>
Query traces for delegation depth distribution<br/>
Test multi-hop flows and verify full chain visibility
</td>
</tr>
<tr>
<td><strong>Layer 5:<br/>Observable Trust</strong></td>
<td>
• Trace completion rate (all spans present)<br/>
• Auth attribute presence in traces<br/>
• Trace correlation across agents<br/>
• Audit query coverage
</td>
<td>
• 100% traces complete<br/>
• 100% spans have auth attributes<br/>
• Single trace ID per request chain<br/>
• Can answer "who did what for whom"
</td>
<td>
Query tracing backend for orphaned or incomplete spans<br/>
Check for spans missing auth attributes (subject, actor)<br/>
Verify parent-child span relationships across agent boundaries<br/>
Test audit queries: who requested, which agents involved, what scopes used
</td>
</tr>
</tbody>
</table>

## Common Pitfalls

<table>
<thead>
<tr>
<th width="25%">Pitfall</th>
<th width="25%">Problem</th>
<th width="25%">Why It Fails</th>
<th width="25%">Solution</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>1. Using static secrets "just for now"</strong></td>
<td>Team uses client secrets or API keys during development, planning to switch to federated cryptographic auth later.</td>
<td>Code patterns solidify around secrets, making migration harder. Secrets leak into docs, scripts, and developer habits.</td>
<td>Start with cryptographic identity federation from day one, even in dev. Most identity providers run locally and are easier than managing secret rotation.</td>
</tr>
<tr>
<td><strong>2. Skipping delegation chain preservation</strong></td>
<td>Using basic token exchange without actor claims to "simplify implementation."</td>
<td>You lose the ability to answer "who requested this and why?" in production. Incident response becomes guesswork.</td>
<td>Implement actor claims from the start. The token exchange extension is typically small (~100 lines) and pays dividends in audit capability.</td>
</tr>
<tr>
<td><strong>3. Authorization in agent code instead of proxy</strong></td>
<td>Each agent implements its own token validation logic.</td>
<td>Inconsistent enforcement, easy to bypass, hard to update. One forgotten check = security hole.</td>
<td>Use the proxy pattern (sidecar, service mesh, or API gateway). Authorization becomes infrastructure, not application code.</td>
</tr>
<tr>
<td><strong>4. Not testing credential rotation</strong></td>
<td>Identity provider setup works on day 1, but credentials expire after 24 hours and renewals fail silently.</td>
<td>Connectivity issues between identity provider and agents, credential delivery misconfiguration, or clock skew.</td>
<td>Monitor identity provider logs, test with short TTLs (1 hour) in dev, set up alerts for rotation failures.</td>
</tr>
<tr>
<td><strong>5. Ignoring delegation depth limits</strong></td>
<td>No maximum depth on delegation chains.</td>
<td>Agent A → B → C → D → ... becomes hard to reason about and may hide privilege escalation.</td>
<td>Enforce <code>delegation_depth &lt;= 3</code> in authorization policies. Alert on chains that hit the limit.</td>
</tr>
</tbody>
</table>

---

## Real-World Example

Code examples demonstrating the patterns in this playbook are available in [`examples/identity-architecture/`](examples/identity-architecture/). 

The examples include:
- **`k8s/`** — Kubernetes manifests: agent deployments (`orchestrator-deployment.yaml`, `weather-agent-deployment.yaml`), AgentRuntime CR (`agentruntime.yaml`), AgentCard CRD
  (`orchestrator-agentcard.yaml`), AuthBridge outbound routes (`authproxy-routes.yaml`), OTel collector and tracing (`otel-tracing.yaml`), demo UI (`demo-ui.yaml`), and Ollama LLM backend
  (`ollama-deployment.yaml`)
- **`keycloak-spi/`** — Custom Keycloak SPI that adds RFC 8693 `act` claims to exchanged tokens (`AgenticTokenExchangeProvider.java`), enabling delegation chain preservation
- **`orchestrator/`** — Python A2A agent that routes user requests via Ollama, forwards to peer agents through AuthBridge, and extracts JWT claims into OpenTelemetry spans (`server.py`)
- **`scripts/`** — Automated cluster lifecycle: local image registry (`registry.sh`), full kind cluster setup with SPIRE, Keycloak, and operator (`setup.sh`), and teardown (`teardown.sh`)
- **`Helm values`** — Configuration for Keycloak (`keycloak-values.yaml`), Phoenix tracing UI (`phoenix-values.yaml`), and the operator (`operator-values.yaml`)

Instruction for running the setup is [`examples/identity-architecture/README.md`](examples/identity-architecture/README.md)

---

## Glossary

Tool-specific terms used throughout this playbook. Each term is introduced in context within its corresponding layer section.

<table>
<thead>
<tr>
<th width="20%">Term</th>
<th width="80%">Definition</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>SPIFFE/SPIRE</strong></td>
<td><strong><a href="https://spiffe.io/">SPIFFE</a></strong> (Secure Production Identity Framework for Everyone) — Standard for cryptographic workload identity. Defines SPIFFE IDs (URIs like <code>spiffe://trust.domain/path</code>) and SVIDs (verifiable identity documents).<br><br><strong><a href="https://spiffe.io/docs/latest/spire-about/">SPIRE</a></strong> — Reference implementation that issues and rotates X.509 and JWT SVIDs automatically. Used in <strong>Layer 1</strong>.</td>
</tr>
<tr>
<td><strong>X.509-SVID / JWT-SVID</strong></td>
<td>SPIFFE Verifiable Identity Documents. X.509-SVIDs are short-lived certificates for mTLS. JWT-SVIDs are signed JSON Web Tokens for API authentication. Used in <strong>Layers 1, 2</strong>.</td>
</tr>
<tr>
<td><strong>AgentCard</strong></td>
<td>A verifiable credential describing an agent's capabilities. The <a href="https://agent2agent.info/docs/concepts/agentcard/">A2A Protocol specification</a> defines AgentCard as a JSON "business card" for agent discovery. This playbook uses the <strong>Rossoctl implementation</strong>: a Kubernetes CRD that cryptographically binds an agent's SPIFFE identity to its capabilities, policies, and code hash using digital signatures — creating a tamper-proof "passport" for agents. Used in <strong>Layer 1</strong>.</td>
</tr>
<tr>
<td><strong>AuthBridge</strong></td>
<td>A sidecar proxy pattern that enforces authentication and authorization transparently for agent workloads. Part of the <a href="https://github.com/rossoctl/operator">Rossoctl operator</a>, AuthBridge is injected via mutating webhook and intercepts traffic on three ports: <strong>inbound (8080)</strong> for JWT validation, <strong>agent (8081)</strong> for application logic, and <strong>outbound (8082)</strong> for token exchange. This "port stealing" pattern ensures all agent communication passes through authorization enforcement without modifying agent code. Used in <strong>Layer 3</strong>.</td>
</tr>
</tbody>
</table>

---

## References

### CoSAI Whitepapers
- **Agentic Identity and Access Management:** Coalition for Secure AI, March 2026. https://www.coalitionforsecureai.org/wp-content/uploads/2026/04/agentic-identity-and-access-control.pdf  
  *Primary reference for this playbook. Defines the 9 core principles, capability-risk classification, OBO delegation patterns, and phased adoption framework.*

- **Model Context Protocol (MCP) Security:** CoSAI, 2026. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/blob/main/model-context-protocol-security.pdf  
  *Defines MCP-T1 through MCP-T12 threat taxonomy and security controls for MCP servers, tools, and agent-to-tool interactions.*

- **CoSAI Principles for Secure-by-Design Agentic Systems:** Coalition for Secure AI. https://github.com/cosai-oasis/ws4-secure-design-agentic-systems  
  *Foundation document establishing zero-trust, least-privilege, and defense-in-depth principles for agentic systems.*

### Standards and Specifications
- **SPIFFE Specification:** https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE.md
- **RFC 8693 (OAuth 2.0 Token Exchange):** https://datatracker.ietf.org/doc/html/rfc8693
- **RFC 9396 (Rich Authorization Requests):** https://datatracker.ietf.org/doc/html/rfc9396
- **RFC 7009 (OAuth 2.0 Token Revocation):** https://datatracker.ietf.org/doc/html/rfc7009
- **W3C Trace Context:** https://www.w3.org/TR/trace-context/
- **NIST AI 100 (Risk Management Framework):** https://www.nist.gov/itl/ai-risk-management-framework
- **NIST SP 800-63 (Digital Identity Guidelines):** https://pages.nist.gov/800-63-3/

### CoSAI Threat Taxonomy

This playbook addresses the following threat categories from the MCP Security whitepaper:

<table>
<thead>
<tr>
<th width="15%">Threat</th>
<th width="35%">Description</th>
<th width="50%">How This Playbook Mitigates</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>MCP-T1</strong></td>
<td>Unauthorized agent actions — agents perform operations beyond authorized scope</td>
<td><strong>Layers 1, 3, 4:</strong> AgentCards define explicit capabilities; AuthBridge enforces at every hop; delegation chains preserve scope limits</td>
</tr>
<tr>
<td><strong>MCP-T2</strong></td>
<td>Agent impersonation — malicious actors spawn unauthorized agents or masquerade as legitimate ones</td>
<td><strong>Layers 1, 2:</strong> SPIFFE cryptographic identity prevents spoofing; federated JWT auth requires valid SPIRE certificate</td>
</tr>
<tr>
<td><strong>MCP-T3</strong></td>
<td>Privilege escalation — agents exploit weak boundaries to gain elevated access</td>
<td><strong>Layers 1, 3, 4:</strong> Signed capabilities prevent tampering; sidecar enforcement prevents bypass; delegation depth limits prevent chain abuse</td>
</tr>
<tr>
<td><strong>MCP-T7</strong></td>
<td>Credential compromise — long-lived secrets leaked through agent memory, logs, or prompts</td>
<td><strong>Layers 1, 2:</strong> Short-lived X.509/JWT-SVIDs auto-rotated; no static secrets in environment variables</td>
</tr>
<tr>
<td><strong>MCP-T9</strong></td>
<td>Insufficient logging/audit — inability to reconstruct "which agent did what on whose behalf"</td>
<td><strong>Layer 5:</strong> Observable trust with delegation chains in traces; immutable audit logs with correlation IDs</td>
</tr>
</tbody>
</table>

**Additional threat themes addressed:**
- **Over-permissioning:** ZSP (Layer 1) and just-in-time credentials
- **Loss of actor clarity:** OBO tokens preserve full delegation chain (Layer 4)
- **Shadow/unknown agents:** Explicit registration and AgentCard requirement (Layer 1)
- **Broken delegation chains:** RFC 8693 with act claims (Layer 4)
- **Agent collusion & proxy chaining:** Delegation depth limits and ABAC policies (Layer 4)

### Tools
- **SPIRE:** https://spiffe.io/docs/latest/spire-about/
- **Keycloak:** https://www.keycloak.org/
- **OpenTelemetry:** https://opentelemetry.io/
- **Envoy Proxy:** https://www.envoyproxy.io/ (alternative to custom AuthBridge sidecar)

### Implementation Examples
- **Rossoctl SPIRE Signing Demo:** https://github.com/rossoctl/operator/blob/main/demos/agentcard-spire-signing/demo.md  
  *Complete reference implementation demonstrating SPIRE-signed AgentCards, AuthBridge sidecar injection with federated-jwt authentication, RFC 8693 token exchange delegation, and end-to-end observability on Kubernetes. Includes automated setup scripts and verification steps.*


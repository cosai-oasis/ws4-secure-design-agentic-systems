# Rossoctl SPIRE Signing Demo

Secure agent-to-agent communication on a local kind cluster with podman. Two agents communicate via A2A JSON-RPC with SPIRE identities, signed AgentCards, AuthBridge token exchange, and OpenTelemetry tracing. A browser UI lets Alice authenticate via Keycloak and chat with agents.


## Repository Layout

```
agents-identity/
├── keycloak-spi/                      # Custom Keycloak SPI (RFC 8693 actor claims)
│   ├── Dockerfile, pom.xml
│   └── src/.../AgenticTokenExchangeProvider.java
├── keycloak-values.yaml               # Helm override for custom Keycloak image
├── phoenix-values.yaml                # OTel Collector + Phoenix + PostgreSQL
├── orchestrator/
│   ├── Dockerfile
│   └── server.py                      # A2A JSON-RPC handler with Ollama routing
├── k8s/
│   ├── weather-agent-server.yaml      # ConfigMap: Python A2A handler
│   ├── weather-agent-deployment.yaml  # Full deployment (SA, RBAC, signer, service)
│   ├── ollama-deployment.yaml         # Ollama LLM infra (qwen2.5:0.5b)
│   ├── orchestrator-deployment.yaml   # Orchestrator (SA, RBAC, peers ConfigMap, signer)
│   ├── orchestrator-agentcard.yaml    # AgentCard CR
│   ├── agentruntime.yaml              # AgentRuntime CRs (triggers AuthBridge injection)
│   ├── authproxy-routes.yaml          # Outbound token-exchange routes
│   ├── otel-tracing.yaml              # Shared tracing module (stdlib, no pip deps)
│   └── demo-ui.yaml                   # Demo UI (server + HTML/JS + NetworkPolicy + HTTPRoute)
├── scripts/
│   ├── setup.sh                       # Full automated setup (registry-aware, rebuilds operator)
│   ├── teardown.sh                    # Deletes cluster, preserves registry
│   └── registry.sh                    # Local OCI registry lifecycle
├── practical-guides/                  # Identity architecture and OAuth delegation guides
```

External dependencies (not in this repo):

| Directory | Purpose |
|-----------|---------|
| `~/rossoctl/` | Main rossoctl installer (Helm charts, scripts) |
| `~/rossoctl-operator/` | Operator repo (signer, webhook, controllers) |

### Why We Build the Operator from HEAD

The released operator (`v0.3.0-alpha.1`) is 388 commits behind HEAD and missing fixes required for this demo. `setup.sh` rebuilds from the local `~/rossoctl-operator` repo automatically.

Key fixes since the release:

| Commit | Fix |
|--------|-----|
| `a6658af` | Write `client-id.txt` in federated-jwt mode — without this, jwt-validation has no expected audience |
| `60e1cc7` | Write empty `client-secret.txt` in federated-jwt mode — prevents authbridge crash on missing file |
| `0024e99` | SPIFFE JWT-SVID authentication for client registration — the `federated-jwt` auth type we use |
| `a0a2cd9` | Kagenti to Rossoctl rename — CRDs, labels, namespaces, chart names |
| `cc97a79` | rossocortex to cortex rename — authbridge references |
| `9348895` | Correct operator controller image name in chart |
| `5f4a8e3` | spiffe-helper image fix — spire-agent-socket mount in authbridge-proxy |
| `04e426b` | Sunset legacy client-registration sidecar in favor of webhook injection |

## How to Run

### Prerequisites

- podman
- kind (`KIND_EXPERIMENTAL_PROVIDER=podman`)
- kubectl
- helm

### First Time Setup

```bash
# Start local OCI registry and cache all images (including operator rebuild)
scripts/registry.sh start && scripts/registry.sh push

# Full cluster setup
scripts/setup.sh
```

### Iterating

```bash
# Tear down cluster (keeps registry cache)
scripts/teardown.sh

# Recreate from cache
scripts/setup.sh

# Force rebuild of all images
scripts/setup.sh --force-build
```

## Verification

### Check AgentCards

```bash
kubectl get agentcard -n agents
```

Both agents should show `VERIFIED`, `BOUND`, and `SYNCED` status.

### End-to-End via Demo UI

Open http://demo-ui.localtest.me:8080, log in as `alice / alice`, and send a message like "What is the weather in Tokyo?". The full flow:

1. Alice logs in via OIDC (Authorization Code + PKCE)
2. Alice's JWT is sent to the orchestrator's inbound AuthBridge
3. AuthBridge validates the JWT
4. Orchestrator asks Ollama which peer to route to
5. Orchestrator forwards the request with the Authorization header
6. Outbound AuthBridge exchanges Alice's JWT for a delegated token (SPIFFE audience)
7. Weather-agent's inbound AuthBridge validates the delegated token
8. Weather-agent returns mock weather data

### Direct Agent Test (bypasses AuthBridge)

```bash
kubectl exec -n agents deploy/orchestrator-agent -c agent -- python3 -c "
import urllib.request, json
req = urllib.request.Request('http://localhost:8081/',
    data=json.dumps({'jsonrpc':'2.0','id':'1','method':'message/send',
        'params':{'message':{'role':'user','messageId':'m1',
            'parts':[{'type':'text','text':'What is the weather in Tokyo?'}]}}}).encode(),
    headers={'Content-Type':'application/json'})
print(json.dumps(json.load(urllib.request.urlopen(req, timeout=120)), indent=2))
"
```

### Check AuthBridge Logs

```bash
# Orchestrator: look for "inbound authorized" and "outbound token exchanged"
kubectl logs -n agents deploy/orchestrator-agent -c authbridge-proxy --tail=20

# Weather-agent: look for "inbound authorized" with orchestrator's SPIFFE ID as clientID
kubectl logs -n agents deploy/weather-agent -c authbridge-proxy --tail=20
```

## Cluster URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Demo UI | http://demo-ui.localtest.me:8080 | alice / alice |
| Phoenix (traces) | http://phoenix.localtest.me:8080 | — |
| Keycloak (admin) | http://keycloak.localtest.me:8080 | admin / admin |
| Tornjak (SPIRE UI) | http://spire-tornjak-ui.localtest.me:8080 | — |

## Deployment Explanation

### Architecture

```
Browser (Alice)
  │  OIDC login (Authorization Code + PKCE, server-side)
  ▼
Demo UI (pod, no sidecar)
  │  Authorization: Bearer <alice-jwt>
  ▼
Orchestrator AuthBridge inbound (port 8080, jwt-validation)
  │  validates Alice's JWT
  ▼
Orchestrator Agent (port 8081)
  │  asks Ollama which peer to route to
  │  forwards A2A JSON-RPC to peer (with Authorization header)
  ▼
Orchestrator AuthBridge outbound (port 8082, token-exchange)
  │  exchanges Alice's JWT for delegated token (SPIFFE audience)
  │  delegated token has orchestrator as client, Alice as subject
  ▼
Weather Agent AuthBridge inbound (port 8080, jwt-validation)
  │  validates delegated token
  ▼
Weather Agent (port 8081) → returns mock weather data
```

### Identity and Trust

Each agent runs with a SPIRE-issued X.509-SVID identity under trust domain `localtest.me`. The operator's agentcard-signer init container signs each agent's AgentCard using the SPIRE identity, making the card tamper-evident and cryptographically bound to the agent's workload.

### AuthBridge Sidecar Injection

Deploying an `AgentRuntime` CR triggers the operator's mutating webhook to inject an `authbridge-proxy` sidecar into the agent pod:

- **Port 8080 (reverse proxy)**: intercepts inbound traffic, validates JWTs
- **Port 8081 (agent)**: the actual agent process (relocated from 8080 via `PORT` env var)
- **Port 8082 (forward proxy)**: intercepts outbound traffic, performs token exchange
- **Port 8083 (transparent proxy)**: iptables-redirected outbound traffic

### Token Exchange (RFC 8693)

When the orchestrator forwards a request to the weather-agent, the outbound AuthBridge intercepts it and exchanges Alice's JWT for a delegated token at Keycloak. The delegated token carries:

- **`client_id`**: the orchestrator's SPIFFE ID (`spiffe://localtest.me/ns/agents/sa/orchestrator-agent-sa`)
- **`sub` (subject)**: Alice's user ID (preserved from the original token)
- **`aud` (audience)**: the weather-agent's SPIFFE ID

This preserves the delegation chain — the weather-agent knows both who the end user is (Alice) and which agent forwarded the request (orchestrator).

### Keycloak Configuration

A custom Keycloak SPI (`keycloak-spi/`) adds RFC 8693 `act` claims to exchanged tokens, which stock Keycloak doesn't include. Agents authenticate to Keycloak using `federated-jwt` (SPIFFE identity), not client secrets. The operator registers each agent as a Keycloak OAuth2 client using its SPIFFE ID as the client ID.

### Observability

All agents emit OpenTelemetry spans via the stdlib-based tracing module (`k8s/otel-tracing.yaml`). W3C `traceparent` headers propagate trace context across agent boundaries. Traces are collected by the OTel Collector and visualized in Phoenix.

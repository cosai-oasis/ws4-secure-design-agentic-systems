# Runtime Conformance Testing for MCP Servers

**Practical Guide — Verifying T1–T12 Controls at Runtime**

---

## Overview

Static analysis and design review can verify that security controls are *written* correctly.
Runtime conformance testing verifies that they *work* when the server is actually running —
including under adversarial inputs, expired tokens, oversized payloads, and multi-turn
session manipulation.

This guide describes how to apply runtime conformance testing to MCP servers, using the
open-source [cosai-mcp](https://github.com/ragsvasan/cosai-mcp) scanner as a reference
implementation. cosai-mcp is a black-box JSON-RPC prober and stateful conformance harness
that tests a live MCP server against all 12 threat categories defined in the
[CoSAI MCP Security Taxonomy](../whitepapers/model-context-protocol-security.md).

The guide tracks **CoSAI MCP Security v2.0** (August 2026) and **MCP 2026-07-28**: the
scanner speaks both the stateless 2026-07-28 protocol and the earlier `initialize`-based
versions, and can check a deployment against a v2.0 Security Assurance Profile level
(see [Verifying an assurance level](#verifying-a-v20-security-assurance-profile-level)).

---

## Why Runtime Testing Is Necessary

The CoSAI T1–T12 taxonomy defines *what* must be enforced. Runtime conformance testing
answers the question: *is it actually enforced on the running server?*

Common gaps between design intent and runtime behavior:

- Auth middleware that passes in unit tests but fails on certain token formats (T1)
- Tool dispatch that checks permissions in the happy path but skips checks on error paths (T2)
- Input validation that covers known-bad patterns but misses schema-conformant adversarial values (T3)
- Tool manifests that are frozen at init but quietly updated mid-session by a middleware bug (T6)
- Session IDs that appear in error log URLs, leaking via Referer headers (T7)

None of these are detectable by static analysis. They require a running server and
adversarial probes.

---

## Three Testing Engines

Runtime conformance testing for MCP requires three distinct mechanisms, each covering a
different class of threats:

| Engine | Covers | Mechanism |
|--------|--------|-----------|
| **Black-box prober** | T1, T3, T8, T10 (partial T2/T6/T11) | One-shot JSON-RPC probes over Streamable HTTP |
| **Stateful conformance harness** | T2, T6, T7 | Full handshake (2026-07-28 `server/discover`, or legacy `initialize`) → multi-turn scripted scenarios |
| **Middleware instrumentation** | T4, T9, T12 | In-process middleware; detection requires being in the call path |

> **Important:** Black-box probes alone cannot fully test T4 (prompt injection boundary),
> T9 (LLM output trust), or T12 (audit log integrity). These require either instrumented
> middleware or cooperative server-side tooling.

---

## Quick Start

### Prerequisites

```bash
pip install cosai-mcp        # Python 3.11+
```

Or run without installing:
```bash
uvx cosai-mcp scan http://your-mcp-server:8000
```

### Run a full conformance scan

```bash
# Unauthenticated server
cosai scan http://localhost:8000 --fail-on high

# Server requiring Bearer token
cosai scan http://localhost:8000 \
  --auth-token "$MCP_TOKEN" \
  --fail-on high \
  --report-html conformance-report.html \
  --report-sarif conformance-report.sarif
```

### Integrate into CI/CD

```yaml
# .github/workflows/mcp-conformance.yml
- uses: cosai-mcp/scan-action@v1
  with:
    target: ${{ env.MCP_SERVER_URL }}
    auth_token: ${{ secrets.MCP_TOKEN }}
    fail_on: high
```

Exit codes are fail-closed:
- `0` — no findings at or above threshold
- `1` — findings detected
- `2` — scanner internal error (treated as failure by CI)
- `3` — target unreachable

### Protocol eras (MCP 2026-07-28)

MCP 2026-07-28 removed the `initialize` handshake and `Mcp-Session-Id`: clients call
`server/discover`, and every request carries its identity and protocol version in
`_meta` plus the `MCP-Protocol-Version`, `Mcp-Method` and `Mcp-Name` headers. The
scanner is a dual-era client:

- By default (`--protocol-era auto`) it tries `server/discover` first and falls back to
  the legacy `initialize` handshake only for servers that do not recognise it. The era is
  detected once per scan and used for every probe.
- A server that is recognisably 2026-07-28 but rejects the client's version is reported
  `SCAN-INCOMPLETE`. It is **never downgraded** to the legacy handshake, because a
  downgrade path is itself a v2.0 finding.
- `--protocol-era modern` or `legacy` pins one era.

---

## T1–T12 Coverage Map

The table below maps each CoSAI threat category to the probes cosai-mcp runs and the
engine that covers it. The "What the probe does" column describes the adversarial action
taken against a live server.

### T1 — Improper Authentication

| Probe | What the probe does | Pass condition |
|-------|---------------------|----------------|
| T01-001-p1 | Sends `initialize` with no `Authorization` header | Server returns 401 or session error |
| T01-002-p1/p2 | Sends a JWT signed with the wrong key | Server rejects with 401 |
| T01-003-p1/p2 | Replays a previously used JTI value | Server rejects (replay cache enforced) |
| T01-004-p1/p2 | Sends a DPoP proof with mismatched `htu`/`htm` | Server rejects DPoP binding failure |
| T01-007-p1 | Unauthenticated `tools/call` whose `_meta` claims an identity and capabilities (2026-07-28) | Server ignores `_meta` claims for authorization and rejects |
| T01-008-p1 | Lists tools with a valid token issued for a **different** resource (RFC 8707 audience) | Server rejects the foreign-audience token |

T01-008 needs `--foreign-audience-token`: a short-lived (under one hour) token for a
sacrificial test resource. The token is disclosed to the server under test, so never use
one for a production resource. The scan also checks RFC 9728 Protected Resource Metadata
passively, using same-origin requests only.

### T2 — Missing Access Control (Stateful)

Tested via multi-turn scenarios in the stateful harness:

- **T2-SC-001:** Calls a privileged tool as a low-privilege session; asserts rejection
- **T2-SC-002:** Calls a tool with a valid token but missing required scope; asserts rejection

> If your server uses placeholder tool names (`admin_delete`, `read_file`), use
> `--profile` or `--method-override` to map them to your actual tool names.

### T3 — Input Validation Failures

| Probe | Adversarial payload |
|-------|---------------------|
| T03-001-p1/p2/p3 | Oversized payloads (10KB–1MB strings in tool arguments) |
| T03-002-p1/p2 | Command injection patterns in tool arguments (`; cat /etc/passwd`, `$(id)`, `../../../etc`) |

With adaptive probing enabled (default), payloads are synthesized to conform to the
server's actual `inputSchema` — injecting adversarial values into real parameter positions
rather than fictional ones.

### T5 — Inadequate Data Protection

| Probe | What the probe tests |
|-------|---------------------|
| T05-003-p1 | Tool results marked `cacheScope: public` (2026-07-28), which shared intermediaries may serve to other users; user- or tenant-specific results must be private |

### T6 — Integrity/Verification (Stateful)

- **T6-SC-001:** Calls `tools/list` twice in the same session; asserts the manifest is identical.
  Detects tool shadowing or mid-session manifest mutation.

### T7 — Session Security Failures (Stateful)

- **T7-SC-001:** Tests session identity preservation across tool calls in the same session.

MCP 2026-07-28 probes (black-box):

| Probe | What the probe tests |
|-------|---------------------|
| T07-004-p1/p2 | `Mcp-Method` / `Mcp-Name` headers that disagree with the JSON-RPC body; a gateway routing on headers would apply the wrong policy. Server must reject the mismatch |
| T07-005-p1 | An unknown protocol version in `_meta` and `MCP-Protocol-Version`; server must answer `-32022` (UnsupportedProtocolVersion) listing what it supports |
| T07-006-p1 | A legacy `initialize` handshake against a 2026-07-28 server; a retained legacy path must enforce the same per-request authorization |
| T07-007-p1/p2 | Task enumeration and guessable task IDs (Tasks extension); handles must be CSPRNG-generated, opaque, and authorized per caller |

### T8 — Network Binding Failures

| Probe | What the probe tests |
|-------|---------------------|
| T08-001-p1/p2 | Sends a URL parameter pointing to a loopback / RFC1918 address; asserts SSRF blocked |
| T08-002-p1 | Checks whether the server accepts requests that bypass the expected bind address |
| T08-003-p1 | Shadow server detection — tests whether the server can be reached on unexpected ports |

### T10 — Resource Management

| Probe | What the probe tests |
|-------|---------------------|
| T10-001-p1 | Rapid successive calls; asserts rate limiting is enforced |
| T10-002-p1 | Long-running tool call; asserts wall-clock timeout is enforced |
| T10-003-p1 | Recursive tool call pattern; asserts loop depth limit is enforced |

### T11 — Supply Chain / Lifecycle

| Probe | What the probe tests |
|-------|---------------------|
| T11-001-p1/p2 | Calls a tool name not in the server's manifest; asserts JSON-RPC `-32601` (Method Not Found) |

| T11-002-p1 | Whether `server/discover` still advertises deprecated protocol-level Logging as a telemetry channel (2026-07-28) |

> A server that returns `{"result": {"isError": false}}` for an unknown tool name is
> non-compliant with the MCP JSON-RPC spec and may be vulnerable to tool name confusion.

### T4, T5, T9, T12 — Middleware-Only Categories

These categories cannot be fully tested by black-box probing:

| Category | Why black-box is insufficient | Recommended approach |
|----------|------------------------------|----------------------|
| T4 — Data/Control Boundary | Prompt injection detection requires being in the LLM call path | Use `mcp-armor` `BoundaryEngine` or equivalent middleware |
| T5 — Data Protection | PII leakage may be context-dependent | Instrument response pipeline; scan for PII patterns in all tool responses |
| T9 — Trust Boundary | LLM output trust requires observing the re-feed path | Middleware that intercepts LLM output before it reaches tool dispatch |
| T12 — Audit Logging | Log integrity requires access to the log store | Use append-only hash-chained logging; verify chain with `cosai audit verify` |

---

## Reading the Results

### Status definitions

| Status | Meaning |
|--------|---------|
| `PASS` | Server correctly enforced the control |
| `FINDING` | Control missing or bypassable — investigate |
| `INCONCLUSIVE` | Probe could not reach the security logic (e.g. schema mismatch); not a finding |
| `SCAN-INCOMPLETE` | Transport or session error — treat as failure in CI |

### SARIF output

cosai-mcp produces SARIF 2.1.0 output compatible with GitHub's native security tab:

```bash
cosai scan http://localhost:8000 --report-sarif results.sarif
gh api repos/{owner}/{repo}/code-scanning/sarifs \
  -f commit_sha=$(git rev-parse HEAD) \
  -f ref=refs/heads/main \
  -F sarif=@results.sarif
```

---

## Verifying a v2.0 Security Assurance Profile level

CoSAI MCP Security v2.0 §3.3 defines four assurance levels (L1 Sandbox, L2 Internal,
L3 Production, L4 Regulated), and §3.3.5 calls for automated tooling that verifies a
claimed level. The scanner checks one deployment against a level:

```bash
cosai scan https://mcp.example.com/mcp --auth-token "$MCP_TOKEN" \
  --assurance-level 3 --evidence ./evidence
```

A black-box scan can *disprove* many controls but *prove* only a few. Each control gets
one verdict:

- **`pass`**: a probe proved the control.
- **`fail`**: a probe disproved it.
- **`attested`**: the operator supplied hashed evidence via `--evidence`.
- **`unverified`**: nothing above applies.
- **`not_required`**: the control does not apply at the claimed level.

A level is `met` only when every MUST control passes, and `met_with_attestation` when the
remainder are attested. The level claim, scan scope and evidence hashes go into the
signed scorecard.

The [evidence-per-level annex](https://github.com/ragsvasan/cosai-mcp/blob/main/docs/EVIDENCE_PER_LEVEL.md)
answers v2.0 open question #4. For each control and level, it lists the requirement, what
the scanner can establish on its own, and what an operator should attest.

---

## Server-Side Defense Library

[mcp-armor](https://github.com/ragsvasan/mcp-armor) is the companion server-side
protection library. It runs *inside* the MCP server and enforces all 12 CoSAI categories
via a composable middleware chain. When correctly configured, every cosai-mcp probe
against an mcp-armor-protected server should produce `PASS`.

```python
# FastAPI + mcp-armor example
from mcp_armor import CoSAIGuard
from mcp_armor.adapters.fastapi import ArmorMiddleware

guard = CoSAIGuard.from_config("cosai.yaml")
app.add_middleware(ArmorMiddleware, guard=guard)
```

For MCP 2026-07-28 and CoSAI v2.0, mcp-armor adds the following, opt-in and currently
unreleased:

- **Envelope checks:** request-envelope validation (header ↔ body and `_meta` ↔
  authenticated principal) and stateless (session-less) requests behind its ASGI
  middleware or sidecar.
- **Sealed state and handles:** sealed `requestState` and server-held task handles.
- **Telemetry:** W3C trace-context rules and OCSF API Activity audit events with keyed
  parameter digests.

---

## Contributing

The cosai-mcp threat catalog is open source and accepts contributions:

- **New probe definitions** — JSON files following the [catalog schema](https://github.com/ragsvasan/cosai-mcp/blob/main/catalog/)
- **Server profiles** — pre-configured scan settings for known MCP server frameworks
- **Bug reports and findings** — [github.com/ragsvasan/cosai-mcp/issues](https://github.com/ragsvasan/cosai-mcp/issues)

Please review the [CoSAI Contributing policy](../CONTRIBUTING.md) for contributions
to this guide.

---

## References

- [CoSAI MCP Security v2.0 (T1–T12)](../whitepapers/model-context-protocol-security.md)
- [cosai-mcp scanner](https://github.com/ragsvasan/cosai-mcp) — Apache 2.0
- [mcp-armor server SDK](https://github.com/ragsvasan/mcp-armor) — Apache 2.0
- [OWASP MCP Top 10](https://owasp.org/www-project-mcp-top-10/)
- [MCP Specification](https://modelcontextprotocol.io/specification/): 2026-07-28 (stateless), with 2025-03-26 through 2025-11-25 still supported by the scanner
- [cosai-mcp evidence-per-level annex](https://github.com/ragsvasan/cosai-mcp/blob/main/docs/EVIDENCE_PER_LEVEL.md): CoSAI v2.0 §3.3 controls

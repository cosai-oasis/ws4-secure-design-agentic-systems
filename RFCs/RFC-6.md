# Model Context Protocol (MCP) Security Best Practices Gap Analysis

As discussed in the TSC and other forums. We could enhance the industry guidance on how to secure MCP implementations.  I am opening this issue so that we could further brainstorm on this.

## Omar's Thoughts on Potential CoSAI Work

Everyone is using the Model Context Protocol (MCP) to create two-way connections between large language models (LLMs) and external data sources or tools, enabling integration in AI agentic applications. MCP was introduced by Anthropic in late 2024, since then there are several best practices in the [MCP specification(https://modelcontextprotocol.io/specification/draft/basic/security_best_practices). It focuses on three key attack vectors: the Confused Deputy Problem, Token Passthrough, and Session Hijacking. These address risks in MCP implementations, particularly in proxy servers and distributed environments.

However, in CoSAI we could create additional guidance that provide:
- A detailed "how-to" guide for implementing each best practice, expanding on the spec's mitigations with step-by-step instructions.
- A gap analysis based on deep research into MCP documentation, OAuth 2.0/2.1 security guidelines, OWASP API Security guidance, and best practices for API gateways, session management in distributed systems, and model-specific APIs. Research reveals that while the spec covers core OAuth and session-related issues, it overlooks broader vulnerabilities like prompt injection, excessive data exposure, rate limiting, and encryption requirements.

## Detailed How-To Guide for MCP Security Best Practices

We could outline the practical implementation steps for each best practice from the MCP spec. These can be derived from the provided mitigations, augmented with operational details for developers and operators. Assume an HTTP-based MCP implementation using OAuth 2.x, as recommended in the spec.

### 1. Confused Deputy Problem
The Confused Deputy Problem arises in MCP proxy servers using static client IDs with third-party authorization servers, where attackers exploit consent cookies to bypass user approval and redirect codes to malicious URIs.

**Mitigation from Spec:** MCP proxy servers using static client IDs **MUST** obtain user consent for each dynamically registered client before forwarding to third-party authorization servers.

**How-To Implement:**
1. **Identify Proxy Scenarios:** During MCP server setup, audit configurations where the server acts as a proxy to third-party APIs (e.g., via tools like `/tools/invoke`). Check if the third-party authorization server supports dynamic client registration (DCR). If not, flag the use of static client IDs.
   
2. **Implement Per-Client Consent Flow:**
   - On receiving a dynamic client registration request (e.g., via MCP's `/clients/register` endpoint), generate a unique client ID and store it in a secure database (e.g., using encrypted storage with AES-256).
   - Before redirecting to the third-party authorization server, insert an intermediary consent screen in the MCP proxy. Use a web form (e.g., HTML/JS) to display: "Do you consent to [Dynamic Client Name] accessing [Third-Party API] via this MCP proxy?"
   - Require explicit user approval (e.g., via a button click) and log the consent with a timestamp, user ID, and client ID for auditing.

3. **Validate Redirect URIs:** Enforce exact matching of redirect URIs during registration (per OAuth RFC 6749). Use whitelisting: Store approved URIs in the client registration and reject any mismatches to prevent redirection to attacker.com.

4. **Handle Third-Party Forwarding Securely:**
   - After MCP consent, forward the authorization request to the third-party server, appending the static client ID.
   - On callback, validate the authorization code against the registered client and user session before exchanging for tokens.
   - If the third-party server requires additional consent, proxy it transparently but log any skips due to cookies.

5. **Testing and Monitoring:** Use tools like OAuth 2.0 Playground or automated tests (e.g., with Postman) to simulate attacks. Monitor logs for unusual consent skips using SIEM tools (e.g., ELK Stack). Rotate static client secrets periodically.

We are making sure that user consent is granular, preventing cookie-based bypasses.

### 2. Token Passthrough
Token passthrough occurs when an MCP server forwards client-provided tokens to downstream APIs without validation, risking circumvention of controls like rate limiting.

**Mitigation from Spec:** MCP servers **MUST NOT** accept any tokens that were not explicitly issued for the MCP server.

**How-To Implement:**
1. **Token Issuance Policy:** Configure the MCP server to act as its own authorization server (AS) or integrate with one (e.g., using OpenID Connect on top of OAuth). Issue tokens with specific claims: audience (`aud`) set to the MCP server's endpoint (e.g., "https://mcp-proxy.example.com"), issuer (`iss`) matching the MCP AS, and scopes limited to MCP operations.

2. **Validation on Receipt:**
   - For every inbound request (e.g., `/sessions/create` or `/tools/invoke`), parse the Authorization header (Bearer token).
   - Validate signature using the AS's public key (e.g., via JWKS endpoint).
   - Check claims: Ensure `aud` matches the MCP server, `iss` is trusted, expiration (`exp`) is valid, and `nbf` (not before) is respected. Use libraries like `python-jose` or `jsonwebtoken` in Node.js.
   - Reject tokens with mismatched audiences or issuers immediately with a 401 Unauthorized response.

3. **Proxy Token Exchange:**
   - When proxying to downstream APIs, exchange the validated MCP token for a new one issued to the downstream service (e.g., using OAuth client credentials grant).
   - Never forward the original token; generate a fresh one with delegated scopes.

4. **Prevent Bypass Risks:**
   - Enforce rate limiting at the MCP layer (e.g., using Redis for token-based quotas) to avoid downstream overload.
   - Log all token validations without storing token values (use hashes for auditing).
   - For opaque tokens, introspect them via the AS's introspection endpoint (RFC 7662).

5. **Evolution-Proofing:** Design with future controls in mind—e.g., add custom claims for roles. Test by attempting passthrough with invalid tokens and verify rejection.

This maintains trust boundaries and ensures accountability.

### 3. Session Hijacking
Session hijacking exploits guessable or shared session IDs in distributed MCP servers, enabling impersonation or prompt injection via queued events.

**Mitigation from Spec:** MCP servers **MUST** verify all inbound requests, **MUST NOT** use sessions for authentication, **MUST** use secure non-deterministic session IDs, **SHOULD** bind IDs to user-specific information, and can optionally use additional unique identifiers.

**How-To Implement:**
1. **Avoid Session-Based Auth:** Use token-based authentication exclusively (e.g., JWTs) for all requests. Deprecate cookie-based sessions; configure the server (e.g., in Express.js or Flask) to reject session cookies for auth.

2. **Generate Secure Session IDs:**
   - For stateful sessions (e.g., resumable streams in `/sessions/stream`), use cryptographically secure random generators: In Python, `secrets.token_hex(32)`; in Node.js, `crypto.randomBytes(32).toString('hex')`.
   - Ensure IDs are at least 128 bits long to resist guessing. Rotate IDs every 30-60 minutes or on sensitive actions.

3. **Bind IDs to User Info:**
   - Concatenate session ID with a user-specific hash: e.g., `<sha256(user_id)>:<session_id>`.
   - Store in queues (e.g., Redis or Kafka) with this composite key. On polling (e.g., Server A checking queue), derive the user_id from the token and validate against the key.
   - For multi-server setups, use distributed stores like Redis to share bindings securely.

4. **Verify All Requests:**
   - On every inbound call (e.g., POST /events/trigger), re-validate the auth token and check if the session ID matches the bound user.
   - For resumable streams, use GET with ID and token; reject if unbound or mismatched.

5. **Additional Identifiers and Testing:**
   - Optionally bind to device fingerprints (e.g., IP + User-Agent hash) for extra checks.
   - Simulate attacks: Use scripts to guess IDs or inject events; monitor with intrusion detection (e.g., Fail2Ban). Expire unused sessions after 15 minutes.

This prevents injection and impersonation in distributed setups.

## Gap Analysis

Research into MCP implementations, OAuth proxies, API gateways, and distributed session management reveals several gaps in the spec's best practices. The spec focuses narrowly on OAuth-specific and session issues but omits broader threats common to API ecosystems and LLM integrations. Below is a table summarizing key gaps, substantiated by sources:

| Gap | Description | Why Not Covered in Spec | Substantiation |
|-----|-------------|-------------------------|---------------|
| **Prompt Injection** | Attackers inject malicious prompts via tools or contexts, leading to unauthorized actions or data leaks in LLM-integrated MCP servers. | Spec mentions "prompt injection" in session hijacking but lacks dedicated mitigations beyond binding IDs. | MCP involves LLMs invoking tools; RedHat's analysis highlights prompt injection as a top risk in MCP. |
| **Excessive Data Exposure** | MCP servers may return more data than needed (e.g., full user profiles in tool responses), risking privacy breaches. | Spec addresses token risks but not data filtering in responses. | OWASP API Top 10 ranks this #3; APIs often expose sensitive fields without filtering. |
| **Lack of Rate Limiting** | No controls for request volume, enabling DoS or brute-force attacks on MCP endpoints. | Spec mentions rate limiting in token passthrough risks but doesn't mandate it. | Essential for API gateways; OWASP highlights it as a top vulnerability. |
| **Insufficient Token Validation** | Beyond audience/issuer, no emphasis on expiration, revocation, or signature checks. | Spec forbids passthrough but assumes basic validation. | RFC 9700 details full validation needs; token theft is common in MCP. |
| **Encryption Gaps** | No requirements for data in transit (beyond implied HTTPS) or at rest. | Spec assumes HTTP but doesn't specify TLS versions or cipher suites. | OAuth BCP mandates TLS 1.3; API best practices require encryption. |
| **Logging and Monitoring Deficiencies** | Risks of logging sensitive tokens or lacking anomaly detection. | Spec touches on audit trails in passthrough but not comprehensively. | OWASP API Top 10 includes insufficient logging; critical for distributed systems. |
| **Broken Object/Function Level Authorization** | No checks for fine-grained access to MCP objects (e.g., sessions or tools). | Spec covers user binding but not role-based controls. | OWASP #1 and #5; common in APIs. |

These gaps stem from the spec's focus on core protocol risks, but MCP's LLM and proxy nature introduces model-specific threats.

## Some Recommendations for Addressing Gaps

We could recommend the following additional best practices (along with any others) + how-to steps:

1. **Mitigate Prompt Injection:**
- Validate all inputs (e.g., tool parameters) using schema enforcement (JSON Schema in MCP tools).
- How-To: In `/tools/invoke`, sanitize prompts with allowlists; use libraries like `langchain` for LLM guarding. Test with adversarial prompts.

2. **Prevent Excessive Data Exposure:**
- Filter responses to return only requested fields.
- How-To: Implement response masking (e.g., via middleware in the MCP server). Use GraphQL for query control if applicable.

3. **Enforce Rate Limiting:**
- Limit requests per user/token (e.g., 100/min).
- How-To: Integrate with API gateways like Kong; use token buckets in code (e.g., Redis-based).

4. **Enhance Token Validation:**
- Add revocation lists and full claim checks.
- How-To: Use AS introspection; revoke on logout via back-channel (RFC 7009).

5. **Require Encryption:**
- Mandate TLS 1.3 for all endpoints; encrypt stored sessions.
- How-To: Configure servers (e.g., Nginx) with strong ciphers; use vaults like HashiCorp for secrets.

6. **Improve Logging/Monitoring:**
- Log events without PII; alert on anomalies.
- How-To: Use structured logging (e.g., JSON format); integrate with tools like Splunk forreal-time analysis.
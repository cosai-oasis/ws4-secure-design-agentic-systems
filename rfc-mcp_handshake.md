# [DRAFT -- RFC Zero-Trust MCP Handshake]

**Authors:**
@David Pierce, MPA

## **Summary**
I added a TLS handshake to MCP by associating the auth'd identity with the intended tool invocation.

## **Priority**
* P0: This is critical to include in the next release from this workstream.

## **Level of Effort**
* Small: This will take a few days to document.

## **Drawbacks**
Are there any reasons why we should not do this?
No, this is narrowly scoped on purpose.

Please consider:
* is it too opinionated? nope
* is it too complex to implement? nuh uh
* does the ecosystem exist to support this yet? yes, any FaaS or localhost

## **Alternatives**
What other designs have been considered? What is the impact of not doing this?

Externalizing or differently contextualizing that tool, but where the data management is more complicated.

## **Reference Material & Prior Art**
* Is there an existing framework or paper that discusses this?
* Was this discussed in a talk that was recorded?

www.latentspace.tools, www.zeroday.tools


## **Unresolved questions**
* What help from the group do you need to make this successful?

More awesome questions from y'all; glad to help make the robots safe

### Target-State Architecture for Zero-Standing Privileges

A secure integration pattern enabling AI assistants to interact with sensitive business systems through coordinated, transaction-specific authentication protocols with built-in defense-in-depth.

#### Overview

The MCP Handshake Architecture provides an enterprise-grade security framework for AI integrations, implementing a defense-in-depth strategy with clear separation of concerns. It uses a two-phase handshake mechanism ensuring transaction-specific authorization with zero standing privileges, aligning with modern zero trust principles and data classification requirements.

#### Key Components and Terminology

- **AI Assistant** implements the **Local MCP Client** - initiates requests but cannot directly access sensitive APIs
- **Confirmation Agent** implements the **Remote MCP Service** - acts as a secure gateway validating all operations
- **State Store** - provides atomic token management (typically Redis, DynamoDB, or similar with TTL support)
- **User Identity Provider** - external system for user authentication and session token issuance
- **Target Enterprise APIs** - back-end systems containing sensitive data or operations

#### Core Architecture Principles

##### 1. Dual-Agent Authority with Coordinated Components

The architecture implements separation of powers through a dual-validation pattern:

- **Local MCP Client (implemented by AI Assistant)**: Initiates transaction requests and manages client-side workflow, but cannot directly access sensitive systems.
- **Remote MCP Service (implemented by Confirmation Agent)**: Acts as a secure gateway that independently validates operations, manages token lifecycle, and is the only component with access to sensitive API credentials.
- **Secure State Store**: Tracks ephemeral token states and ensures atomic consumption.
   Each component maintains isolated security contexts connected through cryptographically verified handshakes.

##### 2. Ephemeral Action Authorization with Replay Protection

Every sensitive operation requires explicit, time-bound authorization:

- **Phase 1: Request Authorization**: Authenticated user requests an operation.
- **Phase 2: Nonce Generation & Parameter Binding**: A unique nonce (ephemeral token) is generated and cryptographically bound to the parameter hash.
- **Phase 3: Atomic Execution & Token Consumption**: Operation proceeds after validation; token is atomically consumed.
   This provides two-factor replay protection (ephemeral token + parameter hash binding).

##### 3. Tiered Access Control

Access is tiered based on data classification:

1. **Public (Tier 1)**: Basic validation, minimal auth (e.g., public reference data).
2. **Internal (Tier 2)**: PKI verification, parameter sanitization (e.g., internal reports).
3. **Confidential (Tier 3)**: Comprehensive validation (Regex, Schema, AST), parameter transformation (e.g., financial operations, PII access).
4. **Restricted (Tier 4)**: All lower-tier validations + independent secondary validation, highest sensitivity (e.g., admin actions, critical changes).

#### Implementation Reference Architecture

```ini
┌─────────────────┐                   ┌─────────────────────────┐
│                 │                   │                         │
│   AI Assistant  │                   │ OAuth Identity Provider │
│  (Primary Agent)│                   │ (PayPal, Cloudflare,    │
│                 │                   │  Google, etc.)          │
└───────┬─────────┘                   └───────────┬─────────────┘
        │                                         │ Session Token
        │                                         │ (e.g., JWT)
        │ 1. Auth Req (Tool + Params + Metadata) ▼
        │ read: HTTP POST + OAuth Headers ┌─────────────────┐
        ├────────────────────────────────>│                 │
        │    (per-provider UUID)          │                 │
        │                                 │ Confirmation    │
        │ 2. Ephemeral Tx Token <---------│ Agent + State   │
        │                                 │ Store           │
        │ 3. Execute Tool (Tool + Params) │                 │
        │ read: new-HTTP POST Request     │                 │
        ├────────────────────────────────>│                 │
        │   (UUID + Ephemeral Tx Token)   │                 │
        │                                 │                 │
        │                                 │                 │
        │ 4. Result + Proof <-------------│                 │
        │                                 └───────┬─────────┘
        │                                         │
        │                                         │ Validated Call
        │                                         ▼
        │                           ┌─────────────────────────┐
        │                           │                         │
        │                           │    Secure VPC/Cloud     │
        │                           │    Environment          │
        │                           │  ┌───────────────────┐  │
        │                           │  │                   │  │
        │                           │  │ Enterprise APIs   │  │
        │                           │  │ & Services        │  │
        │                           │  │                   │  │
        │                           │  └───────────────────┘  │
        │                           │                         │
        │                           └─────────────────────────┘

```

---

<!-- Page Break -->

### Reference Implementation Schema (MCP.Handshake.v1.1)

### `transaction` (REQUIRED)
Contains core details about the specific request.

- **`id`** (string, UUID, REQUIRED): A unique identifier for this transaction.
- **`timestamp`** (string, ISO-8601, REQUIRED): Timestamp for when the transaction was initiated.
- **`oauth_session_id`** (string, UUID, REQUIRED): Links this transaction to the OAuth validation session.
- **`request_ip`** (string, OPTIONAL): The IP address from which the client request originated.
- **`user_agent`** (string, OPTIONAL): The client user agent string.

### `identity` (REQUIRED)
Information about the authenticated user, extracted from OAuth provider validation.

- **`sub`** (string, REQUIRED): The user's unique identifier from the OAuth provider.
- **`provider`** (string, REQUIRED): The OAuth provider that validated this identity (matches X-OAuth-Provider header).
- **`email`** (string, OPTIONAL): The user's email address from OAuth claims.
- **`name`** (string, OPTIONAL): The user's display name from OAuth claims.
- **`roles`** (array of strings, OPTIONAL): A list of roles assigned to the user.
- **`validated_at`** (string, ISO-8601, OPTIONAL): Timestamp of when the OAuth token was validated.

### `action` (REQUIRED)
Describes what action is being authorized.

- **`tool`** (string, REQUIRED): The name of the tool being invoked (e.g., `create_refund`).
- **`parameters_hash`** (string, SHA256, REQUIRED): A cryptographic fingerprint of the tool's specific invocation parameters for integrity checks.
- **`operation`** (string, OPTIONAL): The specific operation within the tool (e.g., `execute`, `validate`).
- **`sensitivity`** (string, enum: `CONFIDENTIAL`, `PUBLIC`, OPTIONAL): The operational sensitivity level of the action.
- **`data_classification`** (object, OPTIONAL): Details about the type of data being accessed.
  - **`value`** (string, REQUIRED if object present): The classification value (e.g., `PII`, `CONFIDENTIAL`).
  - **`reason`** (string, OPTIONAL): A brief explanation for the classification.
  - **`attesting_agent_id`** (string, OPTIONAL): The identifier of the agent that attested to this classification.

### `authorization` (REQUIRED)
The ephemeral token and related authorization details.

- **`ephemeral_token`** (string, JWT, REQUIRED): A single-use, short-lived token binding identity→action.
- **`expires_at`** (string, ISO-8601, REQUIRED): The expiration timestamp of the ephemeral token.
- **`jti`** (string, UUID, REQUIRED): Unique token identifier used for atomic consumption tracking.
- **`issued_at`** (string, ISO-8601, OPTIONAL): When the ephemeral token was issued.
- **`not_before`** (string, ISO-8601, OPTIONAL): Earliest time the token can be used.
- **`scope`** (array of strings, OPTIONAL): Authorized scopes for this action.

### `validation` (OPTIONAL)
Records the results of any policy or security checks performed before approving the request.

- **`status`** (string, enum: `APPROVED`, `DENIED`, REQUIRED if section present): The final validation status.
- **`timestamp`** (string, ISO-8601, REQUIRED if section present): When validation was performed.
- **`checks_performed`** (array of strings, OPTIONAL): List of validation checks executed:
  - `oauth_token_valid`: OAuth token was successfully validated
  - `user_role_check`: User has required roles
  - `parameter_validation`: Parameters match the hash
  - `rate_limit_check`: Request within rate limits
  - `policy_check`: Passes policy engine rules
- **`policy_version`** (string, OPTIONAL): Version of the policy engine used.
- **`tier_level`** (string, OPTIONAL): Security tier determined during validation.
- **`reason`** (string, OPTIONAL): Explanation, typically provided if status is `DENIED`.

### `audit` (OPTIONAL)
Contains information essential for logging and security audits.

- **`client_id`** (string, REQUIRED if section present): Identifier for the client application.
- **`integration_id`** (string, REQUIRED if section present): Identifier for the specific integration.
- **`correlation_id`** (string, OPTIONAL): For distributed tracing across systems.
- **`session_fingerprint`** (string, OPTIONAL): Client session fingerprint for security.

### `receipt` (OPTIONAL)
Provides cryptographic proof of the transaction for non-repudiation.

- **`transaction_proof`** (string, REQUIRED if section present): Cryptographic signature of transaction.
- **`timestamp`** (string, ISO-8601, REQUIRED if section present): When receipt was generated.
- **`algorithm`** (string, OPTIONAL): Signature algorithm used (e.g., `RS256`, `HS256`).

### `error_handling` (REQUIRED - always present)
A dedicated section for reporting errors. This object is **always present** to ensure structural consistency. Fields are `null` when no error, populated when error occurs.

- **`status_code`** (integer or null): HTTP status code (e.g., `400`, `500`), or `null` if no error.
- **`error_type`** (string or null): Specific error type, or `null` if no error:
  - `oauth_validation_error`: OAuth token validation failed
  - `token_expired`: Ephemeral token has expired
  - `token_consumed`: Token already used
  - `parameter_mismatch`: Parameters don't match hash
  - `permission_denied`: User lacks required permissions
  - `rate_limit_exceeded`: Too many requests
- **`message`** (string or null): Descriptive error message, or `null` if no error.
- **`retry_allowed`** (boolean or null): Whether retry is safe, or `null` if no error.

***

```json
{
  "transaction": {
    "id": "tx-550e8400-e29b-41d4-a716-446655440000",     // REQUIRED
    "timestamp": "2024-01-21T10:30:00Z",                 // REQUIRED
    "oauth_session_id": "oauth-550e8400-e29b-41d4",      // REQUIRED
    "request_ip": "192.168.1.100",                       // OPTIONAL
    "user_agent": "MCP-Client/1.0"                       // OPTIONAL
  },
  
  "identity": {                                           // REQUIRED section
    "sub": "user-123",                                    // REQUIRED
    "provider": "paypal",                                 // REQUIRED
    "email": "user@example.com",                          // OPTIONAL
    "name": "John Doe",                                   // OPTIONAL
    "roles": ["admin", "refund_agent"],                   // OPTIONAL
    "validated_at": "2024-01-21T10:29:55Z"               // OPTIONAL
  },
  
  "action": {                                             // REQUIRED section
    "tool": "create_refund",                              // REQUIRED
    "parameters_hash": "7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730",  // REQUIRED
    "operation": "execute",                               // OPTIONAL: Specific operation
    "sensitivity": "CONFIDENTIAL",                        // OPTIONAL: Data sensitivity level
    "data_classification": {                              // OPTIONAL: Data handling info
      "value": "PII",
      "reason": "Contains customer financial data"
    }
  },
  
  "authorization": {                                      // REQUIRED section
    "ephemeral_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",  // REQUIRED
    "expires_at": "2024-01-21T10:30:30Z",                // REQUIRED
    "jti": "550e8400-e29b-41d4-a716-446655440001",       // REQUIRED
    "issued_at": "2024-01-21T10:30:00Z",                 // OPTIONAL
    "not_before": "2024-01-21T10:30:00Z",                // OPTIONAL
    "scope": ["refunds", "customer_data"]                // OPTIONAL: Authorized scopes
  },
  
  "validation": {                                         // OPTIONAL section
    "status": "APPROVED",                                 // REQUIRED if section present
    "timestamp": "2024-01-21T10:30:00Z",                 // REQUIRED if section present
    "checks_performed": [                                 // OPTIONAL
      "oauth_token_valid",
      "user_role_check",
      "parameter_validation",
      "rate_limit_check"
    ],
    "policy_version": "1.2.0"                            // OPTIONAL: Policy engine version
  },
  
  "audit": {                                             // OPTIONAL section
    "client_id": "mcp-client-prod-001",                  // REQUIRED if section present
    "integration_id": "paypal-refund-system",            // REQUIRED if section present
    "correlation_id": "corr-123456",                     // OPTIONAL: For distributed tracing
    "session_fingerprint": "fp-abc123"                   // OPTIONAL: Client fingerprint
  },
  
  "error_handling": {                                    // ALWAYS PRESENT (all fields null when no error)
    "status_code": null,                                 // INTEGER when error, null otherwise
    "error_type": null,                                  // STRING when error, null otherwise
    "message": null,                                     // STRING when error, null otherwise
    "retry_allowed": null                                // BOOLEAN when error, null otherwise
  }
}

```

### Operational Lifecycle

**Integration Setup Phase:** Enterprise, IT/Ops, and Application teams collaborate to define classifications, configure environments, and implement integration logic.
**Transaction Execution Flow:**

1. User authenticates; Local MCP Client collects request details.
2. **Handshake Phase 1 (Request Authorization)**: Local Client sends request; Remote Service validates session, hashes parameters, generates ephemeral token bound to hash.
3. **Handshake Phase 2 (Execute Operation)**: Local Client sends parameters and tokens; Remote Service re-verifies hash, atomically consumes token, performs tiered validation.
4. Operation executes if all checks pass; results and proof returned.

---

#### Data Classification Mapping

| Data Class | Description                     | Examples                                | Security Extensions Required      |
|------------|---------------------------------|-----------------------------------------|-----------------------------------|
| **Class 1: PII** | Most sensitive personal data      | SSN, payment methods, credentials       | per-integration specifics         |
| **Class 2: Sensitive Personal Data** | Financial txns, personal details | Txn history, refunds, balance         | Transaction-bound tokens + add'l  |
| **Class 3: Confidential Personal Data** | Business-sensitive operations   | Customer profiles, invoices, processing | Transaction-bound tokens + enhanced validation |
| **Class 4: Internal Data** | Standard business operations    | Exchange rates, general account info  | Standard MCP 2.1 authorization    |
| **Class 5: Public Data** | Non-sensitive operations        | Public API endpoints, documentation   | No additional authorization       |

#### Required Custom Extensions

1. **Transaction-Bound Ephemeral Tokens (Class 1-3)**: Cryptographically bind tokens to operation parameters (toolName, paramsHash, userId, dataClass, short expiry).
2. **Atomic Token Consumption (Class 1-3)**: Prevent replay via one-time use (e.g., Redis `EVAL` for GET & DEL).

**Class 4-5 Operations (Internal/Public Data)**: Standard single-phase MCP 2.1 (bearer token).

```ini
┌─────────────────┐    Standard MCP 2.1    ┌──────────────────┐
│   AI Assistant  │◄──── Single Phase ─────┤ Standard MCP 2.1 │
│ (Class 4-5 ops) │      Bearer Token      │   Authorization  │
└─────────────────┘                        └──────────────────┘

```

**Class 1-3 Operations (PII/Sensitive/Confidential)**: Two-phase zero-trust.

```ini
┌─────────────────┐                        ┌──────────────────┐
│   AI Assistant  │                        │ Standard MCP 2.1 │
│ (Class 1-3 ops) │◄─── Session Token ─────┤   Authorization  │
└─────────┬───────┘                        └──────────────────┘
          │ Sensitive Operations (send_money, refund, etc.)
          ▼
┌─────────────────┐    2-Phase Flow        ┌──────────────────┐
│ Enhanced Local  │◄─── Phase 1: Auth  ────┤ Zero-Trust MCP   │
│ MCP Client      │◄─── Phase 2: Execute ──┤ Extension Service│
└─────────────────┘                        └────────┬─────────┘
                                                    │ Class 1-2 Only
                                                    ▼
                                         ┌──────────────────┐
                                         │ Confirmation     │
                                         │ Agent Validator  │
                                         └──────────────────┘

```

#### Financial API Tool Classification Examples

```typescript
const TOOL_CLASSIFICATIONS = {
  "create_payment_method": 1, "update_customer_payment": 1, // Class 1
  "send_money": 2, "refund_transaction": 2,                 // Class 2
  "create_invoice": 3, "process_payment": 3,                // Class 3
  "list_transactions": 4, "get_account_balance": 4,         // Class 4
  "get_exchange_rate": 5                                    // Class 5
};

```

Class 4-5 operations use standard MCP 2.1. Class 1-3 layer zero-trust extensions, determined by `TOOL_CLASSIFICATIONS`.

#### Implementation Notes

* Every JSON-RPC message MUST be a new HTTP POST request
* OAuth tokens travel in HTTP headers, not in the JSON-RPC payload
* The ephemeral token is consumed atomically using Redis with the JTI as key
* Parameters can be validated server-side if included in the authorization request
* The oauth_session_id allows correlation between OAuth validation and MCP operations

#### Ephemeral Token Claims

```json
{
  "sub": "user-123",              // REQUIRED: User ID from OAuth
  "iss": "mcp-server",           // REQUIRED: Token issuer
  "aud": "mcp-executor",         // REQUIRED: Token audience
  "exp": 1705838430,             // REQUIRED: Expiry timestamp
  "iat": 1705838400,             // REQUIRED: Issued at timestamp
  "jti": "550e8400-e29b-41d4-a716-446655440001",  // REQUIRED: Unique ID for atomic consume
  
  "mcp": {                       // REQUIRED: MCP-specific claims
    "provider": "paypal",        // REQUIRED: OAuth provider
    "tool": "create_refund",     // REQUIRED: Authorized tool
    "parameters_hash": "7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730",  // REQUIRED
    "oauth_session_id": "oauth-550e8400-e29b-41d4"  // REQUIRED: Links to OAuth session
  }
}
```

---

### Token Signing and Verification

This section clarifies the cryptographic signing requirements for ephemeral tokens in the MCP Handshake architecture. The security of the system relies on the **cardinality binding** between identity, tool, and parameters - not on any specific signing algorithm.

### Key Security Property: Cardinality Binding

The critical security property is the cryptographic binding of three elements:
1. **Identity** (WHO) - The authenticated user from OAuth
2. **Tool** (WHAT) - The specific tool being invoked
3. **Parameters** (WITH WHICH) - The exact parameters via SHA256 hash

This binding ensures that a token authorizing `user-123` to execute `create_refund` with specific parameters cannot be used to:
- Authorize a different user
- Execute a different tool
- Use different parameters

**The signing algorithm is merely the mechanism to ensure this binding cannot be forged.**

### Ephemeral Token Generation

The Remote MCP Service MUST sign ephemeral tokens using a cryptographically secure method:

```javascript
// Example using HS256 (symmetric)
const ephemeralToken = jwt.sign({
  sub: getUserId(sessionToken),              // User ID from OAuth
  exp: Math.floor(Date.now() / 1000) + 30,  // 30 second TTL
  jti: uuid.v4(),                           // Unique ID for atomic consumption
  iss: "mcp-server",                        // Token issuer
  aud: "mcp-executor",                      // Token audience
  mcp: {
    provider: oauthProvider,                // From X-OAuth-Provider header
    tool: tool,                             // Tool being authorized
    parameters_hash: parameters_hash,        // SHA256 of parameters
    oauth_session_id: getSessionId(sessionToken)
  }
}, JWT_SECRET, { algorithm: 'HS256' });
```

### Algorithm Flexibility

The MCP Handshake architecture is **algorithm-agnostic**. Implementers MAY use any secure signing algorithm appropriate for their security requirements:

```javascript
// Example: Using RS256 (asymmetric)
const ephemeralToken = jwt.sign(payload, privateKey, { algorithm: 'RS256' });

// Example: Using ES256 (elliptic curve)
const ephemeralToken = jwt.sign(payload, ecPrivateKey, { algorithm: 'ES256' });

// Example: Future quantum-resistant algorithm
const ephemeralToken = jwt.sign(payload, quantumKey, { algorithm: 'CRYSTALS-DILITHIUM' });
```

**Supported algorithms include but are not limited to:**
- **Symmetric**: HS256, HS384, HS512
- **Asymmetric**: RS256, RS384, RS512, PS256, PS384, PS512
- **Elliptic Curve**: ES256, ES384, ES512
- **Future/Quantum-Resistant**: Any standardized post-quantum algorithms

The choice of algorithm should be based on:
- Performance requirements
- Key management capabilities
- Regulatory compliance needs
- Future-proofing considerations (e.g., quantum resistance)

### Token Verification

When receiving the ephemeral token, the service MUST:

```javascript
async function validateAndConsumeToken(token, actualParams) {
  try {
    // 1. Verify JWT signature (algorithm-agnostic)
    const claims = jwt.verify(token, JWT_SECRET_OR_PUBLIC_KEY);
    
    // 2. Check expiration
    if (claims.exp < Date.now() / 1000) {
      throw new Error("Token expired");
    }
    
    // 3. Validate parameter hash matches (THE CRITICAL BINDING)
    const actualHash = sha256(JSON.stringify(actualParams));
    if (actualHash !== claims.mcp.parameters_hash) {
      throw new Error("Parameter tampering detected");
    }
    
    // 4. Atomically consume the token
    const consumed = await redis.eval(
      CONSUME_TOKEN_SCRIPT,
      1,
      `token:${claims.jti}`
    );
    
    if (!consumed) {
      throw new Error("Token already used");
    }
    
    return claims;
  } catch (error) {
    throw new Error(`Token validation failed: ${error.message}`);
  }
}
```

### Security Considerations

1. **Key Management**: Regardless of algorithm choice, signing keys MUST be:
   - Stored securely (e.g., HSM, secure key management service)
   - Rotated periodically
   - Never exposed in logs or error messages

2. **Algorithm Migration**: Systems SHOULD be designed to support algorithm migration:
   ```javascript
   // Support multiple algorithms during transition
   const algorithms = ['HS256', 'RS256', 'ES256'];
   const claims = jwt.verify(token, keyResolver, { algorithms });
   ```

3. **Quantum Readiness**: While current algorithms are sufficient, implementers SHOULD:
   - Design systems to support algorithm updates
   - Monitor NIST post-quantum cryptography standardization
   - Plan for migration when quantum-resistant algorithms mature

### Implementation Notes

- The `jti` (JWT ID) MUST be globally unique to enable atomic consumption
- The `parameters_hash` MUST use a consistent serialization method
- Token TTL (30 seconds) is a balance between security and usability
- The atomic consumption mechanism (e.g., Redis EVAL) is algorithm-independent

### Summary

The MCP Handshake's security comes from the **cryptographic binding of identity→tool→parameters**, not from any specific signing algorithm. This design allows:
- Flexibility in algorithm choice
- Future-proofing against quantum threats  
- Adaptation to different regulatory environments
- Performance optimization based on use case

The signing algorithm is simply the cryptographic proof that this binding has not been tampered with - any secure algorithm that provides this guarantee is acceptable.

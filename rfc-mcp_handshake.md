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

```mermaid
sequenceDiagram
    participant A as AI Assistant<br>(Primary Agent)
    participant U as User Identity Provider<br>(Session Auth)
    participant C as Confirmation Agent + State Store
    box Secure VPC/Cloud Environment
    participant E as Enterprise APIs & Services
    end

    U->>A: Session Token<br>(e.g., JWT)
    A->>C: 1. Auth Req (Tool + Params + Metadata)<br>(Session Token)
    C-->>A: 2. Ephemeral Tx Token
    A->>C: 3. Execute Tool (Tool + Params)<br>(Session Token + Ephemeral Tx Token)
    C-->>A: 4. Result + Proof
    C->>E: Validated Call
```

---

<!-- Page Break -->

### Reference Implementation Schema (MCP.Handshake.v1)

*   **`transaction`**: Contains core details about the specific request.
    *   `id` (string, UUID): A unique identifier for this transaction.
    *   `timestamp` (string, ISO-8601 date-time): Timestamp for when the transaction was initiated.
    *   `user` (object): Information about the authenticated user.
        *   `id` (string): The user's unique identifier.
        *   `roles` (array of strings): A list of roles assigned to the user.

*   **`tool`**: Describes the client or service making the API call.
    *   `name` (string): The name of the tool (e.g., `data-export-service`).
    *   `version` (string): The version of the tool (e.g., `1.2.3`).
    *   `sensitivity` (string, enum: `CONFIDENTIAL`, `PUBLIC`): The operational sensitivity level of the tool.
    *   `parameters_hash` (string, SHA256): A cryptographic fingerprint of the tool's specific invocation parameters for integrity checks.

*   **`target_api`**: Specifies the destination API and the action being requested.
    *   `name` (string): The identifier of the API being called.
    *   `operation` (string): The specific operation or endpoint being invoked on the target API.
    *   `data_classification` (object, optional): Details about the type of data being accessed.
        *   `value` (string or null): The classification value (e.g., `PII`, `CONFIDENTIAL`).
        *   `reason` (string or null): A brief explanation for the classification.
        *   `attesting_agent_id` (string or null): The identifier of the agent or system that attested to this data classification.

*   **`authentication`**: Holds the tokens and state used to authenticate the request.
    *   `session_token` (string): A long-lived session token (e.g., JWT) representing the authenticated user or service session.
    *   `ephemeral_token` (string): A single-use, short-lived token generated for this specific transaction.
    *   `expiry` (string, ISO-8601 date-time): The expiration timestamp of the ephemeral token.
    *   `token_state` (object): Tracks the consumption status of the ephemeral token.
        *   `consumed` (boolean): Indicates whether the ephemeral token has been consumed.
        *   `consumption_timestamp` (string or null, ISO-8601 date-time): Timestamp of when the ephemeral token was consumed, if applicable.

*   **`validation`**: Records the results of any policy or security checks performed before approving the request.
    *   `status` (string, enum: `APPROVED`, `DENIED`): The final validation status of the request.
    *   `timestamp` (string, ISO-8601 date-time): Timestamp of when the validation was performed.
    *   `checks_performed` (array of strings): A list of specific validation checks that were executed (e.g., `parameter_validation`, `auth_check`).
    *   `tier_level` (string): The security or operational tier level determined or applied during validation (e.g., `CONFIDENTIAL`, `HIGH`).
    *   `reason` (string or null): An optional explanation, typically provided if the status is `DENIED`.

*   **`audit`**: Contains information essential for logging and security audits.
    *   `request_ip` (string): The IP address from which the client request originated.
    *   `client_id` (string): An identifier for the client application or service.
    *   `integration_id` (string): An identifier for the specific integration point or workflow.

*   **`receipt`**: Provides a cryptographic proof of the transaction for non-repudiation.
    *   `transaction_proof` (string): A cryptographic signature or hash of critical transaction details.
    *   `timestamp` (string, ISO-8601 date-time): Timestamp marking when the receipt was generated.

*   **`error_handling`**: A dedicated section for reporting errors. This object is **always present** in the handshake message to ensure structural consistency. Its fields are populated with error details if an error occurs; otherwise, they remain `null`.
    *   `status_code` (integer or null): The HTTP status code associated with the error (e.g., `400`, `500`), or `null` if no error.
    *   `error_type` (string or null): A specific error type or code (e.g., `validation_error`, `token_expired`), or `null` if no error.
    *   `message` (string or null): A descriptive message explaining the error, or `null` if no error.
    *   `retry_allowed` (boolean or null): Indicates whether the client can safely attempt the request again, or `null` if not applicable or no error.

***

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MCP.Handshake.v1",
  "description": "Schema for a handshake request, providing context and metadata for secure API interactions.",
  "type": "object",
  "properties": {
    "transaction": {
      "type": "object",
      "description": "Details about the specific transaction.",
      "properties": {
        "id": {
          "type": "string",
          "format": "uuid",
          "description": "Unique identifier for this request (UUID)."
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp of the transaction initiation (ISO-8601)."
        },
        "user": {
          "type": "object",
          "description": "Information about the authenticated user.",
          "properties": {
            "id": {
              "type": "string",
              "description": "User identifier."
            },
            "roles": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "List of user roles."
            }
          },
          "required": ["id", "roles"]
        }
      },
      "required": ["id", "timestamp", "user"]
    },
    "tool": {
      "type": "object",
      "description": "Details about the tool making the request.",
      "properties": {
        "name": {
          "type": "string",
          "description": "Tool name (e.g., `data-export-service`)."
        },
        "version": {
          "type": "string",
          "description": "Tool version (e.g., `1.2.3`)."
        },
        "sensitivity": {
          "type": "string",
          "enum": ["CONFIDENTIAL", "PUBLIC"],
          "description": "Tool sensitivity level."
        },
        "parameters_hash": {
          "type": "string",
          "description": "SHA256 hash of the tool's parameters."
        }
      },
      "required": ["name", "version", "sensitivity", "parameters_hash"]
    },
    "target_api": {
      "type": "object",
      "description": "Details about the API being called.",
      "properties": {
        "name": {
          "type": "string",
          "description": "Required: API name."
        },
        "operation": {
          "type": "string",
          "description": "Required: Specific API operation."
        },
        "data_classification": {
          "type": "object",
          "description": "Optional: Classification of the data being accessed.",
          "properties": {
            "value": {
              "type": ["string", "null"],
              "description": "Classification value (e.g., `PII`, `CONFIDENTIAL`)."
            },
            "reason": {
              "type": ["string", "null"],
              "description": "Reason for the classification."
            },
            "attesting_agent_id": {
              "type": ["string", "null"],
              "description": "ID of the agent that attested to the classification."
            }
          }
        }
      },
      "required": ["name", "operation"]
    },
    "authentication": {
      "type": "object",
      "description": "Authentication details.",
      "properties": {
        "session_token": {
          "type": "string",
          "description": "JWT or other identity token."
        },
        "ephemeral_token": {
          "type": "string",
          "description": "Single-use, transaction-bound token."
        },
        "expiry": {
          "type": "string",
          "format": "date-time",
          "description": "Token expiry timestamp (ISO-8601)."
        },
        "token_state": {
          "type": "object",
          "description": "Token consumption status.",
          "properties": {
            "consumed": {
              "type": "boolean",
              "description": "Boolean indicating if the token has been consumed."
            },
            "consumption_timestamp": {
              "type": ["string", "null"],
              "format": "date-time",
              "description": "Timestamp of token consumption (ISO-8601)."
            }
          },
          "required": ["consumed"]
        }
      },
      "required": ["session_token", "ephemeral_token", "expiry", "token_state"]
    },
    "validation": {
      "type": "object",
      "description": "Validation results.",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["APPROVED", "DENIED"],
          "description": "Validation status."
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "Validation timestamp (ISO-8601)."
        },
        "checks_performed": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "List of validation checks performed."
        },
        "tier_level": {
          "type": "string",
          "description": "Tier level of the validation (e.g., `CONFIDENTIAL`, `HIGH`)."
        },
        "reason": {
          "type": ["string", "null"],
          "description": "Validation reason (e.g., for failure)."
        }
      },
      "required": ["status", "timestamp", "checks_performed", "tier_level"]
    },
    "audit": {
      "type": "object",
      "description": "Audit information.",
      "properties": {
        "request_ip": {
          "type": "string",
          "description": "Client IP address."
        },
        "client_id": {
          "type": "string",
          "description": "Application identifier."
        },
        "integration_id": {
          "type": "string",
          "description": "Specific integration identifier."
        }
      },
      "required": ["request_ip", "client_id", "integration_id"]
    },
    "receipt": {
      "type": "object",
      "description": "Transaction proof.",
      "properties": {
        "transaction_proof": {
          "type": "string",
          "description": "Cryptographic signature of transaction details."
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp of the receipt (ISO-8601)."
        }
      },
      "required": ["transaction_proof", "timestamp"]
    },
    "error_handling": {
      "type": "object",
      "description": "Error handling information. This object is always present; its fields are populated if an error occurs and are null otherwise.",
      "properties": {
        "status_code": {
          "type": ["integer", "null"],
          "description": "HTTP status code."
        },
        "error_type": {
          "type": ["string", "null"],
          "description": "Error type (e.g., `validation_error`)."
        },
        "message": {
          "type": ["string", "null"],
          "description": "Error message."
        },
        "retry_allowed": {
          "type": ["boolean", "null"],
          "description": "Boolean indicating if retry is allowed."
        }
      }
      // No "required" array within error_handling, as individual fields are nullable and only populated on error.
    }
  },
  "required": [
    "transaction",
    "tool",
    "target_api",
    "authentication",
    "validation",
    "audit",
    "receipt",
    "error_handling" // error_handling is required at the top level
  ]
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

#### Implementation Priority

1. Phase 1: Class 4-5 ops with standard MCP 2.1.
2. Phase 2: Add transaction-bound tokens for Class 3 ops.
3. Phase 3: Integrate dual-agent validation for Class 1-2 ops.
4. Phase 4: Full zero-trust pipeline with comprehensive audit.

---

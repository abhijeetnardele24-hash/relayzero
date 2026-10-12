# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Invariants in RelayZero

1. **Air-Gap Verification:** RelayZero must not initiate outbound network calls at runtime (EGRESS 0).
2. **Prompt Injection Boundary:** All unverified field reports must be encapsulated in `<untrusted_field_evidence>` tags to prevent system prompt override.
3. **Audit Trail Immutability:** Operational actions must be appended to the SHA-256 hash-chained log.
4. **Human Review Prerequisite:** Safety-critical conclusions (locations, trapped counts, evacuations) require human operator confirmation before situation brief export.

## Reporting a Vulnerability

Please report sensitive security issues privately to `security@hackapertus.ch` or via GitHub Security Advisories.

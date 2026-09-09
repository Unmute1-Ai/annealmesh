# Security Policy

## Reporting

Use GitHub private vulnerability reporting/security advisories when available. Do not publish production keys, model credentials, private prompts/data, or exploitable endpoint details in public issues.

## Boundaries

- AnnealMesh evaluates reasoning; it does not grant real-world authority.
- A model, evaluator, scanner, or ranking score cannot override principal policy.
- Secrets belong in managed environment/secret stores.
- Production endpoints should use HTTPS and authentication.
- Logs should avoid raw user audio, credentials, and sensitive prompts unless explicitly required and protected.
- Backend provenance and version/digest metadata should be pinned for audited deployments.

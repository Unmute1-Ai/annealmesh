# Sentinel

Purpose
- Governance, authorization, and policy enforcement.

Responsibilities
- Enforce policies and RBAC for actions across the stack.
- Approve or block recovery actions initiated by IGNIS.
- Log decisions and rationale to RCM for auditability.

Integration
- Input: policy evaluations, risk-state, evidence from AnnealMesh/RCM.
- Output: policy decisions, authorization tokens, audit logs.

Next steps
- Publish policy format and an evaluation API example.
- Implement policy simulation/testing harness.

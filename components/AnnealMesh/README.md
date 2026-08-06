# AnnealMesh

Purpose
- Reasoning evaluation and verification: validate model outputs, run verification pipelines, and produce integrity attestations.

Responsibilities
- Run automated verification checks and scoring on model decisions.
- Produce evidence and attestations stored in RCM.
- Provide interfaces for verification results consumed by PhaseFlow and Sentinel.

Integration
- Input: model outputs, runtime context, policy hints.
- Output: verification reports, integrity tokens, structured evidence (JSON) written to RCM.
- Suggested API: POST /annealmesh/verify -> { report_id }

Next steps
- Add example verification rules and test vectors.
- Provide an example harness to replay model outputs for verification.

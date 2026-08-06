# RCM

Purpose
- Persistent context, evidence storage, and audit trails.

Responsibilities
- Store structured evidence, attestation artifacts, logs, and context snapshots.
- Provide durable, queryable APIs for other components to read/write evidence.
- Support tamper-evident storage or cryptographic integrity checks where appropriate.

Integration
- Input: evidence and reports from AnnealMesh, audit logs from Sentinel, snapshots from PhaseFlow.
- Output: queried records for investigations and recovery procedures.

Next steps
- Define storage schema and retention policy.
- Add example APIs and query patterns.

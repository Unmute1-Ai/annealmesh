# AnnealMesh

**Thermodynamic reasoning evaluation and verification for agentic AI.**

AnnealMesh is an Unmute1AI reasoning-integrity architecture for
evaluating claims, evidence, trajectories, and agent-generated
reasoning using explicit thermodynamic state.

Core quantities:

- Energy (E) — structural and claim-consistency cost
- Temperature (T) — governed exploration
- Entropy (S) — candidate diversity
- Free Energy (F) — `F = E - T*S`

Candidate transitions can be evaluated using Metropolis and
Metropolis-Hastings methods while temperature-changing operations
remain governed and auditable.

AnnealMesh forms the reasoning-verification layer of the broader
Unmute1AI resilience architecture.

**Accessibility First. Always.**

## Setup

```powershell
cd C:\Users\cindy\builds\hermes-nemotron-mesh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

Set model and Speech NIM endpoints in `.env`.

## Web app

```powershell
hermes-web
```

Open `http://127.0.0.1:8080`. Microphone access requires HTTPS when the app is
served from a non-local address.

Production deployments should place the service behind an HTTPS reverse proxy,
keep `.env` outside the image, and expose `/health` to the platform.

## CLI

```powershell
hermes-mesh "Design a fault-tolerant event ingestion service"
hermes-voice .\question.wav -o .\answer.wav
```

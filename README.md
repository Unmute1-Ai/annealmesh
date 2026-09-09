# AnnealMesh

**Thermodynamic reasoning evaluation and verification for agentic AI.**

AnnealMesh is an Unmute1AI reasoning-integrity layer for evaluating claims, evidence, trajectories, and multi-model candidate plans using explicit thermodynamic state.

Core quantities:

- **Energy (E)** — structural / consistency cost
- **Temperature (T)** — governed exploration
- **Entropy (S)** — candidate diversity
- **Free Energy (F)** — `F = E - T*S`

AnnealMesh can rank and verify candidate reasoning while keeping execution authority outside the model layer.

> **Status: production candidate for reasoning verification.** It is not a proof that generated outputs are correct, safe, or authorized to cause effects.

## Architecture

```text
candidate generators
      |
      v
  AnnealMesh
E / T / S / F evaluation
      |
      v
verified candidate / hold
      |
      v
 U1 Sentinel
external authority gate
```

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e .
cp .env.example .env
```

Configure model and speech endpoints in `.env`. Keep production secrets outside source control.

## Web app

```bash
hermes-web
```

Open `http://127.0.0.1:8080`.

For non-local deployment, place the service behind HTTPS and expose `/health` to the platform.

## CLI

```bash
hermes-mesh "Design a fault-tolerant event ingestion service"
hermes-voice ./question.wav -o ./answer.wav
```

## Production principles

- Model/candidate quality does **not** grant execution authority.
- External evaluator/scanner verdicts remain advisory.
- Backend/provider/jurisdiction metadata may influence routing but not principal authority.
- Quantum/backend maturity and verified advantage are separate claims.
- Low-confidence or conflicting evidence should hold/review rather than silently release.
- All public benchmark claims should point to reproducible evidence.

See [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) and [SECURITY.md](SECURITY.md).

## Development

```bash
python -m pip install -e ".[dev]"  # if dev extras are added
python -m compileall -q src
```

The CI workflow performs an install/import/package smoke test without requiring live model endpoints.

---

**Unmute1AI**  
Intelligence recommends. Authority decides.

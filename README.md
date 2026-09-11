# AnnealMesh

**Multi-model candidate generation, ranking, and synthesis.**

[Portfolio](https://github.com/Unmute1-Ai/Unmute1ai#readme) · [Engineering](https://github.com/Unmute1-Ai/U1Ai#readme) · [Security evidence](https://github.com/Unmute1-Ai/glass-box#readme)

AnnealMesh coordinates a planner, parallel candidate generators, a model-based judge, and a final synthesis step. The checked-in Python package includes command-line, web, and speech interfaces.

**Status: development implementation.** Model-based scores are advisory evaluations, not formal proof or authorization to execute actions.

## How it works

1. Generate a short plan with constraints and success criteria.
2. Produce candidates using several reasoning strategies.
3. Rank candidates using structured judge responses.
4. Carry selected candidates into later rounds while lowering sampling temperature.
5. Synthesize a final response from the plan and finalists.

The implementation uses an annealing-inspired temperature schedule. It does not implement a physical thermodynamic system or a general mathematical proof verifier.

## Setup

Requires Python 3.11+ and configured model endpoints.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

On Windows, activate with `.venv\Scripts\activate`. Configure the providers described in [.env.example](.env.example). Keep credentials local.

## Interfaces

| Interface | Command |
| --- | --- |
| Web application | `hermes-web` |
| Text CLI | `hermes-mesh "Compare two approaches to accessible onboarding"` |
| Speech CLI | `hermes-voice ./question.wav -o ./answer.wav` |

The installed command names retain the `hermes-` prefix for compatibility. Speech requires its configured providers as well as model endpoints.

## Development

```bash
python -m compileall -q src
```

The project does not currently declare a `dev` dependency extra. Installation and compilation checks do not validate live provider behavior or response quality.

## Repository map

- [src/hermes_mesh/mesh.py](src/hermes_mesh/mesh.py) — candidate generation, temperature schedule, ranking, and synthesis.
- [src/hermes_mesh/config.py](src/hermes_mesh/config.py) — runtime configuration.
- [src/hermes_mesh/api.py](src/hermes_mesh/api.py) — web service.
- [docs/](docs/) — supporting documentation.
- [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) — deployment requirements.
- [SECURITY.md](SECURITY.md) — security guidance.

## Authority boundary

A candidate's score does not grant permission. Any integration that performs external actions needs a separately enforced authorization boundary. The intended Sentinel relationship is an architecture boundary, not evidence of an integrated enforcement service in this package.

---

**Unmute1AI · Intelligence recommends. Authority decides.**

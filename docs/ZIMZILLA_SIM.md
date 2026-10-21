# ZimZilla-Sim

ZimZilla-Sim restores an offline, reproducible research-orchestration layer for the original 1859 Riemann Hypothesis target. It separates the work into two independent lanes:

- **Crystal:** exact Weil-positivity and full-space operator obligations.
- **Fusion:** reciprocity, conductor movement, and accumulated-error obligations.

It uses Python's standard library only and makes no model calls. Findings are an explicit research ledger, not generated mathematical evidence. It does not calculate a proof, certify a theorem, or claim RH is solved.

## Run

From the repository root after installing the package:

```bash
python -m hermes_mesh.zimzilla_sim
python -m hermes_mesh.zimzilla_sim --seed 1859 --output zimzilla-report.json
```

Run the regression tests from the repository root:

```bash
python -m unittest discover -s tests -p 'test_zimzilla_sim.py'
```

## Integrity and interpretation

The JSON report includes a SHA-256 digest of the canonical report payload before the digest field is added. Re-running with the same seed produces the same payload and digest. The seed is a reproducibility label only; it does not add randomness or strengthen evidence.

The current hard gates remain:
1. derive the exact Weil functional with all pole, gamma, and prime-power terms, then prove positivity over the full admissible class; or
2. prove a joint reciprocity-remainder cancellation identity with a uniform summed bound.

A symmetry, finite computation, test pass, or simulated candidate is not a proof.

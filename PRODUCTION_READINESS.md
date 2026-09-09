# Production Readiness

**Current classification: reasoning-verification production candidate.**

## Build
- [ ] Clean Python install succeeds
- [ ] Package import smoke test passes
- [ ] Wheel builds reproducibly
- [ ] Supported Python versions are defined
- [ ] Dependency versions are reviewed

## Runtime
- [ ] /health monitored
- [ ] Endpoint timeouts/retries bounded
- [ ] Model/provider failures fail closed or degrade safely
- [ ] Secrets supplied outside source control
- [ ] Logs exclude credentials/sensitive payloads
- [ ] Rate limits and authentication configured for public exposure

## Verification
- [ ] Candidate scoring equations/version are recorded
- [ ] Benchmark datasets are versioned
- [ ] Release/hold thresholds are documented
- [ ] External evaluator results remain advisory
- [ ] Model substitution does not change execution authority
- [ ] Quantum/backend claims distinguish theory, prototype, benchmark, and verified advantage

# Validation status

This is an alpha. No promise of zero regressions or low ping.

Validation layers:
- Unit tests: profile selection, matching transport paths, domain validation, password policy, deployment guards, consistent SQLite backup and health failure cases.
- Docker build: production React bundle and pinned upstream image integration.
- CI smoke test: brand strings, readiness, authenticated API, generated users/subscriptions, restart without resetting owner credentials.
- External end-to-end: NOT complete until each supported client is tested through a real TLS domain on the chosen host.
- REALITY/Hysteria2/WireGuard/Shadowsocks: upstream capabilities / explicit configuration only; not auto-provisioned or claimed as end-to-end tested in this alpha.

Inspect GitHub Actions for the actual run result. The existence of this workflow file is not proof that it passed. CI uses temporary generated credentials, never a published fixed administrator password.

Test p50/p95 connection delay, failures, jitter and throughput on the user's actual ISP. A server-side URL request or TCP connect is not the user's proxy latency. Extra fingerprints on the same server do not create distinct routes.

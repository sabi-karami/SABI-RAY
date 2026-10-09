# Build report — SABI-RAY 0.2.0-alpha.1 (verification in progress)

This revision adds opt-in REALITY/Vision and Shadowsocks TCP, local key generation, a 16-chapter Persian handbook, setup helper and sanitized diagnostics.

The first advanced-profile integration run exposed an API compatibility error: REALITY hosts must use `inbound_default`, not a nonexistent `reality` host enum. This was corrected with a regression test. The next CI run must pass before tagging the new release.

The previous 0.1.0-alpha.1 test record below remains historical evidence only, not proof of the new features.

---

# Verified build report — SABI-RAY 0.1.0-alpha.1

Tested application commit: `41fd65d3b322aa129d3abfdb8048aafda9b730d9`.

Successful GitHub Actions run:
https://github.com/sabi-karami/SABI-RAY/actions/runs/37939392617

## Passed

- 45 isolated Python tests (sandbox Python 3.13; CI Python 3.14).
- Python 3.14 syntax validation of added modules and upstream app.
- Production React dashboard build and Docker image build.
- Docker Compose configuration validation.
- Startup, owner login, core/group provisioning, user creation and subscription retrieval.
- Restart: owner credentials and user data preserved.
- Branded subscription title and Telegram support URL.
- All five inbound listeners ready.
- Actual data transfer with Xray client through local nginx and the managed Xray server, fetching https://example.com/: VLESS/WS, Trojan/WS, VMess/WS, VLESS/HTTPUpgrade, VLESS/XHTTP.
- Playwright: real browser login, authenticated dashboard, protocol search, URL filter persistence, reload, mobile layout without horizontal overflow and no JavaScript runtime exceptions during these flows.

## Evidence

Screenshots contain only synthetic CI data, not a deployed customer database:

- [Login](screenshots/login-desktop.png)
- [Dashboard](screenshots/dashboard-desktop.png)
- [Protocol catalog](screenshots/protocols-desktop.png)
- [Mobile protocol catalog](screenshots/protocols-mobile.png)

## Not verified / not implemented

- External TLS edge and real-domain end-to-end connections.
- Actual ISP latency, throughput, jitter or resilience in Iran.
- Deployment on Railway; provider approval remains required by the documented policy gate.
- End-to-end REALITY, Hysteria2, WireGuard and Shadowsocks profiles; upstream capabilities are retained but not auto-provisioned in this alpha.
- Multi-admin access regression suite, load tests, upgrade/restore rehearsal, full security audit.
- Hundreds of new capabilities, autonomous cross-protocol optimization, payments or AI features.
- Independent second-model review: the model connector setup was dismissed, so no model call was made.

This remains an alpha. Successful loopback transfer is not proof of external TLS edge compatibility or low ping. The documentation-only evidence commit following the tested application commit changes no runtime behavior.

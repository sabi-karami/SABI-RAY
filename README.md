# SABI-RAY

<img src="logo.svg" width="96" alt="SABI-RAY logo" />

**Persian-friendly multi-protocol management console. A branded, security-focused PasarGuard distribution.**

**Status: 0.1.0-alpha.1 — tested development preview, NOT production certified.**

[Verified test report](docs/BUILD-REPORT.md) · [Successful CI run](https://github.com/sabi-karami/SABI-RAY/actions/runs/37939392617)

Contact: [@SAHEBKARAMI](https://t.me/SAHEBKARAMI) · [راهنمای فارسی](README-fa.md) · [Source / notices](NOTICE.md)

## What is included

- Real React dashboard branding, localized product names, original logo/favicon/PWA identity, subscription branding and support links.
- Existing PasarGuard users, reseller RBAC, quotas, expiry, traffic reports, API keys, templates, subscription formats, Telegram integration and multi-node management retained from upstream.
- Automatic VLESS/WS, Trojan/WS and VMess/WS provisioning; optional HTTPUpgrade and XHTTP alpha presets.
- Secure first owner initialization via the upstream validated setup API. No `admin/admin`, no sample reseller and no password overwrite on restart.
- Fail-closed setup, process supervision, listener-aware readiness, persistent randomized paths, pinned panel/node images, secret-safe logs and a consistent SQLite backup command.
- Docker, VPS with Caddy TLS, and a policy-gated Railway packaging path.

This is not “hundreds of newly implemented features”. Many advanced capabilities are inherited from PasarGuard. Hysteria2/WireGuard/REALITY/Shadowsocks remain explicit upstream/node configuration, not pretend-enabled buttons. See [protocol matrix](docs/PROTOCOLS.md).

## New installation on an authorized VPS

Requirements: Docker Engine + Compose, a domain pointed at the server, inbound 80/443, and provider permission to operate this service. Build resources must accommodate the React editor dependencies.

```sh
git clone https://github.com/sabi-karami/SABI-RAY.git
cd SABI-RAY
cp .env.sabi.example .env
# Edit .env privately: set PUBLIC_DOMAIN and a unique strong SABI_INITIAL_PASSWORD.
docker compose -f compose.yaml -f compose.vps.yaml up -d --build
docker compose -f compose.yaml -f compose.vps.yaml ps
```

Open `https://YOUR-DOMAIN/dashboard/`. Sign in using the owner credentials you configured. After successful setup, remove `SABI_INITIAL_PASSWORD` from `.env` and recreate the container; it will not reset credentials. Make users from the generated SABI-RAY templates so they receive the correct group.

## Portable Docker

`docker compose -f compose.yaml up -d --build` binds to loopback port 8080 only. Place your own trusted TLS reverse proxy in front of it. Never expose the plain HTTP panel to the public internet. Use `https://YOUR-DOMAIN` for user subscriptions; HTTP-only local testing does not validate TLS profiles.

## Railway

[Read the policy and prerequisites FIRST](docs/RAILWAY.md). Railway explicitly prohibits proxies/anonymization services in its AUP. This repository does not grant permission or evade that policy. Obtain approval for your exact use case; no Railway service has been deployed by this release.

## Safety and tests

- [Actual testing requirements](docs/TESTING.md)
- [Backups and configuration changes](docs/MIGRATION.md)
- Run `python -m unittest discover -s tests_sabi -v` for isolated SABI-RAY unit tests.
- Inspect Actions for Docker/build/smoke outcomes. An alpha build or health check is not proof of working external connectivity.
- Never send tokens, subscription secrets or passwords to public logs/issues.
- No automatic updates, destructive migrations, payment handling, AI service or bot token is enabled without explicit configuration.

## License and provenance

Based on PasarGuard v5.4.1 (commit `b56ffe369f542152c52c69733205baeaf3f6e4cd`). See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). Corresponding source is available in this repository. Original authorship, legal notices, backend import names and compatibility identifiers are preserved. SABI-RAY does not claim authorship of the upstream codebase.

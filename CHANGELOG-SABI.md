# SABI-RAY changelog

## 0.2.0-alpha.1

- Optional automatic REALITY/Vision (TCP 11443) and Shadowsocks AEAD TCP (11444) for new Docker/VPS installations.
- Local persistent X25519 keys, direct host provisioning and explicit Compose port mapping; no keys committed.
- Backwards-compatible state reading with advanced disabled; refuse silent profile/domain changes.
- Wait for node control-plane registration before initial readiness.
- Correct REALITY Host API inheritance and align initial password validation with upstream.
- Interactive private .env setup helper and read-only sanitized doctor.
- 16-chapter Persian handbook with commands, expected results, prerequisites, warnings, backups, recovery, clients and troubleshooting.
- 78 unit tests; seven transfer combinations; focused reseller OWN-scope regression; browser and restart checks.
- Still alpha: no production certification, no Railway deployment, no guaranteed ping, no automatic Hysteria2/WireGuard/SS2022/UDP or migration of existing installations to advanced mode.

## 0.1.0-alpha.1

Initial branded PasarGuard distribution; five web transport presets, secure setup, Docker/VPS/Railway packaging and first successful CI/browser tests.

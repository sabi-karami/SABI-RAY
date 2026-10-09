# Verified build report — SABI-RAY 0.2.0-alpha.1

Tested application commit: `c44ceb157893134ef1046bc3f3fe4338546326c4`.

Successful CI: https://github.com/sabi-karami/SABI-RAY/actions/runs/37942936496

## Passed

- 78 isolated tests: profile validation, initial password policy matched to upstream, state compatibility, direct profile guards, backup, setup helper, sanitized doctor and Persian documentation links.
- Python 3.14 syntax validation; production React dashboard build; Docker image and Compose validation.
- Initial owner setup, core/group/host/template creation, user creation, subscription retrieval and branded support/profile settings.
- All configured web and direct listeners plus completed node control-plane registration before initial readiness.
- Actual Xray data transfer through local nginx/server to https://example.com/: VLESS/WS, Trojan/WS, VMess/WS, VLESS/HTTPUpgrade and VLESS/XHTTP.
- Actual direct VLESS/REALITY/Vision data transfer using a locally controlled TLS 1.3 origin in the CI network; keys generated locally and persisted with mode 0600.
- Actual Shadowsocks AEAD TCP data transfer with the user's generated cipher/credential.
- Subscription output includes REALITY and ss:// links.
- OWN-scoped reseller regression: own-user read succeeds; cross-owner read/update/delete and core access are rejected; user list hides the other reseller's user.
- Browser: real login and authenticated dashboard, protocol filtering, URL persistence/reload, mobile no-horizontal-overflow and no JS runtime exceptions in these flows.
- Restart: owner login and user data persist.

## Issues found and fixed during this iteration

1. REALITY host security must inherit from inbound; the upstream Host API has no `reality` override enum. Fixed and regression-tested.
2. Direct client test temporary files needed an explicit `.json` extension for Xray format detection. This was a test harness issue, not proof of protocol failure after the fix.
3. Listener reachability could become ready before node control-plane registration completed, creating a race with new users. Initial provisioning now waits for the node's `connected` status.
4. Initial password validation now enforces the pinned upstream policy (including two uppercase/lowercase/digits and 72-byte bcrypt boundary), instead of accepting values later rejected by setup API.

## Not verified / not implemented

- Public domain external TLS edge, real ISP latency/throughput/jitter or long-lived stability in Iran.
- Actual Railway deployment or permission from its provider. Automated direct profiles are rejected on Railway; its AUP restrictions remain documented.
- Hysteria2/WireGuard automatic provisioning, public UDP integration, SS2022 or Shadowsocks UDP.
- Complete security audit, all RBAC combinations, high-load tests, production upgrade/restore rehearsal or automatic certificate rotation.
- Automatic activation of advanced profiles on an existing initialized volume. They remain opt-in for NEW installations.
- Second-model review: no completed model connector / no second model call.

This is an alpha, not a production certification. The CI REALITY origin certificate is a temporary self-signed test fixture, not guidance to disable certificate verification in ordinary TLS production profiles. Documentation-only commits after the tested application commit do not alter runtime behavior.

## Training and evidence

- [Complete Persian handbook — 16 chapters](fa/README.md)
- [Direct profiles guide](fa/07-direct-protocols.md)
- Browser screenshots are available as artifacts on the successful run. Older repository screenshots in docs/screenshots are from the 0.1 alpha and should not be mistaken for newly captured production data.

## Previous release

0.1.0-alpha.1 successful CI: https://github.com/sabi-karami/SABI-RAY/actions/runs/37939392617 — historical result for the original five web combinations.

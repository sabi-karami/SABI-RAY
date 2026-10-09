# Verified hotfix — SABI-RAY 0.2.0-alpha.2

Successful PR CI: https://github.com/sabi-karami/SABI-RAY/actions/runs/37944423453

Tested branch commit: `df406623bcb76ab809513b193a9d26cba130da2f`.
Merged into main as `9362c7841bc5e21bed4ea8591155abc3069ca847` through [PR #1](https://github.com/sabi-karami/SABI-RAY/pull/1).

## Fix scope

The message `Startup stopped: Railway prohibits proxy/anonymization services` was emitted by SABI-RAY's own preflight guard, not a Railway API response. The acknowledgement-related exception is now a non-blocking warning. `RAILWAY_APPROVAL_CONFIRMED` is obsolete and ignored; neither a true value nor fabricated provider approval is required by the code. Provider terms remain the operator's responsibility. Password/domain/state and unsupported direct-profile checks remain in place.

## Verified

- 85 unit tests, Python 3.14 syntax validation, production React/Docker build and Compose configuration.
- All existing seven data-transfer combinations, scoped reseller access checks, browser flows and restart persistence.
- Docker simulation of `DEPLOY_MODE=railway`, `RAILWAY_ENVIRONMENT_ID` and `RAILWAY_PUBLIC_DOMAIN`.
- Initial boot with legacy acknowledgement set to false, successful health and owner login, user creation.
- Container recreation on the same volume with no initial password and no acknowledgement variable: owner login and user persisted; installation state bytes unchanged.
- Warning remains visible but does not cause the old startup exception.

## Not verified

No live Railway service was deployed or reconfigured by this hotfix. No external Railway TLS edge, provider permission or Iranian ISP connectivity was tested. The test used Docker on GitHub Actions with simulated environment variables, not Railway. No user credentials or deployment-volume contents were accessed.

Rebuild from the fixed main commit or `v0.2.0-alpha.2`; restarting an old image does not load new code. Preserve your volume and existing domain/profile settings. See [Persian update instructions](fa/10-railway.md) and [English instructions](RAILWAY.md).

---

## Historical 0.2.0-alpha.1 report

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

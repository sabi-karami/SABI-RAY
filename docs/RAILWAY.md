# Railway deployment: technical package, not permission to operate

Railway's Acceptable Use Policy prohibits operating proxies/anonymization services:
https://railway.com/legal/acceptable-use

Do not deploy this use case without obtaining provider approval. A control-only panel is not automatically exempt: ask Railway about the exact use case. Starting with 0.2.0-alpha.2, provider-policy information is a non-blocking startup warning. `RAILWAY_APPROVAL_CONFIRMED` is obsolete and ignored: no value is required and no provider approval is fabricated or recorded by the application. Technical startup is not evidence that the use case is permitted.

If approved:
1. Deploy this repository using its Dockerfile.
2. Attach a volume at `/var/lib/pasarguard`. Use one replica only.
3. Set `DEPLOY_MODE=railway`, `SABI_ADMIN_USER` and a strong `SABI_INITIAL_PASSWORD` in Railway's Variables UI. Do not put secrets in GitHub or chat.
4. Generate a domain for port 8080, then redeploy if the domain was unavailable on the first attempt. `RAILWAY_PUBLIC_DOMAIN` is detected automatically; alternatively set `PUBLIC_DOMAIN` to your TLS-enabled custom domain.
5. Do not enable WireGuard, Hysteria2 or REALITY through the ordinary HTTPS edge. Public UDP/direct TLS transport requirements differ. WebSocket-compatible presets still require real client testing.
6. Visit `/dashboard/`. Remove `SABI_INITIAL_PASSWORD` from Variables after setup succeeds and save your credentials securely. A restart never resets the password.

The health check tests panel reachability and configured node/inbound listeners. It is not a full external client connectivity test. Gateway login rate limiting is intentionally conservative and groups traffic by the immediate proxy address; it is not per-end-user IP enforcement behind Railway. Configure provider-aware trusted proxies before using large shared populations.

Status: alpha; not deployed to Railway or tested from Iranian networks by this build.

## Updating installations blocked by the old guard

If logs contain `Startup stopped: Railway prohibits proxy/anonymization services`, rebuild from the fixed `main` commit or `v0.2.0-alpha.2`. Restarting/redeploying an older image cannot change its code. Verify your GitHub source/branch and the deployment's commit. Preserve the attached volume and existing domain/profile values. The former acknowledgement variable may be removed or left unchanged; it is ignored.

Expected policy message: `WARNING: Railway deployment detected`, not a policy-related startup exception. Strong initial credentials (new installs), valid domain, readiness and unsupported direct-profile checks still apply. No live Railway deployment was performed by this hotfix.

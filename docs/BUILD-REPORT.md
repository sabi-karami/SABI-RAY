# Build report — 0.1.0-alpha.1

## Verified initial build

Commit `b68da6e844b7634107a87de3575d7bcd9168784c` passed:
https://github.com/sabi-karami/SABI-RAY/actions/runs/37938588591

- 45 isolated Python tests (local Python 3.13 and GitHub Python 3.14).
- Syntax compilation of added modules and upstream app using Python 3.14.
- Production React dashboard build.
- Docker image build with pinned panel/node images.
- Docker Compose configuration validation.
- Application startup and readiness including all five configured inbound listeners.
- Owner login, core/group provisioning, user creation and subscription retrieval.
- Container restart: owner login and user persistence.

## Additional verification

Browser login/dashboard and protocol-catalog tests were added after the initial run. Inspect the latest GitHub Actions run for their actual result; this paragraph does not claim they already passed.

## Not verified

No external TLS proxy data-transfer tests, ISP latency benchmark, Railway deployment, advanced UDP/direct-TCP profile integration, or second-model review has been completed. Local browser attempts were blocked by sandbox dependencies; CI runs browsers with their required system dependencies.

A healthy listener is not proof of a successful client data-transfer session. This remains an alpha.

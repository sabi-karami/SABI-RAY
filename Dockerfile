# SABI-RAY alpha. Immutable upstream runtime references; rebuilt branded dashboard.
FROM oven/bun:1.4.2 AS dashboard
WORKDIR /ui
COPY dashboard/package.json dashboard/bun.lock ./
RUN bun install --frozen-lockfile --ignore-scripts
COPY dashboard/ ./
RUN VITE_BASE_API=/ bun --bun run build && cp build/index.html build/404.html

FROM pasarguard/node@sha256:ae7855b30726ab57d4675109dde051a1151679009afcd69fe72d34d767bae455 AS node
FROM pasarguard/panel@sha256:30d7ac51b5822274f55cc2f506663ecf0d564efafc8776a5c3cfffd9cbfd0fce
USER root
RUN apt-get update && apt-get install -y --no-install-recommends nginx openssl ca-certificates curl && rm -rf /var/lib/apt/lists/* /etc/nginx/sites-enabled/default
COPY --from=node /app/main /opt/sabi-node/main
COPY --from=node /usr/local/bin/xray /usr/local/bin/xray
COPY --from=node /usr/local/share/xray /usr/local/share/xray
WORKDIR /code
COPY app/ /code/app/
COPY sabi_ray/ /code/sabi_ray/
COPY --from=dashboard /ui/build/ /code/dashboard/build/
ENV PORT=8080 UVICORN_HOST=127.0.0.1 UVICORN_PORT=8000 UVICORN_PROXY_HEADERS=True UVICORN_FORWARDED_ALLOW_IPS=127.0.0.1 \
    SQLALCHEMY_DATABASE_URL=sqlite+aiosqlite:////var/lib/pasarguard/db.sqlite3 \
    SUBSCRIPTION_PATH=sub XRAY_EXECUTABLE_PATH=/usr/local/bin/xray XRAY_ASSETS_PATH=/usr/local/share/xray PYTHONUNBUFFERED=1
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=300s --retries=3 CMD curl -fsS --max-time 4 http://127.0.0.1:8080/healthz || exit 1
ENTRYPOINT ["python", "-m", "sabi_ray.runtime"]

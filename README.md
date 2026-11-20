# Skunky Search

Authenticated curated-source discovery service. **Not an open-web search engine.**

`POST /v1/search` with `X-Skunky-Token: <managed secret>` and JSON `{"query":"demo","limit":10}` returns enabled registry matches. `GET /healthz` is unauthenticated.

The bundled `example-docs` record is a deterministic demonstration fixture, not an approved production collection source. A production release must consume reviewed, versioned registry data from `skunky-bot/sources` and enforce source permissions and retention.

Local: `pip install -r requirements.txt && SKUNKY_SERVICE_TOKEN=... uvicorn app:app --port 8000`. CI: `pytest`. Do not expose directly to the public internet.

### Web collection registry

Set `SKUNKY_SOURCE_REGISTRY_PATH` to the path of a read-only registry JSON to load approved sources. An unreadable or malformed registry returns HTTP 503. The bundled registry contains the preview fixture.

`POST /v1/search` accepts `collection_only: true` for scheduled scans. It matches all whitespace-delimited terms against source IDs, names, tags or URLs. Results come from enabled entries with `mode: "web-collection"` and `outreach_allowed: false`. Search returns the first matches in registry order up to `limit`.

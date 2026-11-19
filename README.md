# Skunky Search

Authenticated curated-source discovery service. **Not an open-web search engine.**

`POST /v1/search` with `X-Skunky-Token: <managed secret>` and JSON `{"query":"demo","limit":10}` returns enabled registry matches. `GET /healthz` is unauthenticated.

The bundled `example-docs` record is a deterministic demonstration fixture, not an approved production collection source. A production release must consume reviewed, versioned registry data from `skunky-bot/sources` and enforce source permissions and retention.

Local: `pip install -r requirements.txt && SKUNKY_SERVICE_TOKEN=... uvicorn app:app --port 8000`. CI: `pytest`. Do not expose directly to the public internet.

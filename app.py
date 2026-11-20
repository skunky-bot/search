"""Skunky source search: curated registry only, no network search."""
from __future__ import annotations

import hmac
import json
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Skunky Search", version="0.1.0")
REGISTRY = Path(__file__).with_name("registry.json")


def authorize(token: str | None = Header(default=None, alias="X-Skunky-Token")) -> None:
    expected = os.environ.get("SKUNKY_SERVICE_TOKEN", "")
    if not expected or token is None or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Service authentication required")


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=100)
    limit: int = Field(default=10, ge=1, le=50)
    collection_only: bool = False


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok", "service": "search"}


@app.post("/v1/search", dependencies=[Depends(authorize)])
def search(body: SearchRequest) -> dict:
    path = Path(os.environ.get("SKUNKY_SOURCE_REGISTRY_PATH") or REGISTRY)
    try:
        sources = json.loads(path.read_text(encoding="utf-8"))["sources"]
        if not isinstance(sources, list) or any(not isinstance(source, dict) for source in sources):
            raise ValueError("Invalid sources list")
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(503, "Source registry is unavailable") from exc

    query = body.query.casefold().strip()
    matches = []
    for source in sources:
        if source.get("enabled") is not True:
            continue
        tags = source.get("tags", [])
        fields = [str(source.get(key, "")).casefold() for key in ("id", "label", "url")]
        if isinstance(tags, list):
            fields.append(" ".join(map(str, tags)).casefold())
        if body.collection_only:
            if source.get("mode") != "web-collection" or source.get("outreach_allowed") is not False:
                continue
            matched = bool(query) and all(any(term in field for field in fields) for term in query.split())
        else:
            matched = any(query in field for field in fields)
        if matched:
            matches.append(source)
        if len(matches) == body.limit:
            break
    return {"sources": matches, "total": len(matches), "registry_version": 1}

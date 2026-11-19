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


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok", "service": "search"}


@app.post("/v1/search", dependencies=[Depends(authorize)])
def search(body: SearchRequest) -> dict:
    sources = json.loads(REGISTRY.read_text(encoding="utf-8"))["sources"]
    query = body.query.casefold().strip()
    matches = [
        s for s in sources
        if s.get("enabled", False)
        and any(query in str(v).casefold() for v in (
            s["id"], s["label"], " ".join(s.get("tags", [])), s["url"]
        ))
    ][:body.limit]
    return {"sources": matches, "total": len(matches), "registry_version": 1}

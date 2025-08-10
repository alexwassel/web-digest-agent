
import os
import httpx
from datetime import datetime
from typing import List, Dict, Any

class Searcher:
    def __init__(self, recency_days: int = 30, safety_mode: bool = True):
        self.recency_days = recency_days
        self.safety_mode = safety_mode
        self.session = httpx.Client(timeout=20.0)
        self.brave_key = os.getenv("BRAVE_API_KEY")
        self.base = "https://api.search.brave.com/res/v1/web/search"

    def _headers(self):
        return {"Accept": "application/json", "X-Subscription-Token": self.brave_key}

    def search_round(self, query: str, round_index: int = 1) -> List[Dict[str, Any]]:
        if not self.brave_key:
            raise RuntimeError("BRAVE_API_KEY not set. Enable Demo Mode or provide an API key.")
        q = f"{query} newer_than:{self.recency_days}d"
        params = {"q": q, "count": 20, "safesearch": "moderate"}
        r = self.session.get(self.base, params=params, headers=self._headers())
        r.raise_for_status()
        data = r.json()
        items = data.get("web", {}).get("results", [])
        out = []
        for it in items:
            published = None
            age = it.get("age") or {}
            if "published" in age:
                published = age["published"]
            elif it.get("meta_url", {}).get("lastmod"):
                published = it["meta_url"]["lastmod"]
            iso = None
            if isinstance(published, (int, float)):
                try:
                    iso = datetime.utcfromtimestamp(published).isoformat()
                except Exception:
                    iso = None
            elif isinstance(published, str):
                iso = published
            out.append({
                "title": it.get("title"),
                "url": it.get("url"),
                "snippet": it.get("description"),
                "published_at": iso,
                "source": it.get("meta_url", {}).get("hostname")
            })
        return out

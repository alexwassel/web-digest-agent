
from typing import List, Dict, Any
import httpx

def fetch_text(url: str) -> str:
    try:
        r = httpx.get(url, timeout=20.0)
        r.raise_for_status()
        return r.text[:20000]
    except Exception:
        return ""

def summarize_sources(results: List[Dict[str, Any]], model, prompt_template: str) -> List[Dict[str, Any]]:
    out = []
    for r in results:
        url = r.get("url","")
        html = fetch_text(url) if url else ""
        content = html[:5000]
        prompt = prompt_template.replace("{content}", content)
        j = model.complete_json(prompt, schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "url": {"type": "string"},
                "published_at": {"type": "string"},
                "summary": {"type": "string"},
                "insights": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["summary"]
        })
        j.setdefault("title", r.get("title"))
        j.setdefault("url", r.get("url"))
        j.setdefault("published_at", r.get("published_at"))
        out.append(j)
    return out

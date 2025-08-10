
from datetime import datetime
from typing import List, Dict, Any

def dedupe_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for it in items:
        key = (str(it.get('title','')).strip().lower(), str(it.get('url','')).split('#')[0])
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out

def score_item(it: Dict[str, Any]) -> float:
    freshness = 0.2
    try:
        dt = datetime.fromisoformat(str(it.get('published_at')).replace("Z",""))
        age_days = max((datetime.utcnow() - dt).days, 0)
        freshness = max(0.0, 1.0 - age_days / 90.0)
    except Exception:
        pass
    insights = it.get('insights', []) or []
    density = min(len(insights) / 5.0, 1.0)
    host_bonus = 0.1 if str(it.get('url','')).startswith('https') else 0.0
    return 0.6 * freshness + 0.3 * density + 0.1 * host_bonus

def rank_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(items, key=score_item, reverse=True)

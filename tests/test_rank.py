
from agent.rank import dedupe_results, rank_results

def test_dedupe_by_title_and_url():
    items = [
        {"title": "A", "url": "https://x.test/a", "insights": ["i1", "i2"]},
        {"title": "A", "url": "https://x.test/a#section", "insights": ["i1"]},
        {"title": "B", "url": "https://x.test/b", "insights": []},
        {"title": "C", "url": "https://x.test/c", "insights": ["i1", "i2", "i3", "i4", "i5"]},
    ]
    out = dedupe_results(items)
    assert len(out) == 3
    urls = {it["url"].split("#")[0] for it in out}
    assert urls == {"https://x.test/a", "https://x.test/b", "https://x.test/c"}

def test_rank_prefers_more_insights_when_freshness_equal():
    items = [
        {"title": "A", "url": "https://x.test/a", "insights": ["i1", "i2"]},
        {"title": "B", "url": "https://x.test/b", "insights": []},
        {"title": "C", "url": "https://x.test/c", "insights": ["i1", "i2", "i3", "i4", "i5"]},
    ]
    ranked = rank_results(items)
    titles = [it["title"] for it in ranked]
    assert titles[0] == "C"
    assert titles[-1] == "B"


import os
import json
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

from agent.search import Searcher
from agent.rank import rank_results, dedupe_results
from agent.summarize import summarize_sources
from agent.digest import synthesize_digest, export_markdown_to_pdf
from agent.security import sanitize_topic
from models import get_model_client

CONFIG_PATH = Path(__file__).parent / 'config.yaml'
SAMPLES_DIR = Path(__file__).parent / 'samples'
PROMPTS_DIR = Path(__file__).parent / 'prompts'

st.set_page_config(page_title="WebDigest Agent", page_icon="🧭", layout="wide")
st.title("WebDigest Agent 🧭")
st.caption("Iterative web search → one‑page digest. Demo mode works offline.")

with st.sidebar:
    st.header("Settings")
    topic = st.text_input("Topic", placeholder="e.g., vector databases, LLM evals, NVDA earnings")

    recency = st.select_slider(
        "Recency window",
        options=[7, 14, 30, 60, 90],
        value=30,
        help="Only include sources published within the last N days."
    )

    max_sources = st.slider("Max sources", min_value=5, max_value=30, value=12, step=1)
    rounds = st.slider("Search rounds", min_value=1, max_value=3, value=2)
    demo_mode = st.toggle("Demo Mode (no APIs)", value=False,
                          help="Use bundled sample results and a canned digest. No API keys required.")

    provider = st.selectbox("Model provider", options=["openai", "anthropic"], index=0)
    model_name = st.text_input("Model name", value="gpt-4o-mini" if provider=="openai" else "claude-3-haiku-20240307")

    safety_mode = st.toggle("Safety mode", value=True,
                            help="Apply stricter domain filters and aggressive prompt‑injection defenses.")

    export_pdf = st.toggle("Also export PDF", value=True)

    run_btn = st.button("Run WebDigest", type="primary")

placeholder_status = st.empty()
cols = st.columns([2, 1])

def _load_file(path: Path) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

if run_btn:
    if not topic and not demo_mode:
        st.error("Please enter a topic or enable Demo Mode.")
        st.stop()

    safe_topic = sanitize_topic(topic) if topic else "demo"

    if demo_mode:
        searcher = None
        model = None
    else:
        try:
            model = get_model_client(provider, model_name)
            searcher = Searcher(recency_days=recency, safety_mode=safety_mode)
        except Exception as e:
            st.error(f"Failed to initialize providers: {e}")
            st.stop()

    with st.spinner("Collecting sources..."):
        if demo_mode:
            demo_json = json.loads(_load_file(SAMPLES_DIR / 'demo_topic.json'))
            results = demo_json["results"]
        else:
            r1 = searcher.search_round(safe_topic, round_index=1)
            placeholder_status.info(f"Round 1 fetched {len(r1)} results")

            seed_texts = [f"{x['title']} — {x['snippet']}" for x in r1[:8]]
            refine_prompt = _load_file(PROMPTS_DIR / 'refine_query.md')
            refine_input = refine_prompt.format(topic=safe_topic, bullets="\n".join(f"- {s}" for s in seed_texts))
            refined = model.complete_json(refine_input, schema={
                "type": "object",
                "properties": {
                    "queries": {"type": "array", "items": {"type": "string"}},
                    "entities": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["queries"]
            })
            queries = refined.get("queries", [])[:5]
            r_more = []
            for i, q in enumerate(queries, start=2):
                r_more.extend(searcher.search_round(q, round_index=i))
            results = r1 + r_more

        results = dedupe_results(results)
        results = [r for r in results if r.get('published_at')]
        cutoff = datetime.utcnow() - timedelta(days=recency)
        kept = []
        for r in results:
            try:
                dt = datetime.fromisoformat(str(r['published_at']).replace("Z",""))
                if dt >= cutoff:
                    kept.append(r)
            except Exception:
                continue
        results = kept[:max_sources]

    if not results:
        st.warning("No recent results found for this topic and window.")
        st.stop()

    with st.spinner("Summarizing sources..."):
        if demo_mode:
            summaries = [
                {
                    "url": r["url"],
                    "title": r["title"],
                    "published_at": r["published_at"],
                    "summary": r["snippet"],
                    "insights": ["Demo insight 1", "Demo insight 2"],
                    "word_count": 80
                } for r in results
            ]
        else:
            summarize_prompt = _load_file(PROMPTS_DIR / 'summarize_source.md')
            summaries = summarize_sources(results, model, summarize_prompt)

    ranked = rank_results(summaries)

    with st.spinner("Synthesizing one‑page digest..."):
        if demo_mode:
            digest_md = _load_file(SAMPLES_DIR / 'demo_digest.md')
        else:
            synth_prompt = _load_file(PROMPTS_DIR / 'synthesize_digest.md')
            digest_md = synthesize_digest(
                topic=safe_topic,
                items=ranked,
                model=model,
                prompt_template=synth_prompt
            )

    with cols[0]:
        st.subheader("One‑page Digest")
        st.markdown(digest_md)

    with cols[1]:
        st.subheader("Cited Sources")
        for s in ranked:
            pub = s.get('published_at', '')
            st.write(f"[{s.get('title','(untitled)')}]({s.get('url','#')}) — {pub}")

    st.download_button("Download .md", data=digest_md.encode('utf-8'), file_name=f"webdigest_{safe_topic}.md")

    if export_pdf:
        try:
            pdf_bytes = export_markdown_to_pdf(digest_md)
            st.download_button("Download .pdf", data=pdf_bytes, file_name=f"webdigest_{safe_topic}.pdf")
        except Exception as e:
            st.warning(f"PDF export unavailable: {e}")

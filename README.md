
[![Python Tests](https://github.com/alexwassel/web-digest-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/alexwassel/web-digest-agent/actions/workflows/ci.yml)

# WebDigest Agent

An AI agent that performs iterative web search and generates a one‑page digest. Includes an **offline Demo Mode** so you can run it locally without API keys.

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill in API keys, or enable Demo Mode in the UI
streamlit run app.py
```

## Demo Mode
When enabled, the app:
Skips all API calls (no OpenAI, Anthropic, or Brave Search usage).
Generates on-topic fake search results and a sample digest based on the topic you enter.
Defaults to a generic digest if no topic is provided.
Keeps the same UI flow as live mode — you can still download .md and .pdf files.


## PDF Export (no native deps)
PDF export uses ReportLab (pure Python - easier for cloning and quick testing) — no Homebrew/GTK/Pango/Cairo required.
Click “Download .pdf” after the digest is generated.

## Features
- Streamlit UI: topic, recency (7/14/30/60/90d), rounds (1–3), source cap, safety mode
- Iterative search (Round 1 broad → Round 2 refined via LLM)
- Summarization + ranking with citations (title, link, ISO date)
- Exports: Markdown (always) and PDF (WeasyPrint)
- Demo Mode: works offline using bundled samples
- Pluggable models: OpenAI and Anthropic adapters

## Environment Variables
- `OPENAI_API_KEY` – required if using OpenAI (GPT)
- `ANTHROPIC_API_KEY` – required if using Anthropic (Claude)
- `BRAVE_API_KEY` – required for live search with Brave API (or adapt searcher)

## Security Notes
- API keys and credentials are **kept local** and never stored in the repository.
- `.env` is excluded from version control via `.gitignore`.
- Demo Mode allows you to run the app without any API keys, using bundled sample data.
- Environment variables are used to manage credentials and prevent accidental exposure.
- Prompt‑injection mitigations: sanitize input, summarize don’t execute, structured output requests.
- Recency and domain filters defend against stale/low‑quality sources.

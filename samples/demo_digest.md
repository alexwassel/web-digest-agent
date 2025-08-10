
# Digest: Vector Databases (Last 30 Days)

## Top Insights
- Qdrant added PQ-based compression, cutting RAM ~4× with minor recall impact.
- Weaviate’s hybrid updates improve sparse-query relevance and reduce false negatives.
- Recent benchmarks highlight price/perf tradeoffs between hosted vs. self‑managed stacks.

## Emerging Themes
- Memory efficiency via quantization and HNSW tuning.
- Better hybrid ranking for real‑world retrieval.

## One‑Page Summary
Vector databases continue to evolve along two axes: memory efficiency and hybrid ranking quality. Qdrant’s new quantization options target RAM usage without losing much recall, while Weaviate shipped relevance gains for sparse queries by improving hybrid scoring. Benchmarks this month also surfaced the classic tradeoff: hosted services accelerate iteration but can cost more at scale, while open‑source options like Qdrant or pgvector give teams control at the expense of operational overhead.

Teams building RAG systems should benchmark recall@k on their own datasets, toggle quantization, and measure end‑to‑end latency under concurrent load. Hybrid search remains a strong default when queries mix keywords and semantics.

## Cited Sources
1. Vector DB round‑up — https://example.com/vector-roundup — 2025‑07‑15
2. Weaviate hybrid improvements — https://example.com/weaviate-hybrid — 2025‑07‑28
3. Qdrant quantization — https://example.com/qdrant-quant — 2025‑08‑02

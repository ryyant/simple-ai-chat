# Chunking

Splitting documents into smaller pieces before embedding and retrieval. Chunk quality is one of the biggest levers in a RAG pipeline — too small loses context, too large dilutes relevance and wastes tokens.

---

## Overview

| Method | Idea | Strength | Weakness |
|---|---|---|---|
| **Fixed-size** | Split every N characters/tokens | Simple, fast, predictable | Cuts mid-sentence, ignores meaning |
| **Recursive** | Split on a hierarchy of separators until chunks fit | Respects natural breaks, easy default | Still blind to semantics |
| **Document structure** | Split on headings, sections, lists, code blocks | Preserves logical units | Needs structured input (Markdown, HTML, PDFs with TOC) |
| **Semantic** | Split where embedding similarity drops | Topic-coherent chunks | Slower, needs an embedding model at index time |
| **LLM-based** | Ask an LLM to segment the document | Highest quality, handles nuance | Expensive, slow, non-deterministic |

---

## Fixed-Size Chunking

Split text into chunks of a fixed length (e.g. 500 tokens) with an optional overlap (e.g. 50 tokens) between consecutive chunks.

- **Params** — `chunk_size`, `chunk_overlap`
- **Overlap** — preserves context across boundaries; typical 10–20% of `chunk_size`
- **Use when** — prototyping, uniform corpora, tight latency budgets

```
[chunk 1 ──────────────]
              [chunk 2 ──────────────]
                            [chunk 3 ──────────────]
       └─ overlap ─┘  └─ overlap ─┘
```

> Baseline. Always works, rarely optimal.

---

## Recursive Chunking

Try a list of separators in order; if a chunk is still too large, recurse with the next separator.

Typical separator hierarchy: `["\n\n", "\n", ". ", " ", ""]` — paragraphs → lines → sentences → words → characters.

- **Params** — `chunk_size`, `chunk_overlap`, `separators`
- **Use when** — generic prose, mixed content, sensible default for most pipelines
- **Implementation** — `RecursiveCharacterTextSplitter` in LangChain

> Best general-purpose default. Fixed-size with manners.

---

## Document Structure-Based Chunking

Use the document's own structure as boundaries: Markdown headings, HTML tags, PDF sections, code functions, table rows.

- **Markdown** — split on `#`, `##`, `###`; attach heading path as metadata
- **HTML** — split on `<h1>`, `<section>`, `<article>`
- **Code** — split on functions, classes, modules (language-aware splitters)
- **PDF** — use TOC, page breaks, or layout analysis (Unstructured, LlamaParse)

- **Use when** — input has reliable structure (docs, wikis, codebases)
- **Pair with** — recursive chunking as a fallback when a section exceeds `chunk_size`

> Preserves the author's intent. Heading metadata also boosts retrieval — store it alongside the chunk.

---

## Semantic Chunking

Embed each sentence, then split where the cosine distance between consecutive sentences exceeds a threshold — i.e. where the topic shifts.

**Algorithm**
1. Split into sentences
2. Embed each sentence (often grouped in windows of 1–3 sentences for stability)
3. Compute distance between adjacent embeddings
4. Place a chunk boundary where distance crosses a threshold (absolute or percentile)

- **Params** — `breakpoint_threshold_type` (`percentile`, `standard_deviation`, `interquartile`), `buffer_size`
- **Use when** — topic-diverse documents (long articles, transcripts, research papers)
- **Cost** — extra embedding pass at index time; no extra cost at query time

> Chunks align with meaning, not character counts. Worth it when retrieval precision matters.

---

## LLM-Based Chunking

Send the document to an LLM and ask it to return chunk boundaries (or the chunks themselves), optionally with summaries, titles, or propositions.

**Variants**
- **Boundary detection** — LLM returns positions where the document should split
- **Propositional chunking** — LLM rewrites the document as standalone factual statements; each becomes a chunk
- **Agentic chunking** — LLM groups propositions into coherent topics

- **Use when** — high-value corpora, small document count, quality > cost
- **Cost** — most expensive option; cache aggressively, run offline

> Highest quality, lowest throughput. Reserve for the corpora that justify it.

---

## Choosing a Method

```
Structured input (Markdown, HTML, code)?  → Document structure
Generic prose, need a default?            → Recursive
Topic-diverse, retrieval precision key?   → Semantic
Small corpus, quality is critical?        → LLM-based
Prototyping or uniform short docs?        → Fixed-size
```

**Tunable knobs** — chunk size (typical 256–1024 tokens), overlap (10–20%), embedding model, metadata attached to each chunk (source, heading path, page number).

**Evaluate empirically** — build a small eval set of (query, expected chunk) pairs and measure recall@K across strategies. The right method is corpus-specific.

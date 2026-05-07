# LLM Reference Notes

---

## Prompt Structure

```
[ROLE]        You are a ___
[CONTEXT]     The situation / background is ___
[TASK]        Your job is to ___
[STEPS]       1. ___  2. ___                     (optional — for multi-step tasks)
[CONSTRAINTS] Do not ___ / Keep it ___ / Use ___ tone
[INFORMATION] Dynamic / retrieved content        (optional — dynamic prompting)
[EXAMPLES]    Input → Output                     (optional — few-shot samples)
[FORMAT]      Respond as a ___ / Structure it like ___
[REPEAT]      Repeat critical instructions (optional - more useful for long prompts)
```

For quick one-off prompts, **ROLE + CONTEXT + TASK + FORMAT** is usually enough.  
For system prompts, use all sections and separate them with XML tags (`<instructions>`, `<examples>`, `<format>`) or markdown headers.

---

## Anthropic vs OpenAI API

| Feature | Anthropic | OpenAI |
|---|---|---|
| **Create** | `client.messages.create()` | `client.responses.create()` (new) / `client.chat.completions.create()` (legacy) |
| **Streaming** | `client.messages.stream()` | `client.responses.create(stream=True)` |
| **Batching** | `client.messages.batches.create()` — requests inline | `client.batches.create()` — `.jsonl` file upload; works with both `/v1/responses` and `/v1/chat/completions` |
| **Structured output** | No native support — force via `tool_choice` | Native: `.parse(text_format=MyModel)` on Responses API or `.parse(response_format=MyModel)` on legacy |

---

## Guardrails

A safety layer that constrains, monitors, or redirects model behaviour to keep outputs safe, accurate, and aligned.

**Input**
- Topic restrictions
- Content classification
- Prompt injection detection

**Output**
- Hallucination checks
- Format validation
- Toxicity filtering
- Citation grounding
- Length limits

**Implementation approaches**
- Rule-based filters
- Model-as-judge
- Embedding similarity
- Structured output enforcement
- External tools (NeMo, LlamaGuard)

> Trade-off: every filter adds latency and cost. The goal is **calibration**, not maximum restriction.

---

## Token Optimisation (Claude Code)

**Context management** *(biggest impact)*
- `/clear` between unrelated tasks
- `/rename` before clearing so you can find the session later; `/resume` to return
- `/compact` proactively as a checkpoint — tell Claude explicitly what to preserve
- Don't wait for auto-compaction

**CLAUDE.md**
- Keep under ~2 000 tokens
- Put detailed content in separate files and reference them by path — Claude only reads them when relevant

**Model switching**
- Use stronger models only when necessary; switch with `/model sonnet`
- Disable unused MCP servers — each tool description consumes context window tokens (configure in `.claude/settings.json`)

**Other**
- Limit extended thinking — it's a large cost driver
- `/cost` to check current usage, or configure the status line to display it continuously

---

## RAG (Retrieval-Augmented Generation)

Gives the model access to external knowledge at inference time.

**Pipeline**

| Phase | When | What happens |
|---|---|---|
| **Indexing** | Once, offline | Raw docs → chunking → embedding → stored in vector store |
| **Retrieval** | Per query, online | Query embedded → similarity search → top-K chunks returned |
| **Generation** | Per query, online | Top-K chunks + query → grounded response |

**Embeddings**
- **Generate** — use pre-trained models (BERT, SentenceTransformers) to convert text into fixed-size vectors; do the same for the query
- **Store** — vector DB (FAISS, Pinecone, Weaviate, Milvus) for fast similarity search
- **Compute** — cosine similarity (most popular for semantic search) or Euclidean distance
- **Retrieve** — rank by similarity score, return top-K results with metadata (doc ID, text, etc.)

**Optimisations**
- Use Approximate Nearest Neighbours (ANN) for large datasets
- Pre-normalise vectors for cosine similarity to speed up computation

---

## Claude Code Concepts

| Concept | What it is | When to use |
|---|---|---|
| **Skills** | Markdown files with procedural instructions — define how Claude handles specific tasks | Encode team workflows or coding standards |
| **Agents** | Autonomous workers Claude spawns for complex, multi-step tasks; run in parallel in isolated contexts | Parallel or long-running tasks |
| **MCP** | Interface connecting Claude to external tools, DBs, or APIs (GitHub, Jira, SQL) | Read/write to external services |
| **Plugins** | Bundle of agents + skills + MCP configs as a single installable package | Share a customised setup across a team or repo |

---

## Typical Enhancements Checklist

- [ ] Function calling / tool use
- [ ] Prompt caching
- [ ] Guardrails
- [ ] Fine-tuning
- [ ] Orchestration / multi-agent
- [ ] Evaluations
- [ ] Token & cost optimisation
- [ ] Dynamic model switching
- [ ] Monitoring & feedback loop

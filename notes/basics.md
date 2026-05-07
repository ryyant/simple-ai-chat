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

## Prompt Caching

Cache stable parts of your prompt to cut latency and cost on repeated calls.

| | Anthropic | OpenAI |
|---|---|---|
| **How** | Mark with `cache_control: {"type": "ephemeral"}` on a content block | Automatic — no markup needed |
| **Min size** | 1024 tokens | 1024 tokens |
| **TTL** | 5 minutes | ~5 minutes |
| **Cost** | Write: +25% / Read: −90% vs base input | Read: −50% vs base input |

**What to cache** — system prompts, tool definitions, large documents, few-shot examples.  
**Key rule** — cached content must be a stable prefix; anything after the breakpoint is not cached.

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

## Agents & Multi-Agent Systems

An **agent** is an LLM in a loop — perceive → plan → act (tool call) → observe → repeat.

**Core:** LLM, tools, memory (context window + optional external store), system prompt.

**Workflow patterns** (Anthropic, *Building effective agents*)
- **Prompt chaining** — sequential steps; output of one feeds the next
- **Routing** — classify input, dispatch to a specialised handler
- **Parallelisation** — independent subtasks concurrently. *Sectioning* (split a task) or *voting* (redundancy for accuracy)
- **Orchestrator–workers** — lead LLM decomposes at runtime, delegates to workers
- **Evaluator–optimiser** — one LLM produces, another critiques in a loop

> Workflows are deterministic orchestration. *Agents* are workflows where the LLM chooses its own path.

---

### Approaches to parallel work

| Approach | Mechanism | When to use |
|---|---|---|
| **Single session** | One Claude, one context | Most tasks |
| **Worktrees / parallel terminals** | Separate repo checkouts, separate sessions, zero awareness | Independent features that don't touch the same code |
| **Subagents** | Lead spawns workers via the `Agent` tool (formerly `Task`); workers report back, can't talk to each other | Parallelisable subtasks with no inter-dependency |
| **Agent Teams** | Agents with own contexts but a *shared* task list / state; they observe each other and adapt | Coordinating work: shared files, dependent changes, cross-cutting refactors |

```
Subagents — one-way, report back
Lead ─┬─ A → reports back
      ├─ B → reports back
      └─ C → reports back

Agent Teams — peer-aware, shared state
Lead ─┬─ A ──┐
      ├─ B ──┼── shared task list / state
      └─ C ──┘
```

Agent Teams aren't a built-in Claude Code primitive — realised via shared file, external task tracker, or frameworks (CrewAI, AutoGen, Cline-style team modes).

---

**When to dispatch a subagent**
- **Single** — one well-scoped task that doesn't need the parent's full context, or produces noisy output (search results, file dumps)
- **Sequential** — ordered steps; pass a *summary* of the prior step into the next brief, not the raw transcript. Verify each handoff — quality compounds
- **Parallel** — 2+ truly independent tasks. Don't use for related failures or cross-cutting changes (renaming an API across files — that's an Agent Team)

**Dispatching in parallel**
1. Confirm independence — would changing one alter the others?
2. Write one self-contained prompt per subagent (paths, constraints, output format, length cap)
3. Send all `Agent` calls in a *single* assistant turn — separate turns run sequentially
4. On return: read each summary, spot-check edits, run tests, check for conflicts on shared files

**Briefing a subagent** (starts cold, prompt must be self-contained)
- Goal, file paths, what's been ruled out
- Scope ("review `providers/`" not "the codebase")
- Constraints ("don't change production code", "under 400 words")
- Structured return ("numbered findings: `file:line` — issue — fix")
- Whether to write code or just research — it can't infer

**Common mistakes:** too broad (subagent gets lost) · no context (doesn't know where to look) · no constraints (refactors more than asked) · vague output spec (can't tell what changed) · trusting summaries blindly.

---

## Claude Code Concepts

| Concept | What it is | When to use |
|---|---|---|
| **Skills** | Markdown files with procedural instructions — define how Claude handles specific tasks | Encode team workflows or coding standards |
| **Agents** | Autonomous workers Claude spawns for complex, multi-step tasks; run in parallel in isolated contexts | Parallel or long-running tasks |
| **MCP** | Interface connecting Claude to external tools, DBs, or APIs (GitHub, Jira, SQL) | Read/write to external services |
| **Plugins** | Bundle of agents + skills + MCP configs as a single installable package | Share a customised setup across a team or repo |
| **Hooks** | Shell commands that fire automatically on Claude Code events | Automate side-effects like formatting, linting, or notifications |

### Hooks

Configured in `.claude/settings.json` (project) or `~/.claude/settings.json` (global). Events: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`.

Common uses: auto-format/lint after edits, run tests, log tool calls, send notifications on task completion.

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

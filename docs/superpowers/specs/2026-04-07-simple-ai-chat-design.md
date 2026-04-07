# Simple AI Chat — Design Spec

**Date:** 2026-04-07
**Status:** Approved

## Overview

A command-line Python chat program that uses the Google Gemini API (free tier) for multi-turn conversation. The user interacts via a terminal REPL; the program maintains full conversation history within a session.

## Architecture

Two files:

- **`chat.py`** — `ChatSession` class wrapping the Gemini client. Owns conversation history and API interaction.
- **`main.py`** — Thin REPL loop. Owns user I/O and session lifecycle.

## Components

### `ChatSession` (`chat.py`)

- Constructed with config read from environment variables via `python-dotenv`
- Holds history as `list[{"role": "user"|"model", "content": str}]`
- Exposes one public method: `send(message: str) -> str`
  - Appends user message to history
  - Calls Gemini API with full history and system prompt
  - Appends model reply to history
  - Returns reply string
- API errors are caught and re-raised as `RuntimeError` with a human-readable message

### `main.py`

- Loads `.env` at startup
- Instantiates `ChatSession`
- Loops: reads input → calls `session.send()` → prints reply
- Exits cleanly on `KeyboardInterrupt` (Ctrl+C) or `EOFError` (Ctrl+D)
- Catches `RuntimeError` from `ChatSession`, prints error, continues loop

## Configuration (`.env`)

```
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash        # optional, this is the default
SYSTEM_PROMPT=You are a helpful assistant.  # optional, this is the default
```

## Data Flow

1. User types message → `main.py` calls `session.send(message)`
2. `ChatSession` appends `{"role": "user", "content": message}` to history
3. Full history + system prompt sent to Gemini API
4. Response appended as `{"role": "model", "content": reply}`
5. Reply returned to `main.py` and printed

## Testing

- `tests/test_chat.py` — unit tests for `ChatSession`, patching `google.generativeai` so no real API calls are made
- Test cases:
  - `send()` appends user message and model reply to history
  - `send()` passes full history on subsequent calls
  - API errors are re-raised as `RuntimeError`
- `main.py` is not unit tested (pure I/O glue)

## Dependencies

- `google-generativeai` — Gemini SDK
- `python-dotenv` — `.env` loading
- `pytest` — testing

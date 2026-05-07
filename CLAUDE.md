# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A command-line AI chat program written in Python, supporting multiple LLM providers (Google Gemini, OpenAI, Anthropic) with runtime model switching.

## Setup & Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the chat program
python main.py

# Run tests
python -m pytest

# Run a single test
python -m pytest tests/test_foo.py::test_bar
```

## Architecture

- `main.py` — entry point; loads `.env`, instantiates `ChatSession`, runs the REPL loop; exposes `handle_input(user_input, session, system_prompt, api_keys) -> HandleResult` for testability
- `chat.py` — `ChatSession` class: thin wrapper over a provider, exposes `send(message) -> str`, `history`, `current_provider`, `current_model`
- `providers/base.py` — `BaseProvider` ABC with abstract `send(message) -> str` and `history: list[dict]`
- `providers/gemini.py` — `GeminiProvider`: uses `google-genai` stateful chat object
- `providers/openai.py` — `OpenAIProvider`: uses `openai` SDK, builds full message array per request
- `providers/anthropic.py` — `AnthropicProvider`: uses `anthropic` SDK, `system` is a top-level kwarg, `max_tokens=8192`
- `providers/__init__.py` — `create_provider(provider, api_key, model, system_prompt) -> BaseProvider` factory with deferred imports
- `requirements.txt` — Python dependencies

## Key Conventions

- API keys are stored in a `.env` file (see `.env.example`) and loaded via `python-dotenv` in `main.py`; never hardcoded
- Conversation history is kept as `list[{"role": "user"|"assistant", "content": str}]` on each provider and surfaced via `ChatSession.history`
- `ChatSession.__init__` takes `provider`, `api_key`, `model`, and `system_prompt` — env var loading happens in `main.py`, not inside the class
- `create_provider` uses deferred imports so a missing SDK for one provider doesn't break the others
- Switching models via `/model <provider>/<model>` in the REPL creates a fresh `ChatSession` (history cleared)

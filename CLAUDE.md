# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A simple command-line AI chat program written in Python, using free LLM APIs (e.g., Google Gemini, Groq, Cohere, or Mistral — all offer free tiers).

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

- `main.py` — entry point; loads `.env`, instantiates `ChatSession`, runs the REPL loop
- `chat.py` — `ChatSession` class: wraps Gemini client, owns conversation history, exposes `send(message) -> str`
- `requirements.txt` — Python dependencies

## Key Conventions

- API keys are stored in a `.env` file (see `.env.example`) and loaded via `python-dotenv` in `main.py`; never hardcoded
- Conversation history is kept as `list[{"role": "user"|"model", "content": str}]` on `ChatSession` and passed with every API request
- `ChatSession.__init__` takes `api_key`, `model`, and `system_prompt` — env var loading happens in `main.py`, not inside the class

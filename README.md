# llm-chatbots

A simple command-line AI chat program in Python, using the Google Gemini API (free tier).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your API key:
   ```bash
   cp .env.example .env
   ```

   ```
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   SYSTEM_PROMPT=You are a helpful assistant.
   ```

   Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

## Usage

```bash
python main.py
```

Type your message and press Enter. Use `Ctrl+C` or `Ctrl+D` to quit.

## Running Tests

```bash
python -m pytest
```

## Project Structure

- `main.py` — entry point; loads `.env`, starts the chat REPL
- `chat.py` — `ChatSession` class; manages conversation history and Gemini API calls

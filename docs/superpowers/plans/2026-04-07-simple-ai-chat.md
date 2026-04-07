# Simple AI Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a terminal-based multi-turn chat program backed by the Google Gemini free API.

**Architecture:** `chat.py` contains a `ChatSession` class that wraps the Gemini client, manages conversation history, and exposes a single `send()` method. `main.py` is a thin REPL that owns I/O and delegates everything else to `ChatSession`.

**Tech Stack:** Python 3.10+, `google-generativeai`, `python-dotenv`, `pytest`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `requirements.txt` | Create | Pin all dependencies |
| `.env.example` | Create | Document required/optional env vars |
| `chat.py` | Create | `ChatSession` class — Gemini client, history, `send()` |
| `main.py` | Create | REPL loop, I/O, error display |
| `tests/__init__.py` | Create | Make tests a package |
| `tests/test_chat.py` | Create | Unit tests for `ChatSession` |

---

### Task 1: Project scaffold — dependencies and env template

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`

- [ ] **Step 1: Create `requirements.txt`**

```text
google-generativeai>=0.7.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create `.env.example`**

```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
SYSTEM_PROMPT=You are a helpful assistant.
```

- [ ] **Step 3: Install dependencies**

Run:
```bash
pip install -r requirements.txt
```
Expected: All packages install without errors.

- [ ] **Step 4: Create tests package**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git init
git add requirements.txt .env.example tests/__init__.py
git commit -m "chore: project scaffold with dependencies and env template"
```

---

### Task 2: `ChatSession` — history management (no API)

**Files:**
- Create: `chat.py`
- Create: `tests/test_chat.py`

- [ ] **Step 1: Write failing test — history is empty on init**

Create `tests/test_chat.py`:

```python
from unittest.mock import MagicMock, patch
import pytest


@patch("chat.genai")
def test_initial_history_is_empty(mock_genai):
    mock_genai.GenerativeModel.return_value = MagicMock()
    from chat import ChatSession
    session = ChatSession(api_key="test-key", model="gemini-1.5-flash", system_prompt="You are helpful.")
    assert session.history == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_chat.py::test_initial_history_is_empty -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'chat'`

- [ ] **Step 3: Create minimal `chat.py` to make test pass**

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv


class ChatSession:
    def __init__(self, api_key: str, model: str, system_prompt: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
        )
        self.history: list[dict] = []
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_chat.py::test_initial_history_is_empty -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add chat.py tests/test_chat.py
git commit -m "feat: ChatSession scaffold with empty history"
```

---

### Task 3: `ChatSession.send()` — appends to history and returns reply

**Files:**
- Modify: `chat.py`
- Modify: `tests/test_chat.py`

- [ ] **Step 1: Write failing tests — send() appends to history**

Append to `tests/test_chat.py`:

```python
@patch("chat.genai")
def test_send_appends_user_and_model_messages(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "Hello back!"
    mock_genai.GenerativeModel.return_value.start_chat.return_value = mock_chat

    from importlib import reload
    import chat as chat_module
    reload(chat_module)
    from chat import ChatSession

    session = ChatSession(api_key="test-key", model="gemini-1.5-flash", system_prompt="You are helpful.")
    reply = session.send("Hello!")

    assert reply == "Hello back!"
    assert session.history == [
        {"role": "user", "content": "Hello!"},
        {"role": "model", "content": "Hello back!"},
    ]


@patch("chat.genai")
def test_send_passes_full_history_on_subsequent_calls(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = [
        MagicMock(text="First reply"),
        MagicMock(text="Second reply"),
    ]
    mock_genai.GenerativeModel.return_value.start_chat.return_value = mock_chat

    from importlib import reload
    import chat as chat_module
    reload(chat_module)
    from chat import ChatSession

    session = ChatSession(api_key="test-key", model="gemini-1.5-flash", system_prompt="You are helpful.")
    session.send("First message")
    session.send("Second message")

    # start_chat is called once; send_message is called twice on the same chat object
    assert mock_chat.send_message.call_count == 2
    first_call_arg = mock_chat.send_message.call_args_list[0][0][0]
    second_call_arg = mock_chat.send_message.call_args_list[1][0][0]
    assert first_call_arg == "First message"
    assert second_call_arg == "Second message"
    assert len(session.history) == 4
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_chat.py -v
```
Expected: 2 new tests FAIL with `AttributeError: 'ChatSession' object has no attribute 'send'`

- [ ] **Step 3: Implement `send()` in `chat.py`**

Replace `chat.py` with:

```python
import google.generativeai as genai
from dotenv import load_dotenv


class ChatSession:
    def __init__(self, api_key: str, model: str, system_prompt: str):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
        )
        self._chat = self._model.start_chat(history=[])
        self.history: list[dict] = []

    def send(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        response = self._chat.send_message(message)
        reply = response.text
        self.history.append({"role": "model", "content": reply})
        return reply
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
pytest tests/test_chat.py -v
```
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add chat.py tests/test_chat.py
git commit -m "feat: implement ChatSession.send() with history tracking"
```

---

### Task 4: `ChatSession.send()` — API error handling

**Files:**
- Modify: `chat.py`
- Modify: `tests/test_chat.py`

- [ ] **Step 1: Write failing test — API errors become RuntimeError**

Append to `tests/test_chat.py`:

```python
@patch("chat.genai")
def test_send_raises_runtime_error_on_api_failure(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = Exception("API quota exceeded")
    mock_genai.GenerativeModel.return_value.start_chat.return_value = mock_chat

    from importlib import reload
    import chat as chat_module
    reload(chat_module)
    from chat import ChatSession

    session = ChatSession(api_key="test-key", model="gemini-1.5-flash", system_prompt="You are helpful.")

    with pytest.raises(RuntimeError, match="API quota exceeded"):
        session.send("Hello!")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_chat.py::test_send_raises_runtime_error_on_api_failure -v
```
Expected: FAIL — `Exception` is raised, not `RuntimeError`

- [ ] **Step 3: Add error handling to `send()` in `chat.py`**

Replace the `send` method:

```python
    def send(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        try:
            response = self._chat.send_message(message)
        except Exception as e:
            self.history.pop()  # remove the unsent user message
            raise RuntimeError(str(e)) from e
        reply = response.text
        self.history.append({"role": "model", "content": reply})
        return reply
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
pytest tests/test_chat.py -v
```
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add chat.py tests/test_chat.py
git commit -m "feat: wrap API errors as RuntimeError in ChatSession.send()"
```

---

### Task 5: `main.py` — REPL loop

**Files:**
- Create: `main.py`

- [ ] **Step 1: Create `main.py`**

```python
import os
from dotenv import load_dotenv
from chat import ChatSession


def main():
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set. Add it to your .env file.")
        return

    model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    system_prompt = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")

    session = ChatSession(api_key=api_key, model=model, system_prompt=system_prompt)

    print(f"Chat started (model: {model}). Type your message and press Enter. Ctrl+C or Ctrl+D to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        try:
            reply = session.send(user_input)
        except RuntimeError as e:
            print(f"Error: {e}")
            continue

        print(f"AI: {reply}\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke test manually**

Copy `.env.example` to `.env` and fill in your real `GEMINI_API_KEY`, then run:

```bash
python main.py
```
Expected: Prompt appears, you can type a message, AI replies, history is maintained across turns, Ctrl+C exits cleanly.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add REPL loop in main.py"
```

---

### Task 6: Final cleanup — add `.gitignore`

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore`**

```text
.env
__pycache__/
*.pyc
.pytest_cache/
```

- [ ] **Step 2: Run full test suite one last time**

```bash
pytest -v
```
Expected: All 4 tests PASS

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```

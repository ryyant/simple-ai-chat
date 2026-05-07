from unittest.mock import MagicMock, patch
import pytest


class FakeSession:
    def __init__(self, provider, model, history=None):
        self.current_provider = provider
        self.current_model = model
        self.history = history or []

    def send(self, message):
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": "test reply"})
        return "test reply"


def test_handle_input_model_no_args_shows_current():
    from main import handle_input
    session = FakeSession("gemini", "gemini-2.5-flash")
    result = handle_input("/model", session, system_prompt=".", api_keys={})
    assert "gemini/gemini-2.5-flash" in result.output
    assert result.new_session is None


def test_handle_input_model_switch_returns_new_session():
    from main import handle_input
    with patch("main.ChatSession") as MockSession:
        new_session = FakeSession("openai", "gpt-4o")
        MockSession.return_value = new_session
        session = FakeSession("gemini", "gemini-2.5-flash")
        result = handle_input(
            "/model openai/gpt-4o",
            session,
            system_prompt=".",
            api_keys={"openai": "sk-test"},
        )
    assert result.new_session is not None
    assert result.new_session.current_provider == "openai"
    assert result.new_session.current_model == "gpt-4o"


def test_handle_input_model_switch_clears_history():
    from main import handle_input
    with patch("main.ChatSession") as MockSession:
        MockSession.return_value = FakeSession("anthropic", "claude-opus-4-7")
        session = FakeSession("gemini", "gemini-2.5-flash", history=[{"role": "user", "content": "old"}])
        result = handle_input(
            "/model anthropic/claude-opus-4-7",
            session,
            system_prompt=".",
            api_keys={"anthropic": "ant-test"},
        )
    assert result.new_session.history == []


def test_handle_input_model_unknown_provider_returns_error():
    from main import handle_input
    session = FakeSession("gemini", "gemini-2.5-flash")
    result = handle_input("/model bogus/some-model", session, system_prompt=".", api_keys={})
    assert "Unknown provider" in result.output
    assert result.new_session is None


def test_handle_input_model_missing_api_key_returns_error():
    from main import handle_input
    session = FakeSession("gemini", "gemini-2.5-flash")
    result = handle_input("/model openai/gpt-4o", session, system_prompt=".", api_keys={})
    assert "No API key" in result.output
    assert result.new_session is None


def test_handle_input_regular_message_calls_send():
    from main import handle_input
    session = FakeSession("gemini", "gemini-2.5-flash")
    result = handle_input("Hello", session, system_prompt=".", api_keys={})
    assert result.output == "test reply"
    assert result.new_session is None


def test_handle_input_runtime_error_returned_as_output():
    from main import handle_input
    session = MagicMock()
    session.send.side_effect = RuntimeError("quota exceeded")
    result = handle_input("Hello", session, system_prompt=".", api_keys={})
    assert "quota exceeded" in result.output
    assert result.new_session is None

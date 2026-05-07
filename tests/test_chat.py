from unittest.mock import MagicMock, patch
import pytest


@patch("providers.gemini.genai")
def test_initial_history_is_empty(mock_genai):
    mock_genai.Client.return_value.chats.create.return_value = MagicMock()
    from chat import ChatSession
    session = ChatSession(provider="gemini", api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    assert session.history == []


@patch("providers.gemini.genai")
def test_send_appends_user_and_assistant_messages(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "Hello back!"
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from chat import ChatSession
    session = ChatSession(provider="gemini", api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    result = session.send("Hello!")
    assert result == "Hello back!"
    assert session.history == [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello back!"},
    ]


@patch("providers.gemini.genai")
def test_send_accumulates_history_across_calls(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = [
        MagicMock(text="First reply"),
        MagicMock(text="Second reply"),
    ]
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from chat import ChatSession
    session = ChatSession(provider="gemini", api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    session.send("First")
    session.send("Second")
    assert mock_chat.send_message.call_count == 2
    assert len(session.history) == 4


@patch("providers.gemini.genai")
def test_history_external_mutation_does_not_affect_provider(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "reply"
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from chat import ChatSession
    session = ChatSession(provider="gemini", api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    session.send("Hello")
    session.history.clear()
    session.history.append({"role": "user", "content": "injected"})
    assert len(session.history) == 2
    assert session.history[0] == {"role": "user", "content": "Hello"}
    assert session.history[1] == {"role": "assistant", "content": "reply"}


@patch("providers.gemini.genai")
def test_send_raises_runtime_error_on_api_failure(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = Exception("API quota exceeded")
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from chat import ChatSession
    session = ChatSession(provider="gemini", api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    with pytest.raises(RuntimeError, match="API quota exceeded"):
        session.send("Hello!")
    assert session.history == []

from unittest.mock import MagicMock, patch
import pytest


@patch("chat.genai")
def test_initial_history_is_empty(mock_genai):
    mock_client = MagicMock()
    mock_client.chats.create.return_value = MagicMock()
    mock_genai.Client.return_value = mock_client
    from chat import ChatSession
    session = ChatSession(api_key="test-key", model="gemini-1.5-flash", system_prompt="You are helpful.")
    assert session.history == []


@patch("chat.genai")
def test_send_appends_user_and_model_messages(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "Hello back!"
    mock_client = MagicMock()
    mock_client.chats.create.return_value = mock_chat
    mock_genai.Client.return_value = mock_client

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
    mock_client = MagicMock()
    mock_client.chats.create.return_value = mock_chat
    mock_genai.Client.return_value = mock_client

    from chat import ChatSession

    session = ChatSession(api_key="test-key", model="gemini-1.5-flash", system_prompt="You are helpful.")
    session.send("First message")
    session.send("Second message")

    # chats.create is called once; send_message is called twice on the same chat object
    assert mock_chat.send_message.call_count == 2
    first_call_arg = mock_chat.send_message.call_args_list[0][0][0]
    second_call_arg = mock_chat.send_message.call_args_list[1][0][0]
    assert first_call_arg == "First message"
    assert second_call_arg == "Second message"
    assert len(session.history) == 4


@patch("chat.genai")
def test_send_raises_runtime_error_on_api_failure(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = Exception("API quota exceeded")
    mock_client = MagicMock()
    mock_client.chats.create.return_value = mock_chat
    mock_genai.Client.return_value = mock_client

    from chat import ChatSession

    session = ChatSession(api_key="test-key", model="gemini-1.5-flash", system_prompt="You are helpful.")

    with pytest.raises(RuntimeError, match="API quota exceeded"):
        session.send("Hello!")

    assert session.history == [], "history must be empty after a failed send"

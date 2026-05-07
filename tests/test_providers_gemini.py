from unittest.mock import MagicMock, patch
import pytest


@patch("providers.gemini.genai")
def test_gemini_initial_history_is_empty(mock_genai):
    mock_genai.Client.return_value.chats.create.return_value = MagicMock()
    from providers.gemini import GeminiProvider
    p = GeminiProvider(api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    assert p.history == []


@patch("providers.gemini.genai")
def test_gemini_send_appends_user_and_assistant_messages(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "Hello back!"
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from providers.gemini import GeminiProvider
    p = GeminiProvider(api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    result = p.send("Hello!")
    assert result == "Hello back!"
    assert p.history == [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello back!"},
    ]


@patch("providers.gemini.genai")
def test_gemini_send_raises_runtime_error_on_api_failure(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = Exception("quota exceeded")
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from providers.gemini import GeminiProvider
    p = GeminiProvider(api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    with pytest.raises(RuntimeError, match="quota exceeded"):
        p.send("Hello!")
    assert p.history == []


@patch("providers.gemini.genai")
def test_gemini_send_rolls_back_history_when_response_text_raises(mock_genai):
    class BlockedResponse:
        @property
        def text(self):
            raise ValueError("no text in response")

    mock_chat = MagicMock()
    mock_chat.send_message.return_value = BlockedResponse()
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from providers.gemini import GeminiProvider
    p = GeminiProvider(api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    with pytest.raises(RuntimeError, match="no text in response"):
        p.send("Hello!")
    assert p.history == []


@patch("providers.gemini.genai")
def test_gemini_send_returns_empty_string_when_response_text_is_none(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = None
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from providers.gemini import GeminiProvider
    p = GeminiProvider(api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    result = p.send("Hello!")
    assert result == ""
    assert p.history == [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": ""},
    ]


@patch("providers.gemini.genai")
def test_gemini_send_accumulates_history_across_calls(mock_genai):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = [
        MagicMock(text="First reply"),
        MagicMock(text="Second reply"),
    ]
    mock_genai.Client.return_value.chats.create.return_value = mock_chat
    from providers.gemini import GeminiProvider
    p = GeminiProvider(api_key="key", model="gemini-2.5-flash", system_prompt="Help.")
    p.send("First")
    p.send("Second")
    assert mock_chat.send_message.call_count == 2
    assert len(p.history) == 4

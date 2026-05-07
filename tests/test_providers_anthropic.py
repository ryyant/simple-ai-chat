from unittest.mock import MagicMock, patch
import pytest


@patch("providers.anthropic.Anthropic")
def test_anthropic_initial_history_is_empty(mock_class):
    mock_class.return_value = MagicMock()
    from providers.anthropic import AnthropicProvider
    p = AnthropicProvider(api_key="key", model="claude-opus-4-7", system_prompt="Help.")
    assert p.history == []


@patch("providers.anthropic.Anthropic")
def test_anthropic_send_appends_user_and_assistant_messages(mock_class):
    mock_client = MagicMock()
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Hello back!"
    mock_client.messages.create.return_value.content = [text_block]
    mock_class.return_value = mock_client
    from providers.anthropic import AnthropicProvider
    p = AnthropicProvider(api_key="key", model="claude-opus-4-7", system_prompt="Help.")
    result = p.send("Hello!")
    assert result == "Hello back!"
    assert p.history == [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello back!"},
    ]


@patch("providers.anthropic.Anthropic")
def test_anthropic_send_passes_system_as_top_level_kwarg(mock_class):
    mock_client = MagicMock()
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "ok"
    mock_client.messages.create.return_value.content = [text_block]
    mock_class.return_value = mock_client
    from providers.anthropic import AnthropicProvider
    p = AnthropicProvider(api_key="key", model="claude-opus-4-7", system_prompt="Be concise.")
    p.send("hi")
    kwargs = mock_client.messages.create.call_args.kwargs
    assert kwargs["system"] == "Be concise."
    assert kwargs["max_tokens"] == 8192
    assert kwargs["messages"] == [{"role": "user", "content": "hi"}]


@patch("providers.anthropic.Anthropic")
def test_anthropic_send_accumulates_history_across_calls(mock_class):
    mock_client = MagicMock()
    first_block = MagicMock()
    first_block.type = "text"
    first_block.text = "First reply"
    second_block = MagicMock()
    second_block.type = "text"
    second_block.text = "Second reply"
    mock_client.messages.create.side_effect = [
        MagicMock(content=[first_block]),
        MagicMock(content=[second_block]),
    ]
    mock_class.return_value = mock_client
    from providers.anthropic import AnthropicProvider
    p = AnthropicProvider(api_key="key", model="claude-opus-4-7", system_prompt="Help.")
    p.send("First")
    p.send("Second")
    assert len(p.history) == 4
    # second call: user + assistant + user (system is top-level, not in messages)
    second_messages = mock_client.messages.create.call_args_list[1].kwargs["messages"]
    assert len(second_messages) == 3


@patch("providers.anthropic.Anthropic")
def test_anthropic_send_skips_non_text_blocks(mock_class):
    mock_client = MagicMock()
    thinking_block = MagicMock()
    thinking_block.type = "thinking"
    thinking_block.text = "should not be returned"
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Hello back!"
    mock_client.messages.create.return_value.content = [thinking_block, text_block]
    mock_class.return_value = mock_client
    from providers.anthropic import AnthropicProvider
    p = AnthropicProvider(api_key="key", model="claude-opus-4-7", system_prompt="Help.")
    result = p.send("Hi")
    assert result == "Hello back!"
    assert p.history[-1] == {"role": "assistant", "content": "Hello back!"}


@patch("providers.anthropic.Anthropic")
def test_anthropic_send_raises_runtime_error_on_api_failure(mock_class):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("overloaded")
    mock_class.return_value = mock_client
    from providers.anthropic import AnthropicProvider
    p = AnthropicProvider(api_key="key", model="claude-opus-4-7", system_prompt="Help.")
    with pytest.raises(RuntimeError, match="overloaded"):
        p.send("Hello!")
    assert p.history == []

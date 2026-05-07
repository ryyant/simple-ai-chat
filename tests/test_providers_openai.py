from unittest.mock import MagicMock, patch
import pytest


@patch("providers.openai.OpenAI")
def test_openai_initial_history_is_empty(mock_class):
    mock_class.return_value = MagicMock()
    from providers.openai import OpenAIProvider
    p = OpenAIProvider(api_key="key", model="gpt-4o", system_prompt="Help.")
    assert p.history == []


@patch("providers.openai.OpenAI")
def test_openai_send_appends_user_and_assistant_messages(mock_class):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices[0].message.content = "Hello back!"
    mock_class.return_value = mock_client
    from providers.openai import OpenAIProvider
    p = OpenAIProvider(api_key="key", model="gpt-4o", system_prompt="Help.")
    result = p.send("Hello!")
    assert result == "Hello back!"
    assert p.history == [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello back!"},
    ]


@patch("providers.openai.OpenAI")
def test_openai_send_includes_system_prompt_in_request(mock_class):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value.choices[0].message.content = "ok"
    mock_class.return_value = mock_client
    from providers.openai import OpenAIProvider
    p = OpenAIProvider(api_key="key", model="gpt-4o", system_prompt="Be concise.")
    p.send("hi")
    messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
    assert messages[0] == {"role": "system", "content": "Be concise."}
    assert messages[1] == {"role": "user", "content": "hi"}


@patch("providers.openai.OpenAI")
def test_openai_send_accumulates_history_across_calls(mock_class):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=MagicMock(content="First reply"))]),
        MagicMock(choices=[MagicMock(message=MagicMock(content="Second reply"))]),
    ]
    mock_class.return_value = mock_client
    from providers.openai import OpenAIProvider
    p = OpenAIProvider(api_key="key", model="gpt-4o", system_prompt="Help.")
    p.send("First")
    p.send("Second")
    assert len(p.history) == 4
    # second call sends: system + user + assistant + user = 4 messages
    second_messages = mock_client.chat.completions.create.call_args_list[1].kwargs["messages"]
    assert len(second_messages) == 4


@patch("providers.openai.OpenAI")
def test_openai_send_raises_runtime_error_on_api_failure(mock_class):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("rate limit")
    mock_class.return_value = mock_client
    from providers.openai import OpenAIProvider
    p = OpenAIProvider(api_key="key", model="gpt-4o", system_prompt="Help.")
    with pytest.raises(RuntimeError, match="rate limit"):
        p.send("Hello!")
    assert p.history == []

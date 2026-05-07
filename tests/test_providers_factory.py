from unittest.mock import MagicMock, patch
import pytest


@patch("providers.gemini.genai")
def test_create_provider_returns_gemini(mock_genai):
    mock_genai.Client.return_value.chats.create.return_value = MagicMock()
    from providers import create_provider
    from providers.gemini import GeminiProvider
    p = create_provider(provider="gemini", api_key="k", model="gemini-2.5-flash", system_prompt=".")
    assert isinstance(p, GeminiProvider)


@patch("providers.openai.OpenAI")
def test_create_provider_returns_openai(mock_class):
    mock_class.return_value = MagicMock()
    from providers import create_provider
    from providers.openai import OpenAIProvider
    p = create_provider(provider="openai", api_key="k", model="gpt-4o", system_prompt=".")
    assert isinstance(p, OpenAIProvider)


@patch("providers.anthropic.Anthropic")
def test_create_provider_returns_anthropic(mock_class):
    mock_class.return_value = MagicMock()
    from providers import create_provider
    from providers.anthropic import AnthropicProvider
    p = create_provider(provider="anthropic", api_key="k", model="claude-opus-4-7", system_prompt=".")
    assert isinstance(p, AnthropicProvider)


def test_create_provider_unknown_raises_value_error():
    from providers import create_provider
    with pytest.raises(ValueError, match="Unknown provider"):
        create_provider(provider="bogus", api_key="k", model="m", system_prompt=".")

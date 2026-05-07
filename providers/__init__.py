from providers.base import BaseProvider


def create_provider(
    provider: str, api_key: str, model: str, system_prompt: str
) -> BaseProvider:
    """Return the correct provider instance. Uses deferred imports so missing SDKs don't block other providers."""
    name = provider.lower()
    if name == "gemini":
        from providers.gemini import GeminiProvider
        return GeminiProvider(api_key=api_key, model=model, system_prompt=system_prompt)
    if name == "openai":
        from providers.openai import OpenAIProvider
        return OpenAIProvider(api_key=api_key, model=model, system_prompt=system_prompt)
    if name == "anthropic":
        from providers.anthropic import AnthropicProvider
        return AnthropicProvider(api_key=api_key, model=model, system_prompt=system_prompt)
    raise ValueError(f"Unknown provider: {provider!r}. Choose from: gemini, openai, anthropic")

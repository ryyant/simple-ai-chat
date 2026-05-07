import os
from typing import NamedTuple, Optional
from dotenv import load_dotenv
from chat import ChatSession

VALID_PROVIDERS = {"gemini", "openai", "anthropic"}

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-opus-4-7",
}

API_KEY_ENV_VARS = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


class HandleResult(NamedTuple):
    output: str
    new_session: Optional[ChatSession]


def handle_input(
    user_input: str,
    session: ChatSession,
    system_prompt: str,
    api_keys: dict[str, str],
) -> HandleResult:
    if user_input.startswith("/model"):
        args = user_input[len("/model"):].strip()

        if not args:
            return HandleResult(
                output=f"Current model: {session.current_provider}/{session.current_model}",
                new_session=None,
            )

        if "/" not in args:
            return HandleResult(
                output="Usage: /model <provider>/<model>  e.g. /model openai/gpt-4o",
                new_session=None,
            )

        provider, model = args.split("/", 1)
        provider = provider.strip().lower()
        model = model.strip()

        if provider not in VALID_PROVIDERS:
            return HandleResult(
                output=f"Unknown provider: {provider!r}. Choose from: {', '.join(sorted(VALID_PROVIDERS))}",
                new_session=None,
            )

        api_key = api_keys.get(provider, "")
        if not api_key:
            return HandleResult(
                output=f"No API key for {provider!r}. Set {API_KEY_ENV_VARS[provider]} in your .env file.",
                new_session=None,
            )

        try:
            new_session = ChatSession(
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                provider=provider,
            )
        except Exception as e:
            return HandleResult(
                output=f"Failed to switch to {provider}/{model}: {e}",
                new_session=None,
            )
        return HandleResult(
            output=f"Switched to {provider}/{model}. Conversation history cleared.",
            new_session=new_session,
        )

    try:
        reply = session.send(user_input)
        return HandleResult(output=reply, new_session=None)
    except Exception as e:
        return HandleResult(output=f"Error: {e}", new_session=None)


def main():
    load_dotenv()

    api_keys = {name: os.environ.get(env, "") for name, env in API_KEY_ENV_VARS.items()}

    provider = os.environ.get("PROVIDER", "gemini").lower()
    if provider not in VALID_PROVIDERS:
        print(f"Error: PROVIDER={provider!r} is not supported. Choose from: {', '.join(sorted(VALID_PROVIDERS))}")
        return

    api_key = api_keys.get(provider, "")
    if not api_key:
        print(f"Error: {API_KEY_ENV_VARS[provider]} is not set. Add it to your .env file.")
        return

    model = os.environ.get("MODEL") or DEFAULT_MODELS[provider]
    system_prompt = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")

    session = ChatSession(
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        provider=provider,
    )

    print(f"Chat started ({provider}/{model}).")
    print(f"  /model                          show current model")
    print(f"  /model <provider>/<model>       switch model (providers: gemini, openai, anthropic)")
    print(f"  Ctrl+C                          quit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        try:
            result = handle_input(user_input, session, system_prompt, api_keys)
        except KeyboardInterrupt:
            print("\n^C (cancelled)\n")
            continue

        if result.new_session is not None:
            session = result.new_session

        if user_input.startswith("/"):
            print(f"{result.output}\n")
        else:
            print(f"AI: {result.output}\n")


if __name__ == "__main__":
    main()

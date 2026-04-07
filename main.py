import os
from dotenv import load_dotenv
from chat import ChatSession


def main():
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set. Add it to your .env file.")
        return

    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
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

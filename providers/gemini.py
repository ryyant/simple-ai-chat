from google import genai
from google.genai import types

from providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, system_prompt: str):
        self._client = genai.Client(api_key=api_key)
        self._chat = self._client.chats.create(
            model=model,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        self.history: list[dict] = []

    def send(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        try:
            response = self._chat.send_message(message)
        except Exception as e:
            self.history.pop()
            raise RuntimeError(str(e)) from e
        reply = response.text
        self.history.append({"role": "assistant", "content": reply})
        return reply

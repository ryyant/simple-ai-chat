from openai import OpenAI

from providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, system_prompt: str):
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._system_prompt = system_prompt
        self.history: list[dict] = []

    def send(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self._system_prompt}] + [
            {"role": h["role"], "content": h["content"]} for h in self.history
        ]
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
            )
        except Exception as e:
            self.history.pop()
            raise RuntimeError(str(e)) from e
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

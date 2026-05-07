from anthropic import Anthropic

from providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, system_prompt: str):
        self._client = Anthropic(api_key=api_key)
        self._model = model
        self._system_prompt = system_prompt
        self.history: list[dict] = []

    def send(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        messages = [{"role": h["role"], "content": h["content"]} for h in self.history]
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=8192,
                system=self._system_prompt,
                messages=messages,
            )
        except Exception as e:
            self.history.pop()
            raise RuntimeError(str(e)) from e
        reply = "".join(block.text for block in response.content if block.type == "text")
        self.history.append({"role": "assistant", "content": reply})
        return reply

import pytest
from providers.base import BaseProvider


def test_base_provider_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseProvider()


def test_base_provider_subclass_must_implement_send():
    class Incomplete(BaseProvider):
        pass

    with pytest.raises(TypeError):
        Incomplete()


def test_base_provider_subclass_with_send_is_valid():
    class Complete(BaseProvider):
        def __init__(self):
            self.history = []

        def send(self, message: str) -> str:
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": "ok"})
            return "ok"

    obj = Complete()
    assert obj.send("hi") == "ok"
    assert obj.history == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "ok"},
    ]

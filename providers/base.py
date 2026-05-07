from abc import ABC, abstractmethod


class BaseProvider(ABC):
    history: list[dict]

    @abstractmethod
    def send(self, message: str) -> str:
        """Send a message and return the assistant's reply."""

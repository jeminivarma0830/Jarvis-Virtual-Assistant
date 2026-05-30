"""skills/base_skill.py — Abstract base class every skill must implement."""

from abc import ABC, abstractmethod


class BaseSkill(ABC):
    @abstractmethod
    def matches(self, text: str) -> bool:
        """Return True if this skill can handle the given (lowercased) text."""

    @abstractmethod
    def handle(self, text: str) -> str:
        """Process the input and return a response string."""

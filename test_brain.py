"""
tests/test_brain.py  –  Unit tests for the Brain (mocked API)
Run:  pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from core.brain import Brain


def _mock_brain() -> Brain:
    """Return a Brain with a mocked Anthropic client."""
    b = Brain()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Mocked response.")]
    b._client.messages.create = MagicMock(return_value=mock_response)
    return b


def test_think_returns_string():
    brain = _mock_brain()
    reply = brain.think("Hello JARVIS")
    assert isinstance(reply, str)
    assert len(reply) > 0


def test_history_grows():
    brain = _mock_brain()
    brain.think("First message")
    brain.think("Second message")
    # 2 user + 2 assistant = 4 entries
    assert len(brain._history) == 4


def test_reset_clears_history():
    brain = _mock_brain()
    brain.think("Something")
    brain.reset()
    assert brain._history == []


def test_history_trimmed():
    brain = _mock_brain()
    for i in range(15):
        brain.think(f"Message {i}")
    from config.settings import CONTEXT_WINDOW
    assert len(brain._history) <= CONTEXT_WINDOW

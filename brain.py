"""
core/brain.py  –  The AI brain: sends messages to Claude, manages conversation history
"""
import logging
import anthropic
from config.settings import (
    ANTHROPIC_API_KEY, AI_MODEL, MAX_TOKENS, SYSTEM_PROMPT, CONTEXT_WINDOW
)

logger = logging.getLogger(__name__)


class Brain:
    """
    Manages conversation with Claude.
    Keeps a rolling context window and injects long-term memories.
    """

    def __init__(self, memory=None):
        self._client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self._history: list[dict] = []   # [{role, content}, ...]
        self._memory = memory            # optional Memory instance

    # ── Public ────────────────────────────────────────────────

    def think(self, user_input: str) -> str:
        """Send user_input to Claude, return the assistant reply."""
        # Optionally enrich prompt with long-term memories
        enriched_input = self._enrich_with_memory(user_input)

        self._history.append({"role": "user", "content": enriched_input})
        self._trim_history()

        try:
            response = self._client.messages.create(
                model=AI_MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=self._history,
            )
            reply = response.content[0].text
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            reply = "I'm sorry, I encountered an error reaching my AI core."

        self._history.append({"role": "assistant", "content": reply})

        # Store this exchange in long-term memory
        if self._memory:
            self._memory.store(user_input, reply)

        return reply

    def reset(self):
        """Clear conversation history."""
        self._history = []
        logger.info("Conversation history cleared.")

    # ── Private ───────────────────────────────────────────────

    def _trim_history(self):
        """Keep only the last CONTEXT_WINDOW messages."""
        if len(self._history) > CONTEXT_WINDOW:
            self._history = self._history[-CONTEXT_WINDOW:]

    def _enrich_with_memory(self, user_input: str) -> str:
        """Prepend relevant long-term memories to the user message."""
        if not self._memory:
            return user_input
        memories = self._memory.recall(user_input)
        if not memories:
            return user_input
        mem_text = "\n".join(f"- {m}" for m in memories)
        return f"[Relevant memories]\n{mem_text}\n\n[User says]\n{user_input}"

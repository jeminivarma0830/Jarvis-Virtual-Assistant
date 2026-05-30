"""
core/assistant.py
Central orchestrator — ties together voice, brain, memory, and skills.
"""

import time
from core.brain import Brain
from core.listener import Listener
from core.speaker import Speaker
from core.wake_word import WakeWordDetector
from memory.memory_manager import MemoryManager
from skills.skill_router import SkillRouter
from core.logger import get_logger

logger = get_logger(__name__)


class JarvisAssistant:
    def __init__(self, mode: str = "voice", use_wake_word: bool = True):
        self.mode = mode
        self.use_wake_word = use_wake_word

        logger.info("Loading components...")
        self.brain = Brain()
        self.speaker = Speaker()
        self.memory = MemoryManager()
        self.skill_router = SkillRouter()

        if mode == "voice":
            self.listener = Listener()
            if use_wake_word:
                self.wake_detector = WakeWordDetector()

        self.speaker.say("JARVIS online. How can I help you?")

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        if self.mode == "text":
            self._run_text_mode()
        elif self.mode == "voice":
            self._run_voice_mode()
        elif self.mode == "ui":
            from ui.server import start_server
            start_server(self)

    def _run_text_mode(self):
        """Simple REPL for terminal use."""
        from rich.console import Console
        console = Console()
        console.print("[bold cyan]JARVIS Text Mode[/bold cyan] — type your request, Ctrl+C to quit.\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                response = self.process(user_input)
                console.print(f"[bold green]JARVIS:[/bold green] {response}\n")
            except (KeyboardInterrupt, EOFError):
                break

    def _run_voice_mode(self):
        """Microphone loop with optional wake word."""
        logger.info(f"Voice mode started. Wake word: {self.use_wake_word}")

        while True:
            if self.use_wake_word:
                logger.info("Waiting for wake word...")
                self.wake_detector.wait_for_wake_word()

            logger.info("Listening...")
            self.speaker.play_chime()           # short beep so user knows it's listening
            text = self.listener.listen()

            if not text:
                continue

            logger.info(f"Heard: {text}")
            response = self.process(text)
            self.speaker.say(response)

    # ── Core processing ───────────────────────────────────────────────────────

    def process(self, user_input: str) -> str:
        """
        Full pipeline:
        1. Check skills first (fast, deterministic)
        2. Retrieve relevant memories for context
        3. Call LLM brain with context + history
        4. Save exchange to memory
        5. Return response string
        """
        # 1. Try skill shortcuts (e.g. "play music", "set timer")
        skill_response = self.skill_router.route(user_input)
        if skill_response is not None:
            self._save_exchange(user_input, skill_response)
            return skill_response

        # 2. Retrieve relevant long-term memories
        memories = self.memory.search(user_input, top_k=3)
        memory_context = self._format_memories(memories)

        # 3. Ask the LLM
        response = self.brain.chat(
            user_input=user_input,
            memory_context=memory_context,
        )

        # 4. Persist exchange
        self._save_exchange(user_input, response)

        return response

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _format_memories(self, memories: list) -> str:
        if not memories:
            return ""
        lines = ["Relevant memories from past conversations:"]
        for m in memories:
            lines.append(f"  - {m['text']}")
        return "\n".join(lines)

    def _save_exchange(self, user_input: str, response: str):
        combined = f"User said: {user_input}. JARVIS replied: {response}"
        self.memory.add(combined)

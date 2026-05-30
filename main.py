"""
main.py  –  JARVIS entry point
Usage:
    python main.py          # voice mode
    python main.py --text   # text-only mode (no microphone needed)
"""
import sys
import argparse
import time
from rich.console import Console
from rich.panel   import Panel
from rich import print as rprint

from core.logger     import setup_logger
from core.brain      import Brain
from core.speech     import Listener, Speaker
from core.dispatcher import dispatch
from memory.long_term import Memory
from config.settings  import JARVIS_NAME, USER_NAME, WAKE_WORD

setup_logger()
console = Console()


def boot_banner():
    console.print(Panel.fit(
        f"[bold cyan]{JARVIS_NAME}[/bold cyan] — Personal AI Assistant\n"
        f"[dim]Serving: {USER_NAME}[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))


def run_voice_mode(brain: Brain, speaker: Speaker):
    """Main voice loop."""
    listener = Listener()
    speaker.speak(f"Good day, {USER_NAME}. JARVIS is online.")

    while True:
        text = listener.listen()
        if text is None:
            continue

        # Wake word check (optional — remove if always-on is preferred)
        if WAKE_WORD and WAKE_WORD not in text:
            continue
        # Strip wake word from the actual command
        text = text.replace(WAKE_WORD, "").strip()
        if not text:
            speaker.speak("Yes?")
            continue

        reply = handle_input(text, brain)
        speaker.speak(reply)

        if _exit_requested(text):
            break


def run_text_mode(brain: Brain, speaker: Speaker):
    """Keyboard-driven loop (useful for testing without a mic)."""
    rprint("[bold cyan]JARVIS text mode[/bold cyan] — type [bold]quit[/bold] to exit\n")
    speaker.speak(f"Good day, {USER_NAME}. Text mode active.")

    while True:
        try:
            text = input(f"[{USER_NAME}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            rprint("\n[dim]Session ended.[/dim]")
            break

        if not text:
            continue
        if _exit_requested(text):
            speaker.speak(f"Goodbye, {USER_NAME}.")
            break

        reply = handle_input(text, brain)
        speaker.speak(reply)


def handle_input(text: str, brain: Brain) -> str:
    """Try a skill first; fall back to the AI brain."""
    # Special commands
    if text in ("reset", "clear memory", "forget everything"):
        brain.reset()
        return "Conversation history cleared."

    # Skill dispatcher
    skill_reply = dispatch(text, brain)
    if skill_reply:
        return skill_reply

    # AI brain
    return brain.think(text)


def _exit_requested(text: str) -> bool:
    return any(w in text.lower() for w in ("goodbye", "good night", "exit", "quit", "shut down jarvis"))


def main():
    parser = argparse.ArgumentParser(description="JARVIS AI Assistant")
    parser.add_argument("--text", action="store_true", help="Run in text-only mode")
    args = parser.parse_args()

    boot_banner()

    memory  = Memory()
    brain   = Brain(memory=memory)
    speaker = Speaker()

    if args.text:
        run_text_mode(brain, speaker)
    else:
        run_voice_mode(brain, speaker)


if __name__ == "__main__":
    main()

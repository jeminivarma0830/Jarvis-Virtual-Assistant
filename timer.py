"""skills/timer.py — Set countdown timers."""

import re
import threading
from skills.base_skill import BaseSkill
from core.logger import get_logger

logger = get_logger(__name__)


class TimerSkill(BaseSkill):
    TRIGGERS = ("timer", "remind me in", "set a timer", "alarm in")

    def matches(self, text: str) -> bool:
        return any(t in text for t in self.TRIGGERS)

    def handle(self, text: str) -> str:
        seconds = self._parse_duration(text)
        if seconds is None:
            return "How long should I set the timer for, sir?"
        label = self._friendly(seconds)
        t = threading.Timer(seconds, self._ring, args=(label,))
        t.daemon = True
        t.start()
        return f"Timer set for {label}. I'll let you know when it's up."

    def _parse_duration(self, text: str) -> int | None:
        total = 0
        found = False
        for val, unit in re.findall(r"(\d+)\s*(hour|minute|second|hr|min|sec)s?", text, re.IGNORECASE):
            found = True
            v = int(val)
            unit = unit.lower()
            if unit in ("hour", "hr"):
                total += v * 3600
            elif unit in ("minute", "min"):
                total += v * 60
            else:
                total += v
        return total if found else None

    def _friendly(self, seconds: int) -> str:
        parts = []
        if seconds >= 3600:
            parts.append(f"{seconds // 3600} hour{'s' if seconds // 3600 > 1 else ''}")
            seconds %= 3600
        if seconds >= 60:
            parts.append(f"{seconds // 60} minute{'s' if seconds // 60 > 1 else ''}")
            seconds %= 60
        if seconds:
            parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")
        return " ".join(parts)

    def _ring(self, label: str):
        logger.info(f"Timer done: {label}")
        # Try to speak — works if Speaker is accessible, otherwise just logs
        try:
            from core.speaker import Speaker
            Speaker().say(f"Sir, your {label} timer is up.")
        except Exception:
            print(f"\n⏰ Timer complete: {label}")

"""
skills/skill_router.py
Routes user input to the appropriate skill using keyword matching.
Returns None if no skill matched (falls through to the LLM).
"""

import re
from core.logger import get_logger

logger = get_logger(__name__)


class SkillRouter:
    def __init__(self):
        # Lazy-import skills to avoid startup errors if optional deps missing
        from skills.weather import WeatherSkill
        from skills.timer import TimerSkill
        from skills.jokes import JokeSkill
        from skills.system_info import SystemInfoSkill

        self._skills = [
            WeatherSkill(),
            TimerSkill(),
            JokeSkill(),
            SystemInfoSkill(),
        ]

        # Try optional skills
        try:
            from skills.spotify import SpotifySkill
            self._skills.append(SpotifySkill())
        except Exception:
            logger.debug("Spotify skill not available.")

        logger.info(f"Skill router ready — {len(self._skills)} skills loaded.")

    def route(self, text: str) -> str | None:
        """
        Check each skill. Return the skill's response or None to fall through to LLM.
        """
        text_lower = text.lower()
        for skill in self._skills:
            if skill.matches(text_lower):
                logger.info(f"Skill matched: {skill.__class__.__name__}")
                try:
                    return skill.handle(text)
                except Exception as e:
                    logger.error(f"Skill error in {skill.__class__.__name__}: {e}")
                    return f"I tried to handle that but ran into an error, sir."
        return None

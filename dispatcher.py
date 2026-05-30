"""
core/dispatcher.py  –  Routes user intent to the right skill
"""
import logging
from skills.weather  import get_weather
from skills.search   import web_search
from skills.system   import system_control
from config.settings import JARVIS_NAME

logger = logging.getLogger(__name__)

# Keyword → skill mapping (extend freely)
SKILL_MAP = {
    ("weather", "temperature", "forecast", "rain", "sunny", "humidity"): get_weather,
    ("search", "google", "look up", "find", "who is", "what is"): web_search,
    ("open", "launch", "close", "shutdown", "volume", "mute"):     system_control,
}


def dispatch(user_input: str, brain) -> str | None:
    """
    Check if user_input matches a skill keyword.
    If yes, run the skill and return its output (string).
    If no skill matches, return None so brain.think() handles it.
    """
    lower = user_input.lower()

    for keywords, skill_fn in SKILL_MAP.items():
        if any(kw in lower for kw in keywords):
            logger.info(f"Dispatching to skill: {skill_fn.__name__}")
            try:
                return skill_fn(user_input)
            except Exception as e:
                logger.error(f"Skill error ({skill_fn.__name__}): {e}")
                return f"I encountered an error with that request, {brain._memory and 'Sir' or 'Sir'}."

    return None   # let the brain handle it

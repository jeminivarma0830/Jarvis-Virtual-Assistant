"""
skills/system.py  –  System control: open apps, adjust volume, shutdown, etc.
"""
import subprocess
import platform
import logging

logger = logging.getLogger(__name__)
OS = platform.system()   # "Windows" | "Darwin" | "Linux"


def system_control(user_input: str) -> str:
    """Route system commands based on keywords in user_input."""
    lower = user_input.lower()

    if "shutdown" in lower or "shut down" in lower:
        return _shutdown()
    if "open" in lower or "launch" in lower:
        return _open_app(lower)
    if "volume" in lower:
        return _volume_control(lower)
    if "mute" in lower:
        return _mute()

    return "I'm not sure what system action you'd like me to perform."


def _open_app(text: str) -> str:
    """Open a named application."""
    import re
    match = re.search(r"(?:open|launch)\s+(.+)", text)
    app = match.group(1).strip() if match else ""
    if not app:
        return "Which application should I open?"
    try:
        if OS == "Darwin":
            subprocess.Popen(["open", "-a", app])
        elif OS == "Windows":
            subprocess.Popen(["start", app], shell=True)
        else:
            subprocess.Popen([app])
        return f"Opening {app}."
    except FileNotFoundError:
        return f"I couldn't find '{app}' on this system."
    except Exception as e:
        logger.error(f"Open app error: {e}")
        return f"Failed to open {app}."


def _volume_control(text: str) -> str:
    import re
    match = re.search(r"(\d+)", text)
    level = int(match.group(1)) if match else None
    try:
        if OS == "Darwin" and level is not None:
            subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
            return f"Volume set to {level}%."
        elif OS == "Linux" and level is not None:
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{level}%"])
            return f"Volume set to {level}%."
        return "Volume adjustment isn't supported on this OS yet."
    except Exception as e:
        logger.error(f"Volume error: {e}")
        return "I couldn't adjust the volume."


def _mute() -> str:
    try:
        if OS == "Darwin":
            subprocess.run(["osascript", "-e", "set volume with output muted"])
        elif OS == "Linux":
            subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "mute"])
        return "Audio muted."
    except Exception as e:
        logger.error(f"Mute error: {e}")
        return "I couldn't mute the audio."


def _shutdown() -> str:
    return "I won't initiate a system shutdown without explicit confirmation. Please type 'confirm shutdown' if you're sure."

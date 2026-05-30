"""
core/speaker.py
Text-to-speech — converts JARVIS responses to audio.
Uses ElevenLabs if configured, otherwise falls back to pyttsx3 (offline).
"""

import os
import threading
from dotenv import load_dotenv
from core.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "")


class Speaker:
    def __init__(self):
        self._use_elevenlabs = bool(ELEVENLABS_KEY)
        self._lock = threading.Lock()

        if self._use_elevenlabs:
            from elevenlabs.client import ElevenLabs
            self._el_client = ElevenLabs(api_key=ELEVENLABS_KEY)
            logger.info("Speaker: ElevenLabs TTS enabled.")
        else:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 175)
            self._engine.setProperty("volume", 0.9)
            # Pick a decent voice if available
            voices = self._engine.getProperty("voices")
            if voices:
                self._engine.setProperty("voice", voices[0].id)
            logger.info("Speaker: pyttsx3 (offline) TTS enabled.")

    def say(self, text: str):
        """Speak text (blocking)."""
        if not text:
            return
        logger.debug(f"Speaking: {text[:80]}...")
        with self._lock:
            if self._use_elevenlabs:
                self._speak_elevenlabs(text)
            else:
                self._speak_pyttsx3(text)

    def say_async(self, text: str):
        """Speak text in a background thread (non-blocking)."""
        t = threading.Thread(target=self.say, args=(text,), daemon=True)
        t.start()

    def play_chime(self):
        """Play a short activation sound (beep)."""
        try:
            import winsound
            winsound.Beep(880, 150)          # Windows
        except ImportError:
            try:
                import subprocess
                subprocess.run(["aplay", "-q", "/usr/share/sounds/alsa/Front_Left.wav"],
                               timeout=1, check=False)  # Linux
            except Exception:
                pass                         # Silent fallback

    # ── Backends ──────────────────────────────────────────────────────────────

    def _speak_pyttsx3(self, text: str):
        self._engine.say(text)
        self._engine.runAndWait()

    def _speak_elevenlabs(self, text: str):
        import tempfile, os
        try:
            audio = self._el_client.generate(
                text=text,
                voice=ELEVENLABS_VOICE or "Josh",
                model="eleven_multilingual_v2",
            )
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name
                for chunk in audio:
                    f.write(chunk)
            # Play with ffplay (cross-platform)
            import subprocess
            subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}. Falling back to pyttsx3.")
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

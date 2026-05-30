"""
core/wake_word.py
Wake word detection using Picovoice Porcupine.
Blocks until "Hey JARVIS" (or configured keyword) is detected.
Free API key: https://console.picovoice.ai/
"""

import os
import struct
from dotenv import load_dotenv
from core.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

PICOVOICE_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "")


class WakeWordDetector:
    def __init__(self, keyword: str = "jarvis"):
        if not PICOVOICE_KEY:
            logger.warning(
                "PICOVOICE_ACCESS_KEY not set — wake word detection disabled. "
                "JARVIS will always listen."
            )
            self._enabled = False
            return

        try:
            import pvporcupine
            import pyaudio

            self._enabled = True
            self._porcupine = pvporcupine.create(
                access_key=PICOVOICE_KEY,
                keywords=[keyword],
            )
            self._pa = pyaudio.PyAudio()
            self._stream = self._pa.open(
                rate=self._porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self._porcupine.frame_length,
            )
            logger.info(f"Wake word detector ready — keyword: '{keyword}'")
        except Exception as e:
            logger.error(f"Failed to initialise wake word detector: {e}")
            self._enabled = False

    def wait_for_wake_word(self):
        """Block until the wake word is spoken."""
        if not self._enabled:
            return           # no-op if not configured

        logger.debug("Listening for wake word...")
        while True:
            pcm = self._stream.read(
                self._porcupine.frame_length, exception_on_overflow=False
            )
            pcm = struct.unpack_from("h" * self._porcupine.frame_length, pcm)
            result = self._porcupine.process(pcm)
            if result >= 0:
                logger.info("Wake word detected!")
                return

    def __del__(self):
        if hasattr(self, "_stream") and self._stream:
            self._stream.close()
        if hasattr(self, "_pa") and self._pa:
            self._pa.terminate()
        if hasattr(self, "_porcupine") and self._porcupine:
            self._porcupine.delete()

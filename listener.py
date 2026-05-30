"""
core/listener.py
Speech-to-text — captures microphone audio and converts it to text.
Uses Google STT by default; falls back to local Whisper if preferred.
"""

import os
import speech_recognition as sr
from core.logger import get_logger

logger = get_logger(__name__)

USE_WHISPER = os.getenv("USE_WHISPER", "false").lower() == "true"


class Listener:
    def __init__(self):
        self.recogniser = sr.Recognizer()
        self.recogniser.energy_threshold = 300     # adjust for ambient noise
        self.recogniser.pause_threshold = 0.8      # seconds of silence = end of phrase
        self.microphone = sr.Microphone()

        # Calibrate ambient noise on startup
        with self.microphone as source:
            logger.info("Calibrating microphone for ambient noise...")
            self.recogniser.adjust_for_ambient_noise(source, duration=1)
        logger.info("Listener ready.")

        if USE_WHISPER:
            import whisper
            self._whisper_model = whisper.load_model("base")
            logger.info("Whisper model loaded (local STT).")

    def listen(self, timeout: int = 5, phrase_limit: int = 15) -> str:
        """
        Record audio and return transcribed text.
        Returns empty string if nothing was heard or transcription failed.
        """
        with self.microphone as source:
            try:
                audio = self.recogniser.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
            except sr.WaitTimeoutError:
                return ""

        return self._transcribe(audio)

    def _transcribe(self, audio: sr.AudioData) -> str:
        if USE_WHISPER:
            return self._transcribe_whisper(audio)
        return self._transcribe_google(audio)

    def _transcribe_google(self, audio: sr.AudioData) -> str:
        try:
            text = self.recogniser.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            logger.debug("Google STT: could not understand audio.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Google STT request failed: {e}")
            return ""

    def _transcribe_whisper(self, audio: sr.AudioData) -> str:
        import tempfile, wave, os
        try:
            # Save audio to a temp WAV, then run Whisper on it
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                wav_path = f.name
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(audio.sample_width)
                wf.setframerate(audio.sample_rate)
                wf.writeframes(audio.get_raw_data())
            result = self._whisper_model.transcribe(wav_path)
            return result.get("text", "").strip()
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return ""
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

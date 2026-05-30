"""
core/speech.py  –  Speech-to-Text and Text-to-Speech
"""
import logging
import speech_recognition as sr
import pyttsx3
from config.settings import (
    STT_ENGINE, TTS_ENGINE, TTS_RATE, TTS_VOLUME,
    ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
)

logger = logging.getLogger(__name__)

# ─────────────────────────── TTS ──────────────────────────────

class Speaker:
    """Converts text to speech using the configured engine."""

    def __init__(self):
        if TTS_ENGINE == "pyttsx3":
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", TTS_RATE)
            self._engine.setProperty("volume", TTS_VOLUME)
            # Pick a decent voice (index 1 is often more natural)
            voices = self._engine.getProperty("voices")
            if len(voices) > 1:
                self._engine.setProperty("voice", voices[1].id)

    def speak(self, text: str):
        """Speak text aloud."""
        if not text:
            return
        logger.info(f"[TTS] {text}")
        print(f"\n🤖 JARVIS: {text}\n")

        if TTS_ENGINE == "elevenlabs" and ELEVENLABS_API_KEY:
            self._speak_elevenlabs(text)
        else:
            self._speak_pyttsx3(text)

    def _speak_pyttsx3(self, text: str):
        self._engine.say(text)
        self._engine.runAndWait()

    def _speak_elevenlabs(self, text: str):
        try:
            import requests, io
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
            headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
            payload = {"text": text, "model_id": "eleven_monolingual_v1",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(io.BytesIO(r.content))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            else:
                logger.error(f"ElevenLabs error {r.status_code}: {r.text}")
                self._speak_pyttsx3(text)   # fallback
        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")
            self._speak_pyttsx3(text)


# ─────────────────────────── STT ──────────────────────────────

class Listener:
    """Converts microphone audio to text."""

    def __init__(self):
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = 300
        self._recognizer.dynamic_energy_threshold = True

    def listen(self, timeout: int = 5, phrase_limit: int = 10) -> str | None:
        """Record from microphone and return transcribed text, or None on failure."""
        with sr.Microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("🎙  Listening...")
            try:
                audio = self._recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
            except sr.WaitTimeoutError:
                return None

        try:
            if STT_ENGINE == "whisper":
                text = self._recognizer.recognize_whisper(audio, language="english")
            else:
                text = self._recognizer.recognize_google(audio)
            logger.info(f"[STT] Heard: {text}")
            return text.lower().strip()
        except sr.UnknownValueError:
            logger.debug("STT: could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"STT request error: {e}")
            return None

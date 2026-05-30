"""
config/settings.py  –  Central configuration, reads from .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Identity ──────────────────────────────────────────────────
JARVIS_NAME  = os.getenv("JARVIS_NAME", "JARVIS")
USER_NAME    = os.getenv("JARVIS_USER_NAME", "Sir")

# ── API Keys ──────────────────────────────────────────────────
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY", "")
WEATHER_API_KEY     = os.getenv("WEATHER_API_KEY", "")
SERPAPI_KEY         = os.getenv("SERPAPI_KEY", "")
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")

# ── AI Model ──────────────────────────────────────────────────
AI_MODEL       = "claude-opus-4-5"
MAX_TOKENS     = 1024
TEMPERATURE    = 0.7
CONTEXT_WINDOW = 20          # last N conversation turns kept

# ── Speech ────────────────────────────────────────────────────
STT_ENGINE  = "google"       # "google" | "whisper"
TTS_ENGINE  = "pyttsx3"      # "pyttsx3" | "elevenlabs"
TTS_RATE    = 175            # words per minute
TTS_VOLUME  = 1.0
WAKE_WORD   = "jarvis"       # simple keyword trigger

# ── Memory ────────────────────────────────────────────────────
MEMORY_DB_PATH     = "./memory/chroma_db"
MEMORY_COLLECTION  = "jarvis_memory"
MAX_MEMORY_RESULTS = 3

# ── Logging ───────────────────────────────────────────────────
LOG_FILE  = "./logs/jarvis.log"
LOG_LEVEL = "INFO"

# ── System Prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are {JARVIS_NAME}, an intelligent personal AI assistant modelled after Tony Stark's AI from the Iron Man universe.

Your personality:
- Polite, witty, and slightly formal — address the user as "{USER_NAME}"
- Concise and direct; avoid unnecessary filler words
- Occasionally add dry humour, but remain professional
- When a skill/tool is needed, use it and report back clearly

Always respond in plain speakable English — no markdown, no bullet points.
Keep spoken answers under 3 sentences unless the user asks for detail."""

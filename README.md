# JARVIS – Personal AI Assistant

A Python-based voice + text AI assistant powered by Claude (Anthropic).

## Quick Start

### 1. Clone / set up
```bash
git clone <your-repo>
cd jarvis
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run
```bash
# Voice mode (requires microphone)
python main.py

# Text mode (no mic needed — great for testing)
python main.py --text

# Web dashboard
python ui/dashboard.py
# → open http://localhost:5000
```

### 4. Tests
```bash
pytest tests/
```

## Folder Structure
```
jarvis/
├── main.py               Entry point (voice + text modes)
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py       All config & system prompt
├── core/
│   ├── brain.py          Claude AI conversation manager
│   ├── speech.py         STT (mic → text) & TTS (text → voice)
│   ├── dispatcher.py     Routes intent to skills
│   └── logger.py         Logging setup
├── skills/
│   ├── weather.py        OpenWeatherMap integration
│   ├── search.py         Web search (SerpAPI / DuckDuckGo)
│   └── system.py         Open apps, volume, OS control
├── memory/
│   └── long_term.py      ChromaDB vector memory
├── ui/
│   ├── dashboard.py      Flask + SocketIO web UI
│   └── templates/
│       └── index.html    Dark-theme chat interface
├── logs/
│   └── jarvis.log
└── tests/
    ├── test_brain.py
    └── test_skills.py
```

## Adding a New Skill

1. Create `skills/my_skill.py` with a function `my_skill(user_input: str) -> str`
2. Register it in `core/dispatcher.py`:
```python
from skills.my_skill import my_skill
SKILL_MAP = {
    ...
    ("keyword1", "keyword2"): my_skill,
}
```

## Wake Word
Say **"JARVIS"** before your command in voice mode.
Example: *"JARVIS, what's the weather in Delhi?"*

To disable the wake word requirement, set `WAKE_WORD = ""` in `config/settings.py`.

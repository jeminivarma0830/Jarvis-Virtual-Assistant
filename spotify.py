"""skills/spotify.py — Basic Spotify playback control via spotipy."""

import os
import re
from dotenv import load_dotenv
from skills.base_skill import BaseSkill
from core.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

TRIGGERS = ("play", "pause music", "next song", "skip song", "stop music",
            "resume music", "volume up", "volume down")


class SpotifySkill(BaseSkill):
    def __init__(self):
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth

        self._sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"),
                scope="user-modify-playback-state user-read-playback-state",
            )
        )
        logger.info("Spotify skill ready.")

    def matches(self, text: str) -> bool:
        return any(t in text for t in TRIGGERS)

    def handle(self, text: str) -> str:
        t = text.lower()

        if re.search(r"play (.+)", t):
            query = re.search(r"play (.+)", t).group(1).strip()
            return self._play_track(query)

        if any(w in t for w in ("pause", "stop music")):
            self._sp.pause_playback()
            return "Paused."

        if any(w in t for w in ("resume", "continue")):
            self._sp.start_playback()
            return "Resuming playback."

        if any(w in t for w in ("next", "skip")):
            self._sp.next_track()
            return "Skipping to next track."

        if "volume up" in t:
            self._adjust_volume(+10)
            return "Volume increased."

        if "volume down" in t:
            self._adjust_volume(-10)
            return "Volume decreased."

        return "I didn't catch what you wanted to do with Spotify, sir."

    def _play_track(self, query: str) -> str:
        results = self._sp.search(q=query, limit=1, type="track")
        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            return f"Couldn't find '{query}' on Spotify."
        uri = tracks[0]["uri"]
        name = tracks[0]["name"]
        artist = tracks[0]["artists"][0]["name"]
        self._sp.start_playback(uris=[uri])
        return f"Playing '{name}' by {artist}."

    def _adjust_volume(self, delta: int):
        devices = self._sp.devices().get("devices", [])
        if devices:
            current = devices[0].get("volume_percent", 50)
            new_vol = max(0, min(100, current + delta))
            self._sp.volume(new_vol)

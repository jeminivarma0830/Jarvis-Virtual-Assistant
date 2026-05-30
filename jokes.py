"""skills/jokes.py — Tells a random joke."""

import random
from skills.base_skill import BaseSkill

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why did the robot go on a diet? It had too many bytes.",
    "There are 10 types of people: those who understand binary, and those who don't.",
    "My WiFi password is 'incorrect'. So when guests ask, I say 'incorrect' — works every time.",
]


class JokeSkill(BaseSkill):
    TRIGGERS = ("joke", "make me laugh", "funny", "tell me something funny")

    def matches(self, text: str) -> bool:
        return any(t in text for t in self.TRIGGERS)

    def handle(self, text: str) -> str:
        return random.choice(JOKES)

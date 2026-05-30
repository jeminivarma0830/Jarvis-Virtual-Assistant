"""skills/system_info.py — CPU, RAM, battery, and time/date queries."""

import platform
import datetime
from skills.base_skill import BaseSkill


class SystemInfoSkill(BaseSkill):
    TRIGGERS = (
        "what time", "what's the time", "what date", "today's date",
        "cpu", "ram", "memory usage", "battery", "disk space",
        "system info",
    )

    def matches(self, text: str) -> bool:
        return any(t in text for t in self.TRIGGERS)

    def handle(self, text: str) -> str:
        text = text.lower()

        if "time" in text:
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"It's {now}, sir."

        if "date" in text:
            today = datetime.date.today().strftime("%A, %B %d, %Y")
            return f"Today is {today}."

        try:
            import psutil
        except ImportError:
            return "The psutil library isn't installed, sir. Run: pip install psutil"

        if "battery" in text:
            b = psutil.sensors_battery()
            if b:
                status = "charging" if b.power_plugged else "discharging"
                return f"Battery is at {int(b.percent)}% and {status}."
            return "No battery detected — you must be plugged in, sir."

        if "cpu" in text:
            cpu = psutil.cpu_percent(interval=1)
            return f"CPU usage is at {cpu}%."

        if "ram" in text or "memory" in text:
            vm = psutil.virtual_memory()
            used = round(vm.used / 1e9, 1)
            total = round(vm.total / 1e9, 1)
            return f"RAM: {used} GB used of {total} GB ({vm.percent}%)."

        if "disk" in text:
            d = psutil.disk_usage("/")
            free = round(d.free / 1e9, 1)
            total = round(d.total / 1e9, 1)
            return f"Disk: {free} GB free of {total} GB."

        # Default: quick summary
        cpu = psutil.cpu_percent(interval=0.5)
        vm = psutil.virtual_memory()
        return (
            f"System: {platform.system()} {platform.release()}. "
            f"CPU {cpu}%, RAM {vm.percent}% used."
        )

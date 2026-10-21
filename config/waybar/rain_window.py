#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

LOCATIONS = os.path.expanduser("~/.config/rain-window/locations")
TRIP_MINUTES = 20
STEP_MINUTES = 5
DRY_MM_PER_HOUR = 0.1
LINE_GAP = "\n<span size='6pt'> </span>\n"
BAR_LEVELS = [(16, "█"), (8, "▇"), (4, "▆"), (2, "▅"), (1, "▄"), (0.5, "▃"), (DRY_MM_PER_HOUR, "▂")]


def read_locations():
    try:
        with open(LOCATIONS) as f:
            return [line.split()[:2] for line in f if line.strip()]
    except OSError:
        return []


def intensity(value):
    return 0.0 if value == 0 else 10 ** ((value - 109) / 32)


def forecast(lat, lon):
    url = f"https://gpsgadget.buienradar.nl/data/raintext?lat={lat}&lon={lon}"
    with urllib.request.urlopen(url, timeout=10) as response:
        lines = response.read().decode().splitlines()
    rows = [line.strip().split("|") for line in lines if "|" in line]
    return [(time, intensity(int(value))) for value, time in rows]


def bar(mm_per_hour):
    return next((char for level, char in BAR_LEVELS if mm_per_hour > level), "·")


def add_minutes(time, minutes):
    hours, mins = map(int, time.split(":"))
    total = (hours * 60 + mins + minutes) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def departure_windows(wet, steps):
    last = len(wet) - steps
    windows = []
    for i in range(last + 1):
        if any(wet[i:i + steps]):
            continue
        if windows and windows[-1][1] == i - 1:
            windows[-1][1] = i
        else:
            windows.append([i, i])
    return [(start, end, end == last) for start, end in windows]


def latest(times, end, open_ended):
    return f"{times[end]}+" if open_ended else times[end]


def summarize(times, rain):
    wet = [mm > DRY_MM_PER_HOUR for mm in rain]
    if not any(wet):
        return {"text": ""}

    steps = TRIP_MINUTES // STEP_MINUTES
    windows = departure_windows(wet, steps)
    current = windows[0] if windows and windows[0][0] == 0 else None
    upcoming = [w for w in windows if w is not current]
    following = upcoming[0] if upcoming else None

    lines = []
    verdicts = []

    if current:
        _, end, open_ended = current
        lines.append(f"→ {times[end]}")
        verdicts.append(
            f"Leave by {latest(times, end, open_ended)} to stay dry "
            f"(arrive {add_minutes(times[end], TRIP_MINUTES)})"
        )
    elif wet[0]:
        verdicts.append("Too wet to leave now")
    else:
        verdicts.append(f"Dry now, but not for {TRIP_MINUTES} minutes")

    if following:
        start, end, open_ended = following
        lines.append(f"{times[start]} →")
        verdicts.append(
            f"Next dry window: leave after {times[start]}, until {latest(times, end, open_ended)}"
        )
    else:
        if not current:
            lines.append(f">{times[-1]}")
        verdicts.append(f"No {'other ' if current else ''}{TRIP_MINUTES}-minute dry window before {times[-1]}")

    bars = "".join(bar(mm) for mm in rain)
    tooltip = "\n".join(
        [f"Rain at home or work, next 2 hours", f"<tt>{times[0]} {bars} {times[-1]}</tt>"] + verdicts
    )
    return {"text": LINE_GAP.join(lines), "tooltip": tooltip, "class": "dry" if current else "wet"}


def main():
    locations = read_locations()
    if not locations:
        print(json.dumps({"text": ""}))
        return

    try:
        forecasts = [forecast(lat, lon) for lat, lon in locations]
    except Exception:
        print(json.dumps({"text": ""}))
        return

    count = min(len(f) for f in forecasts)
    times = [forecasts[0][i][0] for i in range(count)]
    rain = [max(f[i][1] for f in forecasts) for i in range(count)]
    print(json.dumps(summarize(times, rain), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())

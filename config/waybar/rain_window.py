#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

LOCATIONS = os.path.expanduser("~/.config/rain-window/locations")
TRIP_MINUTES = 20
STEP_MINUTES = 5
DRY_MM_PER_HOUR = 0.1
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


def summarize(times, rain):
    wet = [mm > DRY_MM_PER_HOUR for mm in rain]
    if not any(wet):
        return {"text": ""}

    steps = TRIP_MINUTES // STEP_MINUTES
    start = next((i for i in range(len(wet) - steps + 1) if not any(wet[i:i + steps])), None)

    if start is None:
        text = f">{times[-1]}"
        verdict = f"No {TRIP_MINUTES}-minute dry window before {times[-1]}"
    elif start == 0:
        text = "now"
        verdict = f"Dry for at least {TRIP_MINUTES} minutes from now"
    else:
        text = times[start]
        verdict = f"Next {TRIP_MINUTES}-minute dry window starts at {times[start]}"

    bars = "".join(bar(mm) for mm in rain)
    tooltip = f"Rain at home or work, next 2 hours\n<tt>{times[0]} {bars} {times[-1]}</tt>\n{verdict}"
    return {"text": text, "tooltip": tooltip, "class": "wet" if wet[0] else "dry"}


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

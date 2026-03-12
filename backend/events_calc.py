"""Celestial event calculations for a given year.

Scans planetary positions day by day using Swiss Ephemeris, detecting:
- Stelliums: 4+ planets in the same zodiac sign
- Transits: Jupiter, Saturn, Rahu, Ketu changing signs
- Retrogrades: planets going retrograde / turning direct
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

try:
    import swisseph as swe  # type: ignore
except ModuleNotFoundError:
    from . import swe_ctypes as swe  # type: ignore

SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_jd(date: datetime) -> float:
    """Return Julian Day number for noon UT on *date*."""
    return swe.julday(date.year, date.month, date.day, 12.0, swe.GREG_CAL)


def _sidereal_lon(jd: float, planet_id: int) -> dict:
    """Return sidereal longitude, sign index, speed, and retrograde flag."""
    # Use sidereal flag – swisseph applies the ayanamsa internally
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0.0, 0.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    xx, _ = swe.calc_ut(jd, planet_id, flags)
    lon_sid = float(xx[0]) % 360.0
    speed = float(xx[3]) if len(xx) > 3 else 0.0
    return {
        "lon": lon_sid,
        "sign_idx": int(lon_sid / 30.0),
        "speed": speed,
        "retrograde": speed < 0,
    }


# ── Main function ─────────────────────────────────────────────────────────────

def calculate_events_for_year(year: int, ephe_path: str = "ephe") -> dict[str, Any]:
    """Scan *year* for major astrological events and return a JSON-serialisable dict."""

    try:
        swe.set_ephe_path(ephe_path)
    except Exception:
        pass  # use built-in ephemeris if path is wrong

    flags = swe.FLG_SWIEPH

    # Planets for conjunction / stellium detection (7 classical)
    CONJ_PLANETS = [
        ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS), ("Saturn", swe.SATURN),
    ]

    # Planets for retrograde detection
    RETRO_PLANET_NAMES = {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}

    # Planets for sign-transit detection (slow movers + nodes)
    TRANSIT_PLANET_NAMES = {"Jupiter", "Saturn", "Rahu", "Ketu"}

    stelliums: list[dict] = []
    transits: list[dict] = []
    retrogrades: list[dict] = []

    prev_state: dict[str, dict] = {}
    current_stellium: dict | None = None

    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 31)          # scan into next Jan to catch year-end events
    delta = timedelta(days=1)

    curr = start
    while curr <= end:
        jd = _get_jd(curr)
        date_str = curr.strftime("%Y-%m-%d")

        # ── 1. Gather daily positions ──────────────────────────────────────
        daily: dict[str, dict] = {}

        for pname, pid in CONJ_PLANETS:
            daily[pname] = _sidereal_lon(jd, pid)

        # Rahu (mean node) and Ketu (opposite)
        rahu_pos = _sidereal_lon(jd, swe.MEAN_NODE)
        daily["Rahu"] = rahu_pos
        ketu_lon = (rahu_pos["lon"] + 180.0) % 360.0
        daily["Ketu"] = {
            "lon": ketu_lon,
            "sign_idx": int(ketu_lon / 30.0),
            "speed": rahu_pos["speed"],
            "retrograde": True,  # nodes are always retrograde on average
        }

        # ── 2. Stellium detection ─────────────────────────────────────────
        sign_buckets: dict[int, list[str]] = {}
        for pname, pos in daily.items():
            si = pos["sign_idx"]
            sign_buckets.setdefault(si, []).append(pname)

        best_sign: int | None = None
        best_planets: list[str] = []
        for si, planets in sign_buckets.items():
            if len(planets) >= 4 and len(planets) > len(best_planets):
                best_sign = si
                best_planets = planets

        if best_sign is not None:
            if current_stellium is None:
                current_stellium = {
                    "start_date":   date_str,
                    "sign":         SIGN_NAMES[best_sign],
                    "planets":      list(best_planets),
                    "peak_date":    date_str,          # exact date when most planets together
                    "peak_planets": list(best_planets),
                }
            else:
                # Accumulate every planet seen over whole period
                current_stellium["planets"] = sorted(
                    set(current_stellium["planets"] + best_planets)
                )
                # Update peak if today has MORE simultaneous planets
                if len(best_planets) > len(current_stellium["peak_planets"]):
                    current_stellium["peak_date"]    = date_str
                    current_stellium["peak_planets"] = list(best_planets)
        else:
            if current_stellium is not None:
                prev_date = (curr - delta).strftime("%Y-%m-%d")
                current_stellium["end_date"] = prev_date
                if current_stellium["start_date"][:4] == str(year):
                    stelliums.append(current_stellium)
                current_stellium = None

        # ── 3. Transits & Retrogrades ─────────────────────────────────────
        for pname, pos in daily.items():
            if pname not in prev_state:
                prev_state[pname] = pos
                continue

            prev = prev_state[pname]

            # Sign ingress for slow movers
            if pname in TRANSIT_PLANET_NAMES and pos["sign_idx"] != prev["sign_idx"]:
                transits.append({
                    "date": date_str,
                    "planet": pname,
                    "from_sign": SIGN_NAMES[prev["sign_idx"]],
                    "to_sign": SIGN_NAMES[pos["sign_idx"]],
                })

            # Retrograde / Direct station
            if pname in RETRO_PLANET_NAMES:
                if not prev["retrograde"] and pos["retrograde"]:
                    retrogrades.append({
                        "date": date_str,
                        "planet": pname,
                        "type": "Retrograde",
                        "sign": SIGN_NAMES[pos["sign_idx"]],
                    })
                elif prev["retrograde"] and not pos["retrograde"]:
                    retrogrades.append({
                        "date": date_str,
                        "planet": pname,
                        "type": "Direct",
                        "sign": SIGN_NAMES[pos["sign_idx"]],
                    })

            prev_state[pname] = pos

        curr = curr + delta

    # Flush open stellium
    if current_stellium is not None and current_stellium["start_date"][:4] == str(year):
        current_stellium["end_date"] = end.strftime("%Y-%m-%d")
        stelliums.append(current_stellium)

    return {
        "year": year,
        "stelliums": stelliums,
        "transits": transits,
        "retrogrades": retrogrades,
    }

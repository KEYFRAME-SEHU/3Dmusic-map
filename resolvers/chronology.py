"""Chronology resolver: find a track's first official release date via MusicBrainz.

MusicBrainz is free and needs no key. It returns the earliest release date
for a recording. Returns (date_iso, day_offset, confidence, provenance).
The date is an approximation: the map recomputes daily, so a wrong date
gets corrected by the next run or by a curator.

MusicBrainz rate-limits to about 1 request per second and returns 503
when busy, so this retries with backoff.
"""
import time
import requests

MB_BASE = "https://musicbrainz.org/ws/2"
HEADERS = {"User-Agent": "3Dmusic-map/1.0 (https://keyframe-sehu.github.io/3Dmusic-map/)"}

def _days_from_origin(date_iso):
    from datetime import date
    y, m, d = [int(x) for x in date_iso.split("-")]
    origin = date(1974, 7, 6)
    return (date(y, m, d) - origin).days

def _norm_date(d):
    """Normalize a MusicBrainz date (YYYY, YYYY-MM, or YYYY-MM-DD) to YYYY-MM-DD."""
    if not d:
        return None
    if len(d) == 4:
        return d + "-07-01"  # year only: mid-year convention
    if len(d) == 7:
        return d + "-01"
    return d

def _search(artist, title):
    q = f'artist:"{artist}" AND recording:"{title}"'
    last_err = None
    for attempt in range(4):
        try:
            r = requests.get(
                MB_BASE + "/recording/",
                params={"query": q, "fmt": "json", "limit": 10},
                headers=HEADERS, timeout=20,
            )
            if r.status_code == 200:
                return r.json().get("recordings", [])
            last_err = "HTTP %s" % r.status_code
        except Exception as e:
            last_err = str(e)
        time.sleep(2 * (attempt + 1))
    raise RuntimeError("MusicBrainz lookup failed after retries: %s" % last_err)

def resolve_chronology(artist, title):
    """Return dict with date, day_offset, confidence, provenance."""
    try:
        recs = _search(artist, title)
    except Exception as e:
        return {"date": None, "day_offset": None, "confidence": "low (MusicBrainz lookup failed: %s)" % e,
                "provenance": "MusicBrainz (failed)"}
    if not recs:
        return {"date": None, "day_offset": None, "confidence": "low (no MusicBrainz match)",
                "provenance": "MusicBrainz (no match)"}
    # Earliest first-release-date across the top matches.
    # (Do not fall back to the releases array: it can hold promos and
    # mislabelled dates that predate the real first release.)
    best = None
    for rec in recs:
        d = _norm_date(rec.get("first-release-date"))
        if d and (best is None or d < best):
            best = d
    if not best:
        return {"date": None, "day_offset": None, "confidence": "low (MusicBrainz match has no date)",
                "provenance": "MusicBrainz (no date)"}
    return {"date": best, "day_offset": _days_from_origin(best),
            "confidence": "medium (MusicBrainz earliest release)",
            "provenance": "MusicBrainz"}

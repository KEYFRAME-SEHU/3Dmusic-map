"""Chronology resolver: find a track's first official release date via MusicBrainz.

MusicBrainz is free and needs no key. It returns the earliest release date
for a recording. Returns a dict with date, day_offset, confidence,
provenance, and the recording MBID (mbid) so the tempo resolver can use
AcousticBrainz without a second search.

The date is an approximation: the map recomputes daily, so a wrong date
gets corrected by the next run or by a curator.

Search strategy (in order), because artist names with punctuation
(e.g. Run-D.M.C., stored with a Unicode hyphen) defeat a single
exact-phrase query:
  1. Fielded exact-phrase search, filtered in Python by a
     punctuation-insensitive name match.
  2. Artist lookup by name, then recordings by that artist's MBID
     (arid) plus the title.
  3. Title-only search, filtered in Python by artist name.

MusicBrainz rate-limits to about 1 request per second and returns 503
when busy, so this waits between requests and retries with backoff.
"""
import re
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

def _norm_name(s):
    """Punctuation-insensitive name key: lowercase, keep only letters/digits.
    'Run-D.M.C.' (Unicode hyphen) and 'run dmc' both become 'rundmc'."""
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def _get(url, params, retries=6):
    """One MusicBrainz GET with backoff on 503/rate-limit. Returns parsed JSON or None.
    Retries up to 6 times; MusicBrainz rate-limits to ~1 req/sec and returns
    503 when busy, so the backoff grows (2s, 4s, 6s, 8s, 10s, 12s)."""
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                return r.json()
            last_err = "HTTP %s" % r.status_code
        except Exception as e:
            last_err = str(e)
        # MusicBrainz wants ~1 req/sec; back off harder on 503.
        time.sleep(2 * (attempt + 1))
    raise RuntimeError("MusicBrainz lookup failed after retries: %s" % last_err)

def _artist_name(rec):
    ac = rec.get("artist-credit") or []
    if ac:
        return (ac[0].get("artist") or {}).get("name", "")
    return ""

def _best_dated(recs, want_artist, want_title):
    """Earliest first-release-date among recordings whose normalized artist
    and title match. Returns (date, mbid) or (None, None)."""
    best = None
    best_mbid = None
    for rec in recs:
        if _norm_name(_artist_name(rec)) != _norm_name(want_artist):
            continue
        if _norm_name(rec.get("title")) != _norm_name(want_title):
            continue
        d = _norm_date(rec.get("first-release-date"))
        if d and (best is None or d < best):
            best = d
            best_mbid = rec.get("id")
    return best, best_mbid

def _search_recordings(query, limit=10):
    data = _get(MB_BASE + "/recording/", {"query": query, "fmt": "json", "limit": limit})
    return (data or {}).get("recordings", [])

def _find_artist_mbid(artist):
    """Look up an artist by name and return the top-scoring MBID, or None."""
    data = _get(MB_BASE + "/artist/", {"query": artist, "fmt": "json", "limit": 5})
    arts = (data or {}).get("artists", [])
    for a in arts:
        if _norm_name(a.get("name")) == _norm_name(artist):
            return a.get("id")
    return arts[0].get("id") if arts else None

def resolve_chronology(artist, title):
    """Return dict with date, day_offset, confidence, provenance, mbid."""
    try:
        # 1. Fielded exact-phrase search, filtered in Python.
        recs = _search_recordings('artist:"%s" AND recording:"%s"' % (artist, title))
        date_iso, mbid = _best_dated(recs, artist, title)
        if date_iso:
            return {"date": date_iso, "day_offset": _days_from_origin(date_iso),
                    "confidence": "medium (MusicBrainz earliest release)",
                    "provenance": "MusicBrainz", "mbid": mbid}
        time.sleep(1.2)  # stay under MusicBrainz's ~1 req/sec limit
        # 2. Artist lookup, then recordings by that artist's MBID + title.
        artist_mbid = _find_artist_mbid(artist)
        if artist_mbid:
            time.sleep(1.2)
            recs = _search_recordings('arid:%s AND recording:"%s"' % (artist_mbid, title))
            date_iso, mbid = _best_dated(recs, artist, title)
            if date_iso:
                return {"date": date_iso, "day_offset": _days_from_origin(date_iso),
                        "confidence": "medium (MusicBrainz earliest release)",
                        "provenance": "MusicBrainz", "mbid": mbid}
        time.sleep(1.2)
        # 3. Title-only search, filtered in Python by artist name.
        recs = _search_recordings('recording:"%s"' % title, limit=25)
        date_iso, mbid = _best_dated(recs, artist, title)
        if date_iso:
            return {"date": date_iso, "day_offset": _days_from_origin(date_iso),
                    "confidence": "medium (MusicBrainz earliest release)",
                    "provenance": "MusicBrainz", "mbid": mbid}
    except Exception as e:
        return {"date": None, "day_offset": None, "mbid": None,
                "confidence": "low (MusicBrainz lookup failed: %s)" % e,
                "provenance": "MusicBrainz (failed)"}
    return {"date": None, "day_offset": None, "mbid": None,
            "confidence": "low (no MusicBrainz match)",
            "provenance": "MusicBrainz (no match)"}

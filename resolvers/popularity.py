"""Popularity resolver: estimate a track's yearly reach (streams per year).

Two sources, in order:
1. Spotify popularity (0-100), when the repo's SPOTIFY_CLIENT_ID /
   SPOTIFY_CLIENT_SECRET secrets are set. Mapped to streams/yr on a log
   scale: streams = 10^(1.5 + popularity * 0.0775). That puts popularity 40
   at ~40,000 streams/yr (Z=0), popularity 20 at ~1,000, popularity 60 at
   ~1.4M, popularity 80 at ~50M. A documented approximation, not a count.
2. YouTube view counts via yt-dlp (no API key), as total views divided by
   the track's age in years. Rough yearly reach.

If neither source returns anything, the track is placed at Z=0 with a
low-confidence flag. The daily recompute and a curator correct it.
"""
import json
import os
import subprocess
import time
from datetime import date

import requests

def _spotify_token():
    cid = os.environ.get("SPOTIFY_CLIENT_ID")
    sec = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not cid or not sec:
        return None
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(cid, sec), timeout=20,
    )
    if r.status_code != 200:
        return None
    return r.json().get("access_token")

def _spotify_popularity(artist, title):
    token = _spotify_token()
    if not token:
        return None, None
    headers = {"Authorization": "Bearer " + token}
    try:
        r = requests.get(
            "https://api.spotify.com/v1/search",
            params={"q": f"track:{title} artist:{artist}", "type": "track", "limit": 1},
            headers=headers, timeout=20,
        )
        r.raise_for_status()
        items = r.json().get("tracks", {}).get("items", [])
        if not items:
            return None, None
        pop = items[0].get("popularity")
        if pop is None:
            return None, None
        streams = int(10 ** (1.5 + pop * 0.0775))
        return streams, f"Spotify popularity {pop}/100"
    except Exception:
        return None, None

def _youtube_views(artist, title):
    """Return the view count of the top YouTube result, or None.
    Retries because YouTube search via yt-dlp is flaky (rate limits)."""
    query = f"ytsearch1:{artist} {title}"
    for attempt in range(3):
        try:
            # --no-check-certificates: some environments (proxies, sandboxes) fail
            # TLS verification for YouTube. This is a public read of a view count.
            out = subprocess.run(
                ["yt-dlp", "--no-check-certificates", "--dump-json", "--no-playlist", query],
                capture_output=True, text=True, timeout=60,
            )
            if out.returncode != 0:
                time.sleep(2 * (attempt + 1))
                continue
            # yt-dlp can print warnings before the JSON; find the first line that parses.
            for line in out.stdout.splitlines():
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    info = json.loads(line)
                except Exception:
                    continue
                if info.get("view_count") is not None:
                    return info.get("view_count")
            return None
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None

def resolve_popularity(artist, title, date_iso=None):
    # 1. Spotify popularity, when credentials are set.
    streams, note = _spotify_popularity(artist, title)
    if streams is not None:
        return {"streams_per_year": streams,
                "confidence": "medium (Spotify popularity mapped to streams/yr; rough)",
                "provenance": note}
    # 2. YouTube views / age.
    views = _youtube_views(artist, title)
    if views is not None:
        age_years = 1.0
        if date_iso:
            try:
                y, m, d = [int(x) for x in date_iso.split("-")]
                age_years = max((date.today() - date(y, m, d)).days / 365.25, 1.0)
            except Exception:
                pass
        streams = int(views / age_years)
        return {"streams_per_year": streams,
                "confidence": "medium (YouTube views / age in years; rough yearly reach)",
                "provenance": f"YouTube via yt-dlp ({views:,} views over {age_years:.1f} years)"}
    return {"streams_per_year": None,
            "confidence": "low (no reach found)",
            "provenance": "Spotify and YouTube (no match)"}

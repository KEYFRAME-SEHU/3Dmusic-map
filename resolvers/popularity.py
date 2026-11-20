"""Popularity resolver: estimate a track's yearly reach (streams per year).

Source: YouTube view counts via yt-dlp (no API key), as total views
divided by the track's age in years. Rough yearly reach.

Note: the old Spotify popularity path was removed. Spotify removed the
`popularity` field from track responses for Development Mode apps in
Feb/Mar 2026, and Extended Quota (the only way to get it back) is only
granted to registered businesses with 250,000+ monthly active users, so
an individual project cannot get it back. The field is simply absent,
so the resolver now goes straight to YouTube.

The cultural-prominence composite (Wikipedia chart peaks, Wikipedia
pageviews, Rolling Stone 500) will replace this streams-only estimate
as the Z axis; until then, YouTube views/age is the reach signal.

If no source returns anything, the track is placed at Z=0 with a
low-confidence flag. The daily recompute and a curator correct it.
"""
import json
import subprocess
import sys
import time
from datetime import date

def _youtube_views(artist, title):
    """Return the view count of the top YouTube result, or None.
    Retries because YouTube search via yt-dlp is flaky (rate limits)."""
    query = f"ytsearch1:{artist} {title}"
    for attempt in range(3):
        try:
            # Run yt-dlp as a Python module (sys.executable -m yt_dlp) so it
            # works whether or not the yt-dlp binary is on PATH. It is
            # installed via resolvers/requirements.txt in both the venv
            # and the GitHub Action.
            # --no-check-certificates: some environments (proxies, sandboxes) fail
            # TLS verification for YouTube. This is a public read of a view count.
            out = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "--no-check-certificates", "--dump-json", "--no-playlist", query],
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
            "provenance": "YouTube (no match)"}

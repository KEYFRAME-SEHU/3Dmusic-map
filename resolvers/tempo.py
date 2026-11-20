"""Tempo resolver: find a track's BPM.

Primary source is Spotify audio features (tempo), which needs the repo's
SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET secrets. Without them, or when
Spotify has no match, the tempo is a flagged guess (the map's philosophy:
the guess is the unit, and the daily recompute plus a curator corrects it).
Returns (bpm, confidence, provenance).
"""
import os
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

def resolve_tempo(artist, title):
    token = _spotify_token()
    if not token:
        return {"bpm": None, "confidence": "low (no Spotify credentials; BPM is a guess)",
                "provenance": "none (Spotify credentials not set)"}
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
            return {"bpm": None, "confidence": "low (no Spotify match)",
                    "provenance": "Spotify (no match)"}
        tid = items[0]["id"]
        r2 = requests.get(
            f"https://api.spotify.com/v1/audio-features/{tid}",
            headers=headers, timeout=20,
        )
        r2.raise_for_status()
        tempo = r2.json().get("tempo")
        if tempo is None:
            return {"bpm": None, "confidence": "low (Spotify has no tempo for this track)",
                    "provenance": "Spotify (no tempo)"}
        return {"bpm": round(tempo), "confidence": "high (Spotify audio features)",
                "provenance": "Spotify"}
    except Exception as e:
        return {"bpm": None, "confidence": "low (Spotify lookup failed: %s)" % e,
                "provenance": "Spotify (failed)"}

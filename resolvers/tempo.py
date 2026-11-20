"""Tempo resolver: find a track's BPM.

Primary source is AcousticBrainz (free, no key): given a MusicBrainz
recording ID (MBID) from the chronology step, it returns the BPM from its
low-level analysis. This replaces the old Spotify audio-features path,
which is no longer available to Development Mode apps: Spotify removed
the audio-features endpoints for new/Development Mode apps on
27 Nov 2024 (HTTP 403), and Extended Quota is only granted to registered
businesses with 250,000+ monthly active users, so an individual project
cannot get it back.

If AcousticBrainz has no BPM for the recording, the tempo is a flagged
guess (the map's philosophy: the guess is the unit, and the daily
recompute plus a curator corrects it).
Returns a dict with bpm, confidence, provenance.
"""
import requests

AB_BASE = "https://acousticbrainz.org/api/v1"

def resolve_tempo(artist, title, mbid=None):
    if not mbid:
        return {"bpm": None,
                "confidence": "low (no MusicBrainz recording ID; BPM is a guess)",
                "provenance": "none (no MBID)"}
    try:
        r = requests.get(AB_BASE + "/" + mbid + "/low-level", timeout=20)
        if r.status_code == 404:
            return {"bpm": None,
                    "confidence": "low (AcousticBrainz has no analysis for this recording; BPM is a guess)",
                    "provenance": "AcousticBrainz (no data)"}
        r.raise_for_status()
        bpm = (r.json().get("rhythm") or {}).get("bpm")
        if bpm is None:
            return {"bpm": None,
                    "confidence": "low (AcousticBrainz has no BPM for this recording; BPM is a guess)",
                    "provenance": "AcousticBrainz (no BPM)"}
        return {"bpm": round(bpm),
                "confidence": "medium (AcousticBrainz)",
                "provenance": "AcousticBrainz"}
    except Exception as e:
        return {"bpm": None,
                "confidence": "low (AcousticBrainz lookup failed: %s; BPM is a guess)" % e,
                "provenance": "AcousticBrainz (failed)"}

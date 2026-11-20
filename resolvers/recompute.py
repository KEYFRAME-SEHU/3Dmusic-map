"""Cascade orchestrator: place one track on the map, one axis at a time.

Order (Julian, 2026-11-20): chronology first, then tempo (confined to the
first placement), then culture (confined to both prior placements).
Every axis is a guess; the daily recompute and a curator correct it.
If a resolver finds nothing, the track is still placed at the origin
for that axis with a low-confidence flag, so it appears on the map
instead of vanishing.

Daily mode (recompute_all) re-runs ONLY the culture axis. The date and
BPM are stable facts that do not change day to day, and the hand-trained
seed values are curator-checked, so they are never overwritten by the
resolvers. Only the prominence (streams, pageviews, relevance) moves daily.
"""
import json
import math
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chronology import resolve_chronology
from tempo import resolve_tempo
from popularity import resolve_popularity
from prominence import resolve_prominence

SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "snapshot-2026-11-20.json")

# 2D baseline projection (same as the SVG baseline, for the flat graph).
X_ORIGIN_PX, X_PX_PER_DAY = 960, 0.039
Y_ORIGIN_PX = 640
Y_SLOW = [(0, 1110), (60, 953), (90, 797), (120, 640)]
Y_FAST = [(120, 640), (140, 546), (175, 452), (250, 358), (500, 264), (1000, 170)]
Z_LOG_PX_PER_DECADE = 126

def _interp(table, v):
    for i in range(len(table) - 1):
        b0, y0 = table[i]
        b1, y1 = table[i + 1]
        if b0 <= v <= b1:
            return y0 + (v - b0) / (b1 - b0) * (y1 - y0)
    return table[0][1] if v < table[0][0] else table[-1][1]

def _y_px(bpm):
    return _interp(Y_SLOW if bpm <= 120 else Y_FAST, bpm)

def _z_pair(streams):
    # Z=0 is 40,000 streams/yr. Mainstream (more) moves toward (1370,230);
    # underground (fewer) moves toward (550,1050). One decade = 126 px along the diagonal.
    decades = math.log10(streams / 40000)
    # diagonal unit vector from origin (960,640) toward mainstream: (410,-410)/579.7
    ux, uy = 410 / 579.7, -410 / 579.7
    d = -decades * Z_LOG_PX_PER_DECADE  # negative decades (mainstream) move +d along the unit vector
    return [round(960 + d * ux, 1), round(640 + d * uy, 1)]

def place_track(artist, title):
    """Run the cascade and return the track dict (not yet saved)."""
    # 1. Chronology.
    chrono = resolve_chronology(artist, title)
    if chrono["date"] is None:
        chrono = {"date": date.today().isoformat(), "day_offset": (date.today() - date(1974, 7, 6)).days,
                  "confidence": "low (no date found; placed at today as a flagged guess)",
                  "provenance": "none (guess)"}
    # 2. Tempo, confined to the chronology placement. AcousticBrainz uses
    # the MusicBrainz recording ID found in step 1.
    tempo = resolve_tempo(artist, title, mbid=chrono.get("mbid"))
    if tempo["bpm"] is None:
        tempo = {"bpm": 120, "confidence": "low (no BPM found; placed at the 120 origin as a flagged guess)",
                 "provenance": "none (guess)"}
    # 3. Culture, confined to both prior placements. First the YouTube
    # reach (a Relevance input), then the prominence composite, which
    # replaces the streams-only Z with commercial reach + cultural
    # influence + current relevance. The composite maps back to an
    # equivalent streams/yr on the existing log scale so the viewer
    # and the 2D baseline keep working unchanged.
    pop = resolve_popularity(artist, title, chrono["date"])
    yt_streams = pop["streams_per_year"]
    if yt_streams is None:
        yt_streams = 40000
        pop = {"streams_per_year": 40000,
               "confidence": "low (no reach found; placed at Z=0 as a flagged guess)",
               "provenance": "none (guess)"}
    prom = resolve_prominence(artist, title, mbid=chrono.get("mbid"),
                              streams_per_year=yt_streams)
    streams = prom["streams_per_year"]
    pop_confidence = ("prominence %.2f (commercial %.2f, influence %.2f, relevance %.2f; %s)"
                      % (prom["prominence"], prom["commercial"], prom["influence"],
                         prom["relevance"], prom["breakdown"]))
    x_px = round(960 + chrono["day_offset"] * X_PX_PER_DAY, 1)
    y_px = round(_y_px(tempo["bpm"]), 1)
    z = _z_pair(streams)
    screen = [round(x_px + (z[0] - 960), 1), round(y_px + (z[1] - 640), 1)]
    return {
        "artist": artist, "title": title,
        "date": chrono["date"], "day_offset": chrono["day_offset"],
        "bpm": tempo["bpm"],
        "mbid": chrono.get("mbid"),
        "streams_per_year": streams,
        "popularity": f"~{streams:,} streams/yr equivalent (cultural prominence {prom['prominence']:.2f}; {prom['breakdown']})",
        "confidence": f"chrono: {chrono['confidence']}; tempo: {tempo['confidence']}; culture: {pop_confidence}",
        "commercial": prom["commercial"], "influence": prom["influence"],
        "relevance": prom["relevance"], "prominence": prom["prominence"],
        "x_px": x_px, "y_px": y_px, "z": z, "screen": screen,
    }

def add_to_snapshot(track):
    with open(SNAPSHOT) as f:
        d = json.load(f)
    # Do not add an exact duplicate.
    for t in d["tracks"]:
        if t["artist"].lower() == track["artist"].lower() and t["title"].lower() == track["title"].lower():
            return d, False
    track["n"] = len(d["tracks"]) + 1
    d["tracks"].append(track)
    d["snapshot_date"] = date.today().isoformat()
    with open(SNAPSHOT, "w") as f:
        json.dump(d, f, indent=2)
    return d, True

def recompute_all():
    """Daily mode: re-run ONLY the culture axis for every track in the snapshot.
    The date and BPM are stable facts (a song's first release date and its
    tempo do not change), and the hand-trained seed values are
    curator-checked, so they are never overwritten by the resolvers.
    Only the prominence (which depends on current streams, pageviews, and
    relevance) is recomputed daily. The MBID is looked up fresh so the
    RS500 check has an ID to match, but the stored date is kept."""
    with open(SNAPSHOT) as f:
        d = json.load(f)
    for t in d["tracks"]:
        # MBID only (for the RS500 check); the stored date and BPM are kept.
        mbid = t.get("mbid")
        if not mbid:
            try:
                chrono = resolve_chronology(t["artist"], t["title"])
                mbid = chrono.get("mbid")
            except Exception:
                mbid = None
        # YouTube reach (a Relevance input), using the stored date for the age.
        pop = resolve_popularity(t["artist"], t["title"], t["date"])
        yt_streams = pop["streams_per_year"] or 40000
        prom = resolve_prominence(t["artist"], t["title"], mbid=mbid,
                                  streams_per_year=yt_streams)
        streams = prom["streams_per_year"]
        pop_confidence = ("prominence %.2f (commercial %.2f, influence %.2f, relevance %.2f; %s)"
                          % (prom["prominence"], prom["commercial"], prom["influence"],
                             prom["relevance"], prom["breakdown"]))
        z = _z_pair(streams)
        t["streams_per_year"] = streams
        t["popularity"] = f"~{streams:,} streams/yr equivalent (cultural prominence {prom['prominence']:.2f}; {prom['breakdown']})"
        t["confidence"] = f"chrono: {t.get('confidence','').split(';')[0] if ';' in t.get('confidence','') else 'hand-trained'}; tempo: hand-trained; culture: {pop_confidence}"
        t["commercial"] = prom["commercial"]
        t["influence"] = prom["influence"]
        t["relevance"] = prom["relevance"]
        t["prominence"] = prom["prominence"]
        t["z"] = z
        t["screen"] = [round(t["x_px"] + (z[0] - 960), 1), round(t["y_px"] + (z[1] - 640), 1)]
        if mbid:
            t["mbid"] = mbid
    d["snapshot_date"] = date.today().isoformat()
    with open(SNAPSHOT, "w") as f:
        json.dump(d, f, indent=2)
    return len(d["tracks"])

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] in ("--daily", "--date"):
        n = recompute_all()
        print(json.dumps({"recomputed": n}))
    else:
        artist, title = sys.argv[1], sys.argv[2]
        track = place_track(artist, title)
        d, added = add_to_snapshot(track)
        print(json.dumps({"added": added, "track": track}, indent=2))

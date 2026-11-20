# 3Dmusic-map

Every recorded song is one point in a 3D landscape you fly through and listen to. Songs move daily and leave glowing trails.

## The axes

- **X = Chronology**, in days from first official release date. Origin (0,0,0) is July 6, 1974, the beginning of disco ("Rock the Boat," first disco #1). Pre-disco is negative X. The leading edge is always today.
- **Y = Tempo**, plain BPM, 0 to 1000. Origin is 120 BPM. The floor is the base plane at 0 BPM.
- **Z = Cultural prominence**, mainstream (front) to underground (deep). Not streams alone: a weighted composite of commercial reach, cultural influence, and current relevance, each scored 0-1 and combined as Prominence = 0.40 x Commercial + 0.30 x Influence + 0.30 x Relevance. Z=0 is the middle of the log scale, about 40,000 streams a year: a song with a real audience of thousands, known in its world, unknown outside it. A 1984 landmark can sit mainstream of the origin even with modest current streams, because its chart peak and influence count.

## The system

The guess is the unit of the map, not the fact. The system places each track in a cascade, one axis at a time, in order:

1. **Chronology first.** Find the first release date (MusicBrainz, then web search). An approximation; it recalculates tomorrow.
2. **Tempo second, confined to the chronology placement.** Measure the BPM with AcousticBrainz (free, no key), using the MusicBrainz recording ID from step 1. One integer; a simple estimation that will change tomorrow.
3. **Culture last, confined to both prior placements.** Estimate cultural prominence from commercial reach (Wikipedia peak chart position and certifications), cultural influence (Rolling Stone 500 rank), and current relevance (Wikipedia pageviews and YouTube views per year). Era-normalized. Estimate, drop it in; the axis resets the next day and recomputes all tracks.

Every day all tracks move dynamically. The daily engine re-runs the three resolvers for every track and saves one snapshot per day. Trails come from the snapshots.

## The data

- `data/snapshot-2026-11-20.json` — the first hand-trained snapshot: 20 tracks, each with its date, BPM, popularity estimate, axis pixels, screen position, and confidence/provenance.
- `docs/layout-spec.md` — the full layout spec (V7).
- `music-map-10-tracks.svg` / `.png` — graph 1, tracks 1-10, numbers on the dots, key on the side.
- `music-map-20-tracks.svg` / `.png` — graph 2, tracks 1-20, numbers on the dots, key on the side.

## The site

GitHub Pages serves `index.html`, a real 3D viewer (Three.js). Drag to orbit, scroll to zoom, right-drag to pan. Click a numbered point to see its track. The three planes are drawn in color: blue Chronology, red Tempo, green Popularity. The flat 2D graph is still in the repo (`music-map-20-tracks.png`) and linked from the page.

No paid APIs. MusicBrainz, AcousticBrainz, Wikipedia, and Wikimedia are free with no key. YouTube is read from the public page (yt-dlp).

Spotify is no longer used. Spotify removed the audio-features endpoints for Development Mode apps on Nov 27, 2024, and removed the `popularity` field for Development Mode apps in Feb/Mar 2026. Extended Quota (the only way to get them back) is granted only to registered businesses with 250,000+ monthly active users, so an individual project cannot get it. The resolvers were rewired to free sources instead; no Spotify secrets are needed.

## Add a track (user input)

Anyone can add a track from the site, no sign-in. There is a form on the page: type the track name and the artist, click "Map this track." The cascade runs right in the browser, instantly: MusicBrainz finds the date (free, no key), AcousticBrainz finds the BPM when it has the track. The reach is a flagged guess at Z=0 for now; the daily update refines it. The point appears on the map immediately and is saved in that browser, so it stays on your map.

The full cascade runs in GitHub Actions for tracks in the snapshot. The resolvers live in `resolvers/`:
- `chronology.py` — MusicBrainz earliest release date (free, no key). Handles artist names with punctuation (e.g. Run-D.M.C.) by normalizing names and falling back from the exact-phrase search to an artist-MBID search to a title-only search.
- `tempo.py` — AcousticBrainz BPM (free, no key), using the MusicBrainz recording ID from the chronology step.
- `popularity.py` — YouTube views per year via yt-dlp (no key).
- `prominence.py` — the cultural-prominence composite: Wikipedia peak chart position and certifications (commercial), Rolling Stone 500 rank via MusicBrainz (influence), Wikipedia pageviews and YouTube reach (relevance). Maps the composite back to an equivalent streams/yr on the existing log scale.
- `recompute.py` — the cascade orchestrator. `python resolvers/recompute.py "Artist" "Title"` places one track; `python resolvers/recompute.py --daily` re-runs every track.
- `requirements.txt` — `requests`, `yt-dlp`.

No secrets are needed. The daily workflow (`.github/workflows/daily.yml`, 12:00 UTC) needs no credentials.

## Status

Hand-training first, then scale up. 20 tracks mapped by hand (Nov 20, 2026) and curator-checked: 9 of 10 passed as-is in the first set; one correction (Mike Love, Babylon Control, whose 13M-view YouTube video moved it ~200 px from deep underground to mainstream of the origin). The 3D viewer is live. The user-input form and the full-cascade resolvers are built; the daily engine (`.github/workflows/daily.yml`, 12:00 UTC) re-runs every track once a day.

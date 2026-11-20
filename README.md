# 3Dmusic-map

Every recorded song is one point in a 3D landscape you fly through and listen to. Songs move daily and leave glowing trails.

## The axes

- **X = Chronology**, in days from first official release date. Origin (0,0,0) is July 6, 1974, the beginning of disco ("Rock the Boat," first disco #1). Pre-disco is negative X. The leading edge is always today.
- **Y = Tempo**, plain BPM, 0 to 1000. Origin is 120 BPM. The floor is the base plane at 0 BPM.
- **Z = Popularity**, mainstream (front) to underground (deep), era-normalized reach. Z=0 is the middle of the log reach scale, about 40,000 streams a year: a song with a real audience of thousands, known in its world, unknown outside it.

## The system

The guess is the unit of the map, not the fact. The system places each track in a cascade, one axis at a time, in order:

1. **Chronology first.** Find the first release date (MusicBrainz, then web search). An approximation; it recalculates tomorrow.
2. **Tempo second, confined to the chronology placement.** Measure the BPM (audio analysis or Spotify). One integer; a simple estimation that will change tomorrow.
3. **Culture last, confined to both prior placements.** Look up the ISRC, check the charts, and check YouTube, because mainstream appeal is cultural appeal, not only sales. Era-normalized. Estimate, drop it in; the axis resets the next day and recomputes all tracks.

Every day all tracks move dynamically. The daily engine re-runs the three resolvers for every track and saves one snapshot per day. Trails come from the snapshots.

## The data

- `data/snapshot-2026-11-20.json` — the first hand-trained snapshot: 20 tracks, each with its date, BPM, popularity estimate, axis pixels, screen position, and confidence/provenance.
- `docs/layout-spec.md` — the full layout spec (V7).
- `music-map-10-tracks.svg` / `.png` — graph 1, tracks 1-10, numbers on the dots, key on the side.
- `music-map-20-tracks.svg` / `.png` — graph 2, tracks 1-20, numbers on the dots, key on the side.

## The site

GitHub Pages serves `index.html`, a real 3D viewer (Three.js). Drag to orbit, scroll to zoom, right-drag to pan. Click a numbered point to see its track. The three planes are drawn in color: blue Chronology, red Tempo, green Popularity. The flat 2D graph is still in the repo (`music-map-20-tracks.png`) and linked from the page.

No paid APIs: MusicBrainz is free, Spotify has a free developer app, YouTube is read from the public page (yt-dlp) for v1.

## Add a track (user input)

Anyone can add a track from the site, no sign-in. There is a form on the page: type the track name and the artist, click "Map this track." The cascade runs right in the browser, instantly: MusicBrainz finds the date (free, no key), AcousticBrainz finds the BPM when it has the track. The reach is a flagged guess at Z=0 for now; the daily update refines it. The point appears on the map immediately and is saved in that browser, so it stays on your map.

The full Spotify cascade (accurate BPM and reach) still runs in the GitHub Actions for tracks in the snapshot. The resolvers live in `resolvers/`:
- `chronology.py` — MusicBrainz earliest release date (free, no key).
- `tempo.py` — Spotify audio features tempo (needs `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` repo secrets).
- `popularity.py` — Spotify popularity mapped to streams/yr, falling back to YouTube views / age via yt-dlp.
- `recompute.py` — the cascade orchestrator. `python resolvers/recompute.py "Artist" "Title"` places one track; `python resolvers/recompute.py --daily` re-runs every track.
- `requirements.txt` — `requests`, `yt-dlp`.

Set the Spotify secrets under the repo's Settings, then Secrets and variables, then Actions. Do not put them in any file.

## Status

Hand-training first, then scale up. 20 tracks mapped by hand (Nov 20, 2026) and curator-checked: 9 of 10 passed as-is in the first set; one correction (Mike Love, Babylon Control, whose 13M-view YouTube video moved it ~200 px from deep underground to mainstream of the origin). The 3D viewer is live. The user-input form and the full-cascade resolvers are built; the daily engine (`.github/workflows/daily.yml`, 12:00 UTC) re-runs every track once a day.

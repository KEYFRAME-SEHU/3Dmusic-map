# How to upload 3Dmusic-map to GitHub

You upload this yourself. No one else needs GitHub access. The files are in this folder.

## What to upload

Upload everything in this folder **except** the `.venv` folder (that is just the local Python tools, not part of the repo).

The files:
- `README.md`
- `index.html` (the GitHub Pages site)
- `data/snapshot-2026-11-20.json` (the 20 tracks)
- `docs/layout-spec.md` (the full layout spec)
- `music-map-10-tracks.svg` and `music-map-10-tracks.png` (graph 1)
- `music-map-20-tracks.svg` and `music-map-20-tracks.png` (graph 2)
- `.github/workflows/daily.yml` (the daily recompute job, skeleton)

## Method 1: GitHub web UI (easiest, no command line)

1. Go to github.com and sign in.
2. Click the `+` at the top right, then `New repository`.
3. Repository name: `3Dmusic-map`. Owner: `KEYFRAME-SEHU`. Leave it Public. Click `Create repository`.
4. On the new empty repo page, click `uploading an existing file`.
5. Drag in all the files above (except `.venv`). You can drag folders too; the web UI keeps the folder structure.
6. Click `Commit changes`.

## Method 2: Git command line

1. Create the empty repo on GitHub as in Method 1, steps 1-3.
2. On your own computer, in a terminal:
   ```
   git clone https://github.com/KEYFRAME-SEHU/3Dmusic-map.git
   cd 3Dmusic-map
   ```
3. Copy all the files above (except `.venv`) into that folder.
4. Then:
   ```
   git add .
   git commit -m "First commit: 20 hand-trained tracks, Pages site, daily workflow skeleton"
   git push
   ```

## Turn on GitHub Pages (so the site is live)

1. On the repo page, go to `Settings`, then `Pages` (in the left sidebar).
2. Under `Build and deployment`, set Source to `Deploy from a branch`.
3. Set Branch to `main` and Folder to `/ (root)`. Click `Save`.
4. The site will be live at `https://keyframe-sehu.github.io/3Dmusic-map/` after a minute or two.

## Next steps (for later, not now)

- The daily workflow (`.github/workflows/daily.yml`) is a skeleton. It runs when the resolver scripts land.
- The Spotify developer app credentials go in the repo as Secrets (`Settings`, then `Secrets and variables`, then `Actions`): `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`. Do not put them in any file.
- YouTube needs no key for v1 (yt-dlp reads the public page).

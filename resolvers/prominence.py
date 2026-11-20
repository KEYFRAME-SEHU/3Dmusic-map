"""Cultural prominence resolver: the Z (culture) axis as a composite.

Z is NOT streams alone. It is "estimated cultural prominence, informed by
commercial reach, cultural influence, and current relevance" (Julian,
2026-11-20). Each component is a 0-1 score built from free, no-key
signals, combined as:

    Prominence = 0.40 * Commercial + 0.30 * Influence + 0.30 * Relevance

Signals (all free, no key unless noted):
  Commercial:
    - Wikipedia peak chart position (Hot 100, UK, genre charts, etc.),
      parsed from the song article's chart table via the MediaWiki API.
      Bounded 1-100, so it is the most era-robust number: a #1 is a #1
      in 1964 and in 2024. Score = (101 - peak) / 100. No chart = 0.
    - Certification level (from the same Wikipedia article's
      Certifications table): none=0, Silver=0.25, Gold=0.5,
      Platinum=0.75, multi-Platinum/Diamond=1.0.
  Influence:
    - Rolling Stone 500 Greatest Songs rank (MusicBrainz Series,
      cached to a local file because the list is static). Score =
      (501 - rank) / 500. Absent = 0. Sparse by design: only 500 songs
      are in the canon, so most tracks score 0 here and the composite
      leans on Commercial and Relevance for them.
  Relevance:
    - Wikipedia pageviews, trailing 12 months, human only (Wikimedia
      Pageviews API, no key). Log scale, capped.
    - YouTube views per year (from popularity.py, already in the stack).

The composite is mapped back to an equivalent streams-per-year on the
existing log scale so the 3D viewer and the 2D baseline keep working
unchanged: Z=0 stays at ~40,000 streams/yr, which is Prominence ~0.5.
Mapping: log10(streams) = 4.6 + (Prominence - 0.5) * 6, so Prominence 0
-> ~40 streams/yr (deep underground) and Prominence 1 -> ~40M/yr
(mainstream). This is a documented anchor, not a measurement.

Each component and the composite are stored on the track so the map can
show WHY a song is prominent, not just how much.

Caveats (from the research): chart and canon lists skew rock/US/UK and
English-language; missing data is coded as 0 for sparse binary flags
(RS500 absent) but a missing chart peak for a song that never charted
is genuinely 0, not "unknown". Wikipedia is a transcription: the chart
table can render a peak plus a footnote (e.g. 11 + footnote = "111"),
so footnotes are stripped before parsing the number.
"""
import json
import math
import os
import re
import time
from datetime import date, timedelta

import requests

H = {"User-Agent": "3Dmusic-map/1.0 (https://keyframe-sehu.github.io/3Dmusic-map/)"}
RS500_SERIES = "355b26c9-001e-4728-852e-82b4379adb82"
RS500_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rs500.json")
RS500_NAMES_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rs500_names.json")

# ---------------------------------------------------------------- Wikipedia
def _wiki_search(artist, title):
    """Find the song article title on Wikipedia. Returns the title or None.
    Scores hits by how well the article title matches the requested song
    title, so a search for 'I Feel Love' does not return 'Love to Love
    You Baby' just because both contain 'Love'."""
    def norm(s):
        return re.sub(r'[^a-z0-9]', '', (s or '').lower())
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search",
                    "srsearch": "%s %s song" % (artist, title),
                    "srlimit": 5, "format": "json"},
            headers=H, timeout=20,
        )
        if r.status_code != 200:
            return None
        hits = r.json().get("query", {}).get("search", [])
        target = norm(title)
        best = None
        best_score = -1
        for hit in hits:
            t = hit.get("title", "")
            # Strip the "(... song)" disambiguation for matching.
            base = re.sub(r'\s*\([^)]*\)\s*$', '', t)
            nt = norm(base)
            if nt == target:
                score = 3
            elif target in nt or nt in target:
                score = 2
            elif "song" in t.lower():
                score = 1
            else:
                score = 0
            if score > best_score:
                best_score = score
                best = t
        return best if best_score > 0 else None
    except Exception:
        return None

def _wiki_wikitext(page_title):
    """Fetch an article's wikitext. Returns the text or ''."""
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "parse", "page": page_title,
                    "prop": "wikitext", "format": "json"},
            headers=H, timeout=20,
        )
        if r.status_code != 200:
            return ""
        return r.json().get("parse", {}).get("wikitext", {}).get("*", "")
    except Exception:
        return ""

def _strip_tags(s):
    """Remove HTML/ref/sup tags and templates, leaving plain text."""
    s = re.sub(r'<ref[^>]*>.*?</ref>', '', s, flags=re.S)
    s = re.sub(r'<ref[^>]*/>', '', s)
    s = re.sub(r'<sup[^>]*>.*?</sup>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'\{\{[^}]*\}\}', '', s)
    s = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', s)
    s = re.sub(r'\[\[([^\]]*)\]\]', r'\1', s)
    s = s.replace("''", "")
    return s.strip()

def _chart_section(wt):
    """Return the wikitext of the chart section (Weekly charts / Chart positions)."""
    m = re.search(r'==\s*(Weekly charts|Chart positions|Charts)\s*==', wt, re.I)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r'\n==[^=]', wt[start:])
    end = start + nxt.start() if nxt else len(wt)
    return wt[start:end]

def _clean_chart_section(sec):
    """Strip table cell attributes (scope, align, colspan, rowspan, style,
    class) that would otherwise become bogus 'cells' when splitting on '|',
    then strip all remaining markup. Handles both '|' data cells and '!'
    header cells."""
    # Remove attribute assignments attached to cell separators, e.g.
    # | scope="row" | US Billboard ... | align="center" | 6
    # ! scope="row" | US Billboard Hot 100
    sec = re.sub(r'[\|!]\s*(?:scope|align|colspan|rowspan|style|class|bgcolor)\s*=\s*"[^"]*"', '|', sec)
    sec = re.sub(r'[\|!]\s*(?:scope|align|colspan|rowspan|style|class|bgcolor)\s*=\s*[^\s|!]+', '|', sec)
    return _strip_tags(sec)

def _singlechart_peaks(wt):
    """Parse {{single chart|CHART|PEAK|...}} templates, the other common
    chart-table format. Returns a list of (peak, chart_name)."""
    out = []
    # Chart code -> readable name (the most common codes).
    names = {
        "billboardhot100": "US Billboard Hot 100",
        "billboarddanceclubplay": "US Billboard Dance Club Songs",
        "billboardrandbhiphop": "US Billboard Hot R&B/Hip-Hop Songs",
        "billboardrandb": "US Billboard Hot R&B Songs",
        "billboardadultcontemporary": "US Billboard Adult Contemporary",
        "billboardmainstreamrock": "US Billboard Mainstream Rock",
        "billboardalternativesongs": "US Billboard Alternative Songs",
        "uk": "UK Singles (OCC)",
        "ukchart": "UK Singles (OCC)",
        "canada": "Canada Top Singles (RPM)",
        "australia": "Australia (ARIA)",
        "germany": "Germany (GfK)",
        "france": "France (SNEP)",
        "netherlands": "Netherlands (Single Top 100)",
        "belgiumflanders": "Belgium (Ultratop 50 Flanders)",
        "belgiumwallonia": "Belgium (Ultratop 50 Wallonia)",
        "ireland": "Ireland (IRMA)",
        "newzealand": "New Zealand (Recorded Music NZ)",
        "spain": "Spain (PROMUSICAE)",
        "italy": "Italy (FIMI)",
        "switzerland": "Switzerland (Schweizer Hitparade)",
        "austria": "Austria (O3 Austria Top 40)",
        "sweden": "Sweden (Sverigetopplistan)",
        "norway": "Norway (VG-lista)",
        "denmark": "Denmark (Tracklisten)",
        "finland": "Finland (Suomen virallinen lista)",
    }
    for m in re.finditer(r'\{\{\s*single chart\s*\|\s*([^|}]+)\s*\|\s*(\d{1,3})\b', wt, re.I):
        code = m.group(1).strip().lower()
        peak = int(m.group(2))
        if peak < 1 or peak > 500:
            continue
        chart = names.get(code, code)
        out.append((peak, chart))
    return out

def get_chart_peak(artist, title):
    """Best (lowest) peak chart position across all charts in the article.
    Returns (peak, chart_name) or (None, None). Prefers the main national
    singles chart (Hot 100, UK Singles) over a genre/indie chart."""
    page = _wiki_search(artist, title)
    if not page:
        return None, None
    wt = _wiki_wikitext(page)
    # 1. Singlechart templates (common format).
    peaks = _singlechart_peaks(wt)
    # 2. Wikitable rows in the chart section.
    sec = _chart_section(wt)
    if sec:
        sec = _clean_chart_section(sec)
        for row in re.split(r'\|\-', sec):
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if len(cells) < 2:
                continue
            chart = cells[0]
            if not chart or chart.lower().startswith("chart"):
                continue
            if "album" in chart.lower():
                continue
            if "year-end" in chart.lower() or "decade" in chart.lower():
                continue
            # Skip template fragments that survived cleaning.
            if chart.startswith("{{") or chart.startswith("!"):
                continue
            peak = None
            for cell in cells[1:]:
                m = re.search(r'\b(\d{1,3})\b', cell)
                if m:
                    peak = int(m.group(1))
                    break
            if peak is None or peak < 1 or peak > 500:
                continue
            peaks.append((peak, chart))
    if not peaks:
        # Some articles put the peak in prose ("rose to No. 11 on ...").
        m = re.search(r'(?:No\.|number|peaked at)\s*(\d{1,3})\s+on', wt, re.I)
        if m:
            return int(m.group(1)), "Wikipedia prose"
        return None, None
    def _rank(chart):
        c = chart.lower()
        if "hot 100" in c:
            return 0
        if "uk singles" in c or "uk top 40" in c:
            return 1
        if "canada" in c or "australia" in c or "germany" in c or "france" in c:
            return 2
        if "indie" in c or "dance" in c or "soul" in c or "r&b" in c or "hip-hop" in c or "rock" in c:
            return 4
        return 3
    # Prefer the main chart; among equal preference, take the lowest peak.
    peaks.sort(key=lambda p: (_rank(p[1]), p[0]))
    return peaks[0]

def get_certification_level(artist, title):
    """Certification level from the article's Certifications table.
    Returns 0.0 (none) to 1.0 (Diamond / multi-Platinum)."""
    page = _wiki_search(artist, title)
    if not page:
        return 0.0
    wt = _wiki_wikitext(page)
    m = re.search(r'==\s*Certifications\s*==', wt, re.I)
    if not m:
        return 0.0
    sec = wt[m.end():m.end() + 4000]
    text = _strip_tags(sec).lower()
    if "diamond" in text:
        return 1.0
    # Count platinum mentions (multi-platinum counts higher).
    plat = len(re.findall(r'platinum', text))
    if plat >= 2:
        return 0.9
    if plat == 1:
        return 0.75
    if "gold" in text:
        return 0.5
    if "silver" in text:
        return 0.25
    return 0.0

def get_pageviews(artist, title):
    """Mean monthly Wikipedia pageviews (human only) over the trailing 12 months.
    Returns the mean, or None."""
    page = _wiki_search(artist, title)
    if not page:
        return None
    end = date.today()
    start = end - timedelta(days=365)
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
           "en.wikipedia/all-access/user/%s/monthly/%s/%s"
           % (page.replace(" ", "_"), start.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
    try:
        r = requests.get(url, headers=H, timeout=20)
        if r.status_code != 200:
            return None
        views = [it.get("views", 0) for it in r.json().get("items", [])]
        if not views:
            return None
        return sum(views) / len(views)
    except Exception:
        return None

# ---------------------------------------------------------------- RS500
def _load_rs500():
    """Return {recording_mbid: rank} from the local cache.
    The list is static (2021 edition, rev. 2024), so it is cached in the
    repo as rs500.json (built once from the MusicBrainz series page,
    which lists the 500 recordings in rank order). Returns {} if the
    cache is missing; the fetch is not retried at runtime because the
    MusicBrainz API browse endpoint does not expose series contents."""
    if os.path.exists(RS500_CACHE):
        try:
            with open(RS500_CACHE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def get_rs500_rank(mbid, artist=None, title=None):
    """Rolling Stone 500 rank (1-500) for a recording, or None.
    Tries the recording MBID first (exact), then falls back to a
    normalized artist+title match, because the chronology resolver's
    MBID is often a different release/remaster of the same song than
    the one the RS500 series links to."""
    if mbid:
        rank = _load_rs500().get(mbid)
        if rank:
            return rank
    if artist and title:
        try:
            with open(RS500_NAMES_CACHE) as f:
                names = json.load(f)
        except Exception:
            return None
        key = re.sub(r'[^a-z0-9]', '', (artist or '').lower()) + '|' + re.sub(r'[^a-z0-9]', '', (title or '').lower())
        return names.get(key)
    return None

# ---------------------------------------------------------------- Covers
# Cover count via SecondHandSongs was dropped: the API returns 403 for
# automated access. A MusicBrainz work-recording count is the planned
# replacement (no new dependency), but it adds two rate-limited
# MusicBrainz requests per track, so it is deferred to a later pass.
# Influence is RS500-only for now; the composite weights below account
# for that sparsity (Influence 0.30, not 0.35).

# ---------------------------------------------------------------- Composite
def _log_scale(value, cap_log):
    """Map a count to 0-1 on a log scale: log10(1+value) / cap_log, capped at 1."""
    if value is None or value <= 0:
        return 0.0
    return min(math.log10(1 + value) / cap_log, 1.0)

def resolve_prominence(artist, title, mbid=None, streams_per_year=None):
    """Compute the cultural-prominence composite for one track.
    Returns a dict with commercial, influence, relevance, prominence (0-1),
    the equivalent streams_per_year on the existing log scale, and a
    human-readable breakdown."""
    # Commercial: chart peak (bounded, era-robust) + certification level.
    peak, chart_name = get_chart_peak(artist, title)
    peak_score = (101 - peak) / 100.0 if peak else 0.0
    cert = get_certification_level(artist, title)
    commercial = 0.7 * peak_score + 0.3 * cert
    # Influence: RS500 rank only (see note above; cover count deferred).
    rank = get_rs500_rank(mbid, artist, title)
    influence = (501 - rank) / 500.0 if rank else 0.0
    # Relevance: pageviews (trailing 12 months) + YouTube-derived reach.
    views = get_pageviews(artist, title)
    pv_score = _log_scale(views, 6.0)  # log10(1M)=6
    yt_score = _log_scale(streams_per_year, 7.0) if streams_per_year else 0.0
    relevance = 0.5 * pv_score + 0.5 * yt_score
    prominence = 0.40 * commercial + 0.30 * influence + 0.30 * relevance
    # Map the composite back to the existing log scale (Z=0 at 40,000 streams/yr,
    # which is Prominence ~0.5): log10(streams) = 4.6 + (Prominence - 0.5) * 6.
    equiv_streams = int(10 ** (4.6 + (prominence - 0.5) * 6))
    parts = []
    if peak:
        parts.append("chart peak #%d (%s)" % (peak, chart_name or ""))
    if rank:
        parts.append("RS500 #%d" % rank)
    if views:
        parts.append("~%d Wikipedia views/mo" % views)
    return {
        "commercial": round(commercial, 3),
        "influence": round(influence, 3),
        "relevance": round(relevance, 3),
        "prominence": round(prominence, 3),
        "streams_per_year": equiv_streams,
        "breakdown": "; ".join(parts) if parts else "no chart/canon/pageview signal found",
    }

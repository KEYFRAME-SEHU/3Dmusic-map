# THE MUSIC MAP — V7 visual layout spec

Hand this spec to any image model to render the next visual. No code. Built from the locked handoff brief (`the-music-map-handoff-brief.md`) plus Julian's corrections of Nov 14–15, 2026.

## What V7 must fix vs V6

V6 had the depth axis backwards (underground near, popular far). V7 flips it: **mainstream in front, underground deep**. V7 also marks the Z=0 plane, which V6 did not show.

## The three axes (locked, do not change)

- **X = chronology**, in days from the origin. Origin (0,0,0) = July 6, 1974, the week "Rock the Boat" topped the Billboard Hot 100. Pre-disco is negative X, post-disco positive. X labels show days with year equivalents (-10,000 d = 1947, +5,000 d, +10,000 d = 2001, +15,000 d = 2015). The leading edge of X is always today; a glowing now-line rides that edge.
- **Y = tempo in plain BPM, 0 to 1000.** No negative numbers anywhere. The planes cross at 120 BPM (Nov 19, Julian: the realistic medium; the long-run average of popular music has hovered 117-122 BPM for eighty years, median pop song 116, Million Song Dataset mean about 125): faster tracks count up past the crossing, slower tracks count down from it toward 0. Each song's Y is its actual stated BPM. Y is drawn non-linear: the 0-120 BPM band gets about half the axis length, 120-1000 compressed into the other half; values stay plain BPM, only the drawing stretches. Ticks: 0, 60, 90, 120 (origin), 140, 175, 250, 500, 1000. Beatless sits on the floor (0 BPM) as a hollow point. A point never moves in Y.
- **Z = mainstream to underground.** Negative toward mainstream (front), positive toward underground (deep). The scale is open-ended; the working window is −50 to +50, with mid ticks at +25 and −25. This is cultural reach, not weirdness: a hugely popular, deeply strange song sits at the front; an obscure conventional one sits deep.

## The Z=0 plane (new in V7)

Draw the Z=0 plane as a visible, labelled upright plane. **Z=0 RESOLVED (Nov 19, Julian): the middle of the log reach scale, about 40,000 streams in a year (tens of thousands; ~70,000 on a lifetime top), a song with a real audience of thousands, known in its world, unknown outside it. That is somewhat known.** The reach scale is logarithmic: nine orders of magnitude, 0 streams at the underground end to billions at the mainstream end (top: Blinding Lights, 5 billion Spotify streams, Aug 31 2025; top single year: ~1.7 billion). Four equal log divisions, each about 200x: 0 to ~200 streams (about 198M tracks, 78% of all ISRCs), ~200 to ~40,000 (about 48M, 19%), ~40,000 to ~8.5M (about 7M, 3%), ~8.5M to billions (about 0.1M, under 0.1%). The middle is the geometric middle of the range, NOT the population median (the median song has roughly a dozen streams a year; the median framing from Nov 15 and Nov 19 is superseded). Example anchors, positions to be set once the scale is final: Taylor Swift, Bob Marley, Beethoven at the front; punk, obscure techno, gabber deep; a bedroom producer at the far deep edge.

**Baseline rule (Nov 19, Julian): the Z axis must extend both ways through the origin, with (0,0,0) in the middle of the line, never at its end. (0,0,0) is the middle of the log reach scale, about 40,000 streams a year, songs that are somewhat known. In the flat baseline view the Z ends are labelled with words only, mainstream at one end, underground at the other, no -50/+50 numbers on the axis; the Z diagonal carries the log-scale ticks instead: 200 streams on the underground half, 40,000 streams at the origin, 8.5M streams on the mainstream half. All three axes carry ticks now (Nov 20): Y 0, 60, 90, 120, 140, 175, 250, 500, 1000; X 1947, 1988, 2001, 2015 (the spec's day values -10,000, +5,000, +10,000, +15,000 shown as years); Z 200, 40,000, 8.5M streams. The baseline is drawn as a precise SVG, not an image-model render, because the model kept garbling labels: `music-map-axes-baseline.svg` in the Library, rendered to `music-map-axes-baseline-all-ticks.png`. Planes are added one at a time (Nov 20, Julian: build one at a time so the idea lands). First plane: Chronology x Popularity, the floor, green, drawn from the axis endpoints, axes and labels on top. CORRECTION (Nov 20, Julian): the chronology plane is the floor, not Chronology x Tempo; it does not involve the BPM axis at all, the BPM axis rises out of it, so the green never touches the BPM arrow. CORRECTION 2 (Nov 20, Julian): it is about the points, the ends, not the Z axis arm; the plane is defined by and ends at the axis endpoints. The 0-BPM-shift approach was dropped. Per Julian's reference image (three grid planes), the floor is drawn as a GREEN GRID bounded by the X and Z endpoints, the axes lying on it, the Z axis running through it as a line on the grid. The other two planes (Chronology x Tempo, Tempo x Popularity) are not drawn yet. Second plane (Nov 20, Julian): Tempo x Popularity, RED grid, bounded by the Y and Z endpoints, drawn at an angle as a slanted vertical band. Its bottom edge at Y=0 is a close line through the 0 marker (960,1110), because 0 BPM is the bottom/edge of the BPM axis. Third plane (Nov 20, Julian): Chronology x Tempo, BLUE grid, upright rectangle bounded by the X and Y endpoints. Color correction (Nov 20, Julian): orange became red; green belongs with Popularity and underground, so the floor is green. The three planes, named by color and axis (X = Chronology, Y = Tempo, Z = Popularity): BLUE, Chronology (Chronology x Tempo); RED, Tempo (Tempo x Popularity, bottom edge at Y=0 a close line through the 0 marker); GREEN, Popularity (floor, Chronology x Popularity, with underground). Y tick fix (Nov 20, Tempo agent): the 60 and 90 labels were swapped in the SVG (60 drawn above 90). Fixed: 60 at y=953, 90 at y=797. Fast half is a band scale (each tick interval exactly 94 px); slow half three bands ~157 px each. First mapped track (Nov 20, example, estimate): 2002, 92 BPM, 70K streams + healthy YouTube. Chronology x~1359 (+10,222 days, July 1 2002 convention). Tempo y~787 (just above the corrected 90 tick). Popularity (987,613), 38 px mainstream of origin (70K read as lifetime total ~ origin; YouTube doubled effective reach). Point on the graphic at (1386,760) with a plumb line to the base (1386,1083). Label change (Nov 20, Julian): "pre-1974" replaced by "before 1974", moved above the X axis at the left end mirroring "today", plainer and more obvious.**

**Label rules (Nov 19, Julian): labels are small, half size, and sit tight against their own axis, at the END of the axis, so there is no confusion about which label belongs to which axis. Tempo (BPM) (Y) on the LEFT side of the Y axis, up at the top end by the 1000. Chronology (X) at the far right end by today. Z is labelled by its ends only: mainstream (Z) at the top-right end, underground at the bottom-left end, each word appearing exactly once in the image, no separate Mainstream - Underground title. The origin tempo is labelled 120 BPM, tight against the origin point immediately left of the Y axis just above the X axis (the old floating 100 BPM label was deleted Nov 19). No tick marks anywhere except the Z log-scale ticks and the 0 floor tick, no small dashes crossing any other axis.**

**Arrows (Nov 19, Julian): arrowheads at the end of every axis, both ends, except 0 BPM, because that is the floor. At 0 BPM place a small tick / line instead of an arrow.**

## The three planes (from Julian's hand sketch)

Three mutually perpendicular, semi-transparent planes crossing at the single origin. Songs float in the space around and between them; points behind a plane stay visible through it.

- **Grey floor plane** = Chronology × Popularity (X across, Z deep), at 0 BPM — the bottom of the graph, since no music is slower than 0 BPM. Beatless sits on it as a hollow point; every point's plumb line drops to it.
- **Origin plane** = the horizontal plane at 120 BPM where the two upright planes cross.
- **Orange upright plane** = Chronology × Tempo (X across, Y up). This is the X=0 "disco" plane.
- **Yellow upright plane** = Tempo × Popularity (Y up, Z deep). This is the Z=0 plane, labelled as above.

## Composition and style

- Light off-white background. Open intersecting planes, not a closed box: chronology extends both ways past the origin (pre-disco to today), and mainstream–underground extends both ways past the origin (−50 to +50). No space theme, no stars, no nebula, nothing decorative.
- About ten tracks, not thousands. Each is a point of light with a short curved glowing trail showing where it has travelled. Trails brightest at the present, fading back.
- Every point drops a thin plumb line to the floor with a faint floor marker, so tempo (height) and reach (depth) read as two fully independent dimensions.
- Points get smaller and dimmer with distance. Muted palette: grey floor, warm orange and yellow uprights; the only things that glow are the songs and their trails.
- Labels must stay readable at phone size. Axis labels: X "Chronology", Y "Tempo (BPM)", Z "Mainstream — Underground", with the front labelled mainstream and the deep end underground.
- Never present invented numbers as measured data. Any BPM or Z position shown is an estimate and must be marked as one.

## The daily rule (context for the visual, not drawn)

Every day each track moves one notch along the chronology scale and slides up or down the mainstream-underground scale as its popularity changes. Y never moves. Movement is the story, so trails matter more than static positions.

## Animation (added 17 Nov 2026)

The diagram page animates the daily rule: a play button steps 180 days, one frame = one day; each track moves one notch/day in X, slides in Z, the median is recomputed daily; trails grow; a new release arrives at the now-line on Day 45. The daily X shift is drawn to scale; the Z drift is simulated illustration, not measured data.

## Hand-training sets (Nov 20, 2026, Julian: train by hand first, then scale up)

Two graphs, numbers on the dots, key on the side. Graph 1: tracks 1-10 (`music-map-10-tracks.svg` / `.png`, key upper-left). Graph 2: tracks 1-20 (`music-map-20-tracks.svg` / `.png`, key lower-left, two columns). The single example point (2002, 92 BPM, 70K) was removed when the real sets were mapped. Screen position = origin (960,640) + X displacement + Y displacement + Z displacement.

Set 1 (1-10), screen (X px, Y px, Z px): 1. Donna Summer, I Feel Love, 1977, 126 BPM, ~15M/yr, (1232,383). 2. Bee Gees, Stayin' Alive, 1977, 104 BPM, ~290M/yr, (1353,380). 3. ManyNames, Dreamverse, 2023, 100 BPM (guess, no published BPM), ~5K/yr, (1578,825). 4. Joey Beltram, Energy Flash, 1990, 123 BPM, ~100K/yr, (1223,591). 5. Bob Marley, Three Little Birds, 1977, 74 BPM (half-time), ~153M/yr, (1320,562). 6. Charles Aznavour, La Boheme, 1965, 115 BPM (rubato mid-range), ~30M/yr, (1088,410). 7. Newcleus, Jam On It, 1984, 116 BPM, ~35K/yr (at the origin), (1093,666). Artist is Newcleus, not Nucleus. 8. Sade, Smooth Operator, 1984, 119 BPM, ~250M/yr, (1441,307). 9. Mike Love, Babylon Control, 2011, 59 BPM, corrected ~1-2M/yr (see curator), (1626,816). 10. Glass Beams, Snake Oil, 2024, 153 BPM (conflict: Beatport 103), ~3M/yr, (1835,344).

Set 2 (11-20), screen: 11. Kraftwerk, The Model, 1978, 124 BPM, ~6M/yr, (1208,427). 12. Nina Simone, Sinnerman, 1965, 147 BPM, ~40M/yr, (1097,260). 13. Giorgio Moroder, Chase, 1978, 126 BPM, ~3M/yr, (1188,445). 14. Massive Attack, Unfinished Sympathy, 1991, 114 BPM, ~28M/yr, (1450,417). 15. Depeche Mode, Enjoy the Silence, 1990, 113 BPM, ~360M/yr, (1534,325). 16. Fela Kuti, Water No Get Enemy, 1975, 93 BPM, ~4M/yr, (1158,603). 17. New Order, Blue Monday, 1983, 130 BPM, ~25M/yr, (1332,344). 18. Erykah Badu, On & On, 1996, 80 BPM, ~38M/yr, (1544,584). 19. Underworld, Born Slippy .NUXX, 1995, 140 BPM, ~15M/yr, (1486,317). 20. Air, La Femme d'Argent, 1998, 80 BPM, ~5M/yr, (1482,662). Dots 11 and 13 sit close together (27 px apart, both 1978, ~125 BPM, similar reach); honest clustering, no overlap.

Curator verdict (Nov 20): 9 of 10 pass as-is in set 1; arithmetic spot-check clean (all day offsets, X pixels, Y interpolations, Z positions verified). One material correction: track 9 (Mike Love, Babylon Control). The popularity agent missed the track's viral YouTube video (Ineffable Music Group, 13M views, ~2M/yr). Corrected from ~10,000 streams/yr (deep underground) to ~1-2M/yr, Z from (906,694) to (1100,500), screen from (1433,1010) to (1626,816), a ~200 px move to mainstream of the origin. Date corrected to May 27, 2011 (x 1485.5, negligible). BPM 59 stands as a flagged guess, corroborated by a second reading, confidence raised to medium-low. Overall: conditional pass, train-ready once track 9 was fixed (it was). Honest unknowns correctly flagged: Dreamverse BPM (100, artist to confirm), Snake Oil BPM (153 vs 103, genuine 3:2 ambiguity), La Boheme rubato (115 mid-range).

Layout fix (Nov 20): the "40,000 streams" Z label moved from (1030,608) to (1060,560) in both graphs, so dots 4 and 16 clear it. The "200 streams" label stays at (775,895); the graph-2 key box was shrunk to end at x=740 so it does not cover it.

## Z revision: cultural prominence (Nov 20, 2026)

Z is no longer streams alone. It is estimated cultural prominence, informed by commercial reach, cultural influence, and current relevance (Julian, Nov 20). The composite is Prominence = 0.40 x Commercial + 0.30 x Influence + 0.30 x Relevance, each component 0-1.

- Commercial: Wikipedia peak chart position (bounded 1-100, the most era-robust number) plus certification level.
- Influence: Rolling Stone 500 Greatest Songs rank (MusicBrainz series, cached; matched by recording MBID, falling back to normalized artist+title because the resolver's MBID is often a different release of the same song).
- Relevance: Wikipedia pageviews (trailing 12 months, human only) plus YouTube views per year.

The composite maps back to an equivalent streams/yr on the existing log scale so the viewer and the 2D baseline keep working unchanged: Z=0 stays at ~40,000 streams/yr (Prominence ~0.5). A 1984 landmark can sit mainstream of the origin even with modest current streams, because its chart peak and influence count.

Spotify is no longer used. Spotify removed the audio-features endpoints for Development Mode apps (Nov 27, 2024) and the popularity field (Feb/Mar 2026); Extended Quota is granted only to registered businesses with 250,000+ monthly users. Tempo now comes from AcousticBrainz, reach from YouTube, no Spotify secrets needed.

Daily rule change (Nov 20): the daily recompute re-runs ONLY the culture axis. Date and BPM are stable facts that do not change day to day, and the hand-trained seed values are curator-checked, so they are never overwritten by the resolvers. Only the prominence moves daily.

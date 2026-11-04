# 🎵 Music Recommender Simulation — VibeFinder 1.0

## Project Summary

VibeFinder 1.0 is a small **content-based** music recommender. It reads a 20-song catalog from a CSV, compares every song to a user's "taste profile" (favorite genre, favorite mood, target energy), gives each song a score with a written list of reasons, and returns the top 5. It runs entirely in the terminal ("CLI-first") and is built to be easy to explain, test, and break on purpose.

---

## How The System Works

### How real recommenders do it

Platforms like Spotify and YouTube blend two families of methods:

- **Collaborative filtering** — "people who behave like you liked this." It uses *behavior* data from many users: plays, skips, likes, saves, playlist adds, listening time. It needs no knowledge of the song itself, but it struggles with brand-new songs and users (the *cold-start* problem).
- **Content-based filtering** — "this song resembles what you already like." It uses *attributes* of the song: genre, mood, tempo, energy, acousticness (and at scale, audio analysis and lyrics).

Every recommender has the same three layers, and it helps to keep them separate:

1. **Input data (features)** — facts about songs (genre, energy, tempo…) and about behavior (skips, replays).
2. **User preferences** — a summary of one person's taste, learned from their history or stated directly.
3. **Ranking / selection** — a rule that turns "how well does each song fit?" into an ordered list, then picks the top few.

Real systems learn their weights from millions of interactions; **VibeFinder is content-based only, with hand-set weights**, so every decision it makes can be read and explained. It prioritizes *genre first, then mood, then how close the energy is*.

### Features used

| Object | Fields used in scoring | Stored but not yet scored |
|---|---|---|
| `Song` | `genre`, `mood`, `energy` | `tempo_bpm`, `valence`, `danceability`, `acousticness`, `artist` |
| `UserProfile` | `favorite_genre`, `favorite_mood`, `target_energy` | `likes_acoustic` |

### Algorithm Recipe (Scoring Rule — judges ONE song)

| Rule | Points |
|---|---|
| Genre matches exactly | **+2.0** |
| Mood matches exactly | **+1.0** |
| Energy closeness | **+1.0 × (1 − \|song energy − target energy\|)** |

Maximum score is 4.0. The energy rule rewards being **close** to the target rather than simply "higher is better": a song at 0.82 for a 0.80 target earns +0.98, while a 0.30 song earns +0.50.

*Why no penalties for mismatches?* Ranking only cares about the gap between songs. Subtracting 2 from every non-matching song is mathematically the same as giving matching songs +4 — it just hides a weight increase and creates confusing negative scores.

### Ranking Rule (orders the WHOLE list)

`recommend_songs` runs `score_song` on every song in the catalog, sorts the results from highest to lowest score with `sorted()`, and keeps the top `k` (default 5). We need both rules because a score alone means nothing until it is compared against every other song's score.

### Data flow

```
data/songs.csv ──load_songs()──▶ list of 20 song dicts
                                      │
user prefs {genre, mood, energy} ──▶ score_song() on each song ──▶ (score, reasons)
                                      │
                         recommend_songs(): sort high→low, keep top k
                                      │
                         main.py prints title, score, and "Why"
```

### Biases expected before building

- Genre is worth twice a mood match, so a song in the right genre but the **wrong vibe** may outrank a perfect-vibe song from a neighboring genre.
- Genre and mood use **exact text matches**, so "indie pop" earns zero genre credit for a "pop" fan.
- With only 20 songs, genres that appear once can never fill a top-5 on their own.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app (from the repo root):

   ```bash
   python -m src.main                # default weights
   python -m src.main --experiment   # weight-shift experiment
   ```

### Running Tests

```bash
pytest
```

---

## Sample Recommendation Output

Output of `python -m src.main` (default weights, all five profiles):

```
Loaded songs: 20
Weights: {'genre': 2.0, 'mood': 1.0, 'energy': 1.0}

================================================================
Profile: High-Energy Pop
  prefs -> genre=pop, mood=happy, energy=0.8
----------------------------------------------------------------
1. Sunrise City - Neon Echo  [pop/happy]
   Score: 3.98
   Why:   genre match: pop (+2.0); mood match: happy (+1.0); energy 0.82 vs target 0.80 (+0.98)
2. Gym Hero - Max Pulse  [pop/intense]
   Score: 2.87
   Why:   genre match: pop (+2.0); energy 0.93 vs target 0.80 (+0.87)
3. Rooftop Lights - Indigo Parade  [indie pop/happy]
   Score: 1.96
   Why:   mood match: happy (+1.0); energy 0.76 vs target 0.80 (+0.96)
4. Fuego Lento - Calle Sol  [latin/playful]
   Score: 0.98
   Why:   energy 0.78 vs target 0.80 (+0.98)
5. Night Drive Loop - Neon Echo  [synthwave/moody]
   Score: 0.95
   Why:   energy 0.75 vs target 0.80 (+0.95)

================================================================
Profile: Kyle - Chill Hip-Hop
  prefs -> genre=hip-hop, mood=chill, energy=0.35
----------------------------------------------------------------
1. Velvet Corners - Lo Kingdom  [hip-hop/chill]
   Score: 3.97
   Why:   genre match: hip-hop (+2.0); mood match: chill (+1.0); energy 0.38 vs target 0.35 (+0.97)
2. Rainy Window Bars - Mellow Cipher  [hip-hop/relaxed]
   Score: 2.90
   Why:   genre match: hip-hop (+2.0); energy 0.45 vs target 0.35 (+0.90)
3. Iron Reps - Block Theory  [hip-hop/intense]
   Score: 2.41
   Why:   genre match: hip-hop (+2.0); energy 0.94 vs target 0.35 (+0.41)
4. Library Rain - Paper Lanterns  [lofi/chill]
   Score: 2.00
   Why:   mood match: chill (+1.0); energy 0.35 vs target 0.35 (+1.00)
5. Midnight Coding - LoRoom  [lofi/chill]
   Score: 1.93
   Why:   mood match: chill (+1.0); energy 0.42 vs target 0.35 (+0.93)

================================================================
Profile: Gym - Intense Hip-Hop
  prefs -> genre=hip-hop, mood=intense, energy=0.92
----------------------------------------------------------------
1. Iron Reps - Block Theory  [hip-hop/intense]
   Score: 3.98
   Why:   genre match: hip-hop (+2.0); mood match: intense (+1.0); energy 0.94 vs target 0.92 (+0.98)
2. Rainy Window Bars - Mellow Cipher  [hip-hop/relaxed]
   Score: 2.53
   Why:   genre match: hip-hop (+2.0); energy 0.45 vs target 0.92 (+0.53)
3. Velvet Corners - Lo Kingdom  [hip-hop/chill]
   Score: 2.46
   Why:   genre match: hip-hop (+2.0); energy 0.38 vs target 0.92 (+0.46)
4. Storm Runner - Voltline  [rock/intense]
   Score: 1.99
   Why:   mood match: intense (+1.0); energy 0.91 vs target 0.92 (+0.99)
5. Gym Hero - Max Pulse  [pop/intense]
   Score: 1.99
   Why:   mood match: intense (+1.0); energy 0.93 vs target 0.92 (+0.99)

================================================================
Profile: Deep Intense Rock
  prefs -> genre=rock, mood=intense, energy=0.9
----------------------------------------------------------------
1. Storm Runner - Voltline  [rock/intense]
   Score: 3.99
   Why:   genre match: rock (+2.0); mood match: intense (+1.0); energy 0.91 vs target 0.90 (+0.99)
2. Gym Hero - Max Pulse  [pop/intense]
   Score: 1.97
   Why:   mood match: intense (+1.0); energy 0.93 vs target 0.90 (+0.97)
3. Iron Reps - Block Theory  [hip-hop/intense]
   Score: 1.96
   Why:   mood match: intense (+1.0); energy 0.94 vs target 0.90 (+0.96)
4. Bassline Voltage - Kilowatt Kids  [edm/euphoric]
   Score: 0.95
   Why:   energy 0.95 vs target 0.90 (+0.95)
5. Broken Static - Ashen Vow  [metal/angry]
   Score: 0.93
   Why:   energy 0.97 vs target 0.90 (+0.93)

================================================================
Profile: Edge Case - Sad but Hyped
  prefs -> genre=pop, mood=sad, energy=0.9
----------------------------------------------------------------
1. Gym Hero - Max Pulse  [pop/intense]
   Score: 2.97
   Why:   genre match: pop (+2.0); energy 0.93 vs target 0.90 (+0.97)
2. Sunrise City - Neon Echo  [pop/happy]
   Score: 2.92
   Why:   genre match: pop (+2.0); energy 0.82 vs target 0.90 (+0.92)
3. Salt and Sorrow - June Harbor  [folk/sad]
   Score: 1.40
   Why:   mood match: sad (+1.0); energy 0.30 vs target 0.90 (+0.40)
4. Storm Runner - Voltline  [rock/intense]
   Score: 0.99
   Why:   energy 0.91 vs target 0.90 (+0.99)
5. Iron Reps - Block Theory  [hip-hop/intense]
   Score: 0.96
   Why:   energy 0.94 vs target 0.90 (+0.96)
```

---

## Experiments You Tried

**Weight shift** (`python -m src.main --experiment`): genre 2.0 → **1.0**, energy 1.0 → **2.0**, mood unchanged.

```
================================================================
Profile: High-Energy Pop
  prefs -> genre=pop, mood=happy, energy=0.8
----------------------------------------------------------------
1. Sunrise City - Neon Echo  [pop/happy]
   Score: 3.96
   Why:   genre match: pop (+1.0); mood match: happy (+1.0); energy 0.82 vs target 0.80 (+1.96)
2. Rooftop Lights - Indigo Parade  [indie pop/happy]
   Score: 2.92
   Why:   mood match: happy (+1.0); energy 0.76 vs target 0.80 (+1.92)
3. Gym Hero - Max Pulse  [pop/intense]
   Score: 2.74
   Why:   genre match: pop (+1.0); energy 0.93 vs target 0.80 (+1.74)
4. Fuego Lento - Calle Sol  [latin/playful]
   Score: 1.96
   Why:   energy 0.78 vs target 0.80 (+1.96)
5. Night Drive Loop - Neon Echo  [synthwave/moody]
   Score: 1.90
   Why:   energy 0.75 vs target 0.80 (+1.90)

================================================================
Profile: Kyle - Chill Hip-Hop
  prefs -> genre=hip-hop, mood=chill, energy=0.35
----------------------------------------------------------------
1. Velvet Corners - Lo Kingdom  [hip-hop/chill]
   Score: 3.94
   Why:   genre match: hip-hop (+1.0); mood match: chill (+1.0); energy 0.38 vs target 0.35 (+1.94)
2. Library Rain - Paper Lanterns  [lofi/chill]
   Score: 3.00
   Why:   mood match: chill (+1.0); energy 0.35 vs target 0.35 (+2.00)
3. Midnight Coding - LoRoom  [lofi/chill]
   Score: 2.86
   Why:   mood match: chill (+1.0); energy 0.42 vs target 0.35 (+1.86)
4. Spacewalk Thoughts - Orbit Bloom  [ambient/chill]
   Score: 2.86
   Why:   mood match: chill (+1.0); energy 0.28 vs target 0.35 (+1.86)
5. Rainy Window Bars - Mellow Cipher  [hip-hop/relaxed]
   Score: 2.80
   Why:   genre match: hip-hop (+1.0); energy 0.45 vs target 0.35 (+1.80)
```

- **Kyle – Chill Hip-Hop:** with default weights, *Iron Reps* (an intense 0.94-energy gym track) ranked **#3** for a chill listener purely because it is hip-hop. After the shift it drops out of the top 5, and chill lofi tracks move up. → **More accurate**, not just different.
- **High-Energy Pop:** *Rooftop Lights* (indie pop, happy, 0.76) climbs from #3 to **#2** above *Gym Hero*, which better matches a "happy pop" request.
- **Trade-off:** genre loyalty gets weaker. A user who truly only wants hip-hop now sees lofi and ambient songs in their list.

---

## Limitations and Risks

- Tiny catalog (20 songs); most genres appear only once.
- Exact string matching: "indie pop" ≠ "pop", "relaxed" ≠ "chill".
- Genre weight dominates, which can push a wrong-vibe song above a right-vibe one.
- Ignores tempo, valence, danceability, acousticness, lyrics, and listening history.
- No diversity rule: the same high-energy songs (e.g. *Gym Hero*) recur across many profiles.

See the [**Model Card**](model_card.md) for the full analysis.

---

## Reflection

<!-- KYLE: write 1–2 paragraphs in your own words:
     - how recommenders turn data into predictions
     - where bias or unfairness could show up in systems like this -->

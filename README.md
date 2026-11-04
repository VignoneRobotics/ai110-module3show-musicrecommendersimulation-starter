# 🎵 Music Recommender Simulation — VibeFinder 1.0

## Project Summary

VibeFinder 1.0 is a small **content-based** music recommender. It reads a 20-song catalog from a CSV, compares every song to a user's "taste profile" (favorite genre, favorite mood, target energy), gives each song a score with a written list of reasons, and returns the top 5 as a readable table. Related labels earn partial credit (e.g. "indie pop" counts halfway toward "pop"), and an optional diversity penalty keeps one artist or genre from crowding the list. It runs entirely in the terminal ("CLI-first") and is built to be easy to explain, test, and break on purpose.

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
| Genre is in the same family (e.g. indie pop ~ pop, lofi ~ hip-hop, metal ~ rock) | **+1.0** (half credit) |
| Mood matches exactly | **+1.0** |
| Mood is in the same family (e.g. relaxed ~ chill, angry ~ intense, playful ~ happy) | **+0.5** (half credit) |
| Energy closeness | **+1.0 × (1 − \|song energy − target energy\|)** |

Maximum score is 4.0. The energy rule rewards being **close** to the target rather than simply "higher is better": a song at 0.82 for a 0.80 target earns +0.98, while a 0.30 song earns +0.50. The "families" are listed in `RELATED_GENRES` / `RELATED_MOODS` in `src/recommender.py`.

*Why no penalties for mismatches?* Ranking only cares about the gap between songs. Subtracting 2 from every non-matching song is mathematically the same as giving matching songs +4 — it just hides a weight increase and creates confusing negative scores. Partial credit does the opposite: it *narrows* the gap for near-misses instead of widening it for misses.

### Ranking Rule (orders the WHOLE list)

`recommend_songs` runs `score_song` on every song in the catalog, sorts the results from highest to lowest score with `sorted()`, and keeps the top `k` (default 5). We need both rules because a score alone means nothing until it is compared against every other song's score.

**Optional diversity penalty (`--diverse`):** instead of taking the top 5 directly, the list is built one pick at a time. Each candidate loses **1.0 point for every song by the same artist** and **0.5 for every song of the same genre** already picked, and the best *adjusted* score wins the next slot. This keeps a top 5 from becoming five near-identical tracks.

### Data flow

```
data/songs.csv ──load_songs()──▶ list of 20 song dicts
                                      │
user prefs {genre, mood, energy} ──▶ score_song() on each song ──▶ (score, reasons)
                                      │
                         recommend_songs(): sort high→low, keep top k
                                      │   (--diverse: re-pick with artist/genre penalty)
                                      │
                         main.py prints a table: title, score, and "Why"
```

### Biases expected before building

- Genre is worth twice a mood match, so a song in the right genre but the **wrong vibe** may outrank a perfect-vibe song from a neighboring genre.
- Genre and mood originally used **exact text matches**, so "indie pop" earned zero genre credit for a "pop" fan (later fixed with partial credit).
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
   python -m src.main --diverse      # diversity penalty (flags can be combined)
   ```

### Running Tests

```bash
pytest
```

---

## Sample Recommendation Output

Output of `python -m src.main` (default weights, all five profiles). Each "Why" line is the exact list of points that song earned:

```
Loaded songs: 20
Weights: {'genre': 2.0, 'mood': 1.0, 'energy': 1.0}
Diversity penalty: OFF

Profile: High-Energy Pop  (genre=pop, mood=happy, energy=0.8)
┌─────┬──────────────────┬───────────────┬─────────────────┬─────────┬───────────────────────────────────────┐
│ #   │ Title            │ Artist        │ Genre/Mood      │ Score   │ Why                                   │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 1   │ Sunrise City     │ Neon Echo     │ pop/happy       │ 3.98    │ genre match: pop (+2.0)               │
│     │                  │               │                 │         │ mood match: happy (+1.0)              │
│     │                  │               │                 │         │ energy 0.82 vs target 0.80 (+0.98)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 2   │ Rooftop Lights   │ Indigo Parade │ indie pop/happy │ 2.96    │ related genre: indie pop ~ pop (+1.0) │
│     │                  │               │                 │         │ mood match: happy (+1.0)              │
│     │                  │               │                 │         │ energy 0.76 vs target 0.80 (+0.96)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 3   │ Gym Hero         │ Max Pulse     │ pop/intense     │ 2.87    │ genre match: pop (+2.0)               │
│     │                  │               │                 │         │ energy 0.93 vs target 0.80 (+0.87)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 4   │ Fuego Lento      │ Calle Sol     │ latin/playful   │ 1.48    │ related mood: playful ~ happy (+0.5)  │
│     │                  │               │                 │         │ energy 0.78 vs target 0.80 (+0.98)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 5   │ Bassline Voltage │ Kilowatt Kids │ edm/euphoric    │ 1.35    │ related mood: euphoric ~ happy (+0.5) │
│     │                  │               │                 │         │ energy 0.95 vs target 0.80 (+0.85)    │
└─────┴──────────────────┴───────────────┴─────────────────┴─────────┴───────────────────────────────────────┘

Profile: Steve - Chill Hip-Hop  (genre=hip-hop, mood=chill, energy=0.35)
┌─────┬───────────────────┬────────────────┬─────────────────┬─────────┬──────────────────────────────────────┐
│ #   │ Title             │ Artist         │ Genre/Mood      │ Score   │ Why                                  │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 1   │ Velvet Corners    │ Lo Kingdom     │ hip-hop/chill   │ 3.97    │ genre match: hip-hop (+2.0)          │
│     │                   │                │                 │         │ mood match: chill (+1.0)             │
│     │                   │                │                 │         │ energy 0.38 vs target 0.35 (+0.97)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 2   │ Rainy Window Bars │ Mellow Cipher  │ hip-hop/relaxed │ 3.40    │ genre match: hip-hop (+2.0)          │
│     │                   │                │                 │         │ related mood: relaxed ~ chill (+0.5) │
│     │                   │                │                 │         │ energy 0.45 vs target 0.35 (+0.90)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 3   │ Library Rain      │ Paper Lanterns │ lofi/chill      │ 3.00    │ related genre: lofi ~ hip-hop (+1.0) │
│     │                   │                │                 │         │ mood match: chill (+1.0)             │
│     │                   │                │                 │         │ energy 0.35 vs target 0.35 (+1.00)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 4   │ Midnight Coding   │ LoRoom         │ lofi/chill      │ 2.93    │ related genre: lofi ~ hip-hop (+1.0) │
│     │                   │                │                 │         │ mood match: chill (+1.0)             │
│     │                   │                │                 │         │ energy 0.42 vs target 0.35 (+0.93)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 5   │ Focus Flow        │ LoRoom         │ lofi/focused    │ 2.45    │ related genre: lofi ~ hip-hop (+1.0) │
│     │                   │                │                 │         │ related mood: focused ~ chill (+0.5) │
│     │                   │                │                 │         │ energy 0.40 vs target 0.35 (+0.95)   │
└─────┴───────────────────┴────────────────┴─────────────────┴─────────┴──────────────────────────────────────┘

Profile: Gym - Intense Hip-Hop  (genre=hip-hop, mood=intense, energy=0.92)
┌─────┬───────────────────┬───────────────┬─────────────────┬─────────┬────────────────────────────────────┐
│ #   │ Title             │ Artist        │ Genre/Mood      │ Score   │ Why                                │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼────────────────────────────────────┤
│ 1   │ Iron Reps         │ Block Theory  │ hip-hop/intense │ 3.98    │ genre match: hip-hop (+2.0)        │
│     │                   │               │                 │         │ mood match: intense (+1.0)         │
│     │                   │               │                 │         │ energy 0.94 vs target 0.92 (+0.98) │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼────────────────────────────────────┤
│ 2   │ Rainy Window Bars │ Mellow Cipher │ hip-hop/relaxed │ 2.53    │ genre match: hip-hop (+2.0)        │
│     │                   │               │                 │         │ energy 0.45 vs target 0.92 (+0.53) │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼────────────────────────────────────┤
│ 3   │ Velvet Corners    │ Lo Kingdom    │ hip-hop/chill   │ 2.46    │ genre match: hip-hop (+2.0)        │
│     │                   │               │                 │         │ energy 0.38 vs target 0.92 (+0.46) │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼────────────────────────────────────┤
│ 4   │ Storm Runner      │ Voltline      │ rock/intense    │ 1.99    │ mood match: intense (+1.0)         │
│     │                   │               │                 │         │ energy 0.91 vs target 0.92 (+0.99) │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼────────────────────────────────────┤
│ 5   │ Gym Hero          │ Max Pulse     │ pop/intense     │ 1.99    │ mood match: intense (+1.0)         │
│     │                   │               │                 │         │ energy 0.93 vs target 0.92 (+0.99) │
└─────┴───────────────────┴───────────────┴─────────────────┴─────────┴────────────────────────────────────┘

Profile: Deep Intense Rock  (genre=rock, mood=intense, energy=0.9)
┌─────┬──────────────────┬───────────────┬─────────────────┬─────────┬──────────────────────────────────────┐
│ #   │ Title            │ Artist        │ Genre/Mood      │ Score   │ Why                                  │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 1   │ Storm Runner     │ Voltline      │ rock/intense    │ 3.99    │ genre match: rock (+2.0)             │
│     │                  │               │                 │         │ mood match: intense (+1.0)           │
│     │                  │               │                 │         │ energy 0.91 vs target 0.90 (+0.99)   │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 2   │ Broken Static    │ Ashen Vow     │ metal/angry     │ 2.43    │ related genre: metal ~ rock (+1.0)   │
│     │                  │               │                 │         │ related mood: angry ~ intense (+0.5) │
│     │                  │               │                 │         │ energy 0.97 vs target 0.90 (+0.93)   │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 3   │ Gym Hero         │ Max Pulse     │ pop/intense     │ 1.97    │ mood match: intense (+1.0)           │
│     │                  │               │                 │         │ energy 0.93 vs target 0.90 (+0.97)   │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 4   │ Iron Reps        │ Block Theory  │ hip-hop/intense │ 1.96    │ mood match: intense (+1.0)           │
│     │                  │               │                 │         │ energy 0.94 vs target 0.90 (+0.96)   │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 5   │ Bassline Voltage │ Kilowatt Kids │ edm/euphoric    │ 0.95    │ energy 0.95 vs target 0.90 (+0.95)   │
└─────┴──────────────────┴───────────────┴─────────────────┴─────────┴──────────────────────────────────────┘

Profile: Edge Case - Sad but Hyped  (genre=pop, mood=sad, energy=0.9)
┌─────┬──────────────────┬───────────────┬─────────────────┬─────────┬───────────────────────────────────────┐
│ #   │ Title            │ Artist        │ Genre/Mood      │ Score   │ Why                                   │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 1   │ Gym Hero         │ Max Pulse     │ pop/intense     │ 2.97    │ genre match: pop (+2.0)               │
│     │                  │               │                 │         │ energy 0.93 vs target 0.90 (+0.97)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 2   │ Sunrise City     │ Neon Echo     │ pop/happy       │ 2.92    │ genre match: pop (+2.0)               │
│     │                  │               │                 │         │ energy 0.82 vs target 0.90 (+0.92)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 3   │ Rooftop Lights   │ Indigo Parade │ indie pop/happy │ 1.86    │ related genre: indie pop ~ pop (+1.0) │
│     │                  │               │                 │         │ energy 0.76 vs target 0.90 (+0.86)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 4   │ Salt and Sorrow  │ June Harbor   │ folk/sad        │ 1.40    │ mood match: sad (+1.0)                │
│     │                  │               │                 │         │ energy 0.30 vs target 0.90 (+0.40)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 5   │ Night Drive Loop │ Neon Echo     │ synthwave/moody │ 1.35    │ related mood: moody ~ sad (+0.5)      │
│     │                  │               │                 │         │ energy 0.75 vs target 0.90 (+0.85)    │
└─────┴──────────────────┴───────────────┴─────────────────┴─────────┴───────────────────────────────────────┘
```

---

## Experiments You Tried

### 1. Exact matching → partial label credit

The first version only gave points for **exact** label matches. Running the profiles exposed two problems:

- For **Steve – Chill Hip-Hop**, *Iron Reps* (an intense 0.94-energy gym track) ranked **#3**, above two genuinely chill lofi songs, purely because it is labeled hip-hop.
- For **High-Energy Pop**, *Rooftop Lights* (indie pop, happy) got **zero** genre credit and sat below *Gym Hero*.

Adding half credit for related labels fixed both: *Iron Reps* drops out of the chill top 5 (replaced by chill lofi tracks), and *Rooftop Lights* rises to #2 for happy pop. *Gym Hero* still appears in 4 of 5 profiles.

### 2. Weight shift (`--experiment`): genre 2.0 → 1.0, energy 1.0 → 2.0

```
Loaded songs: 20
Weights: {'genre': 1.0, 'mood': 1.0, 'energy': 2.0}  (EXPERIMENT)
Diversity penalty: OFF

Profile: High-Energy Pop  (genre=pop, mood=happy, energy=0.8)
┌─────┬──────────────────┬───────────────┬─────────────────┬─────────┬───────────────────────────────────────┐
│ #   │ Title            │ Artist        │ Genre/Mood      │ Score   │ Why                                   │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 1   │ Sunrise City     │ Neon Echo     │ pop/happy       │ 3.96    │ genre match: pop (+1.0)               │
│     │                  │               │                 │         │ mood match: happy (+1.0)              │
│     │                  │               │                 │         │ energy 0.82 vs target 0.80 (+1.96)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 2   │ Rooftop Lights   │ Indigo Parade │ indie pop/happy │ 3.42    │ related genre: indie pop ~ pop (+0.5) │
│     │                  │               │                 │         │ mood match: happy (+1.0)              │
│     │                  │               │                 │         │ energy 0.76 vs target 0.80 (+1.92)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 3   │ Gym Hero         │ Max Pulse     │ pop/intense     │ 2.74    │ genre match: pop (+1.0)               │
│     │                  │               │                 │         │ energy 0.93 vs target 0.80 (+1.74)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 4   │ Fuego Lento      │ Calle Sol     │ latin/playful   │ 2.46    │ related mood: playful ~ happy (+0.5)  │
│     │                  │               │                 │         │ energy 0.78 vs target 0.80 (+1.96)    │
├─────┼──────────────────┼───────────────┼─────────────────┼─────────┼───────────────────────────────────────┤
│ 5   │ Bassline Voltage │ Kilowatt Kids │ edm/euphoric    │ 2.20    │ related mood: euphoric ~ happy (+0.5) │
│     │                  │               │                 │         │ energy 0.95 vs target 0.80 (+1.70)    │
└─────┴──────────────────┴───────────────┴─────────────────┴─────────┴───────────────────────────────────────┘

Profile: Steve - Chill Hip-Hop  (genre=hip-hop, mood=chill, energy=0.35)
┌─────┬───────────────────┬────────────────┬─────────────────┬─────────┬──────────────────────────────────────┐
│ #   │ Title             │ Artist         │ Genre/Mood      │ Score   │ Why                                  │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 1   │ Velvet Corners    │ Lo Kingdom     │ hip-hop/chill   │ 3.94    │ genre match: hip-hop (+1.0)          │
│     │                   │                │                 │         │ mood match: chill (+1.0)             │
│     │                   │                │                 │         │ energy 0.38 vs target 0.35 (+1.94)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 2   │ Library Rain      │ Paper Lanterns │ lofi/chill      │ 3.50    │ related genre: lofi ~ hip-hop (+0.5) │
│     │                   │                │                 │         │ mood match: chill (+1.0)             │
│     │                   │                │                 │         │ energy 0.35 vs target 0.35 (+2.00)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 3   │ Midnight Coding   │ LoRoom         │ lofi/chill      │ 3.36    │ related genre: lofi ~ hip-hop (+0.5) │
│     │                   │                │                 │         │ mood match: chill (+1.0)             │
│     │                   │                │                 │         │ energy 0.42 vs target 0.35 (+1.86)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 4   │ Rainy Window Bars │ Mellow Cipher  │ hip-hop/relaxed │ 3.30    │ genre match: hip-hop (+1.0)          │
│     │                   │                │                 │         │ related mood: relaxed ~ chill (+0.5) │
│     │                   │                │                 │         │ energy 0.45 vs target 0.35 (+1.80)   │
├─────┼───────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 5   │ Focus Flow        │ LoRoom         │ lofi/focused    │ 2.90    │ related genre: lofi ~ hip-hop (+0.5) │
│     │                   │                │                 │         │ related mood: focused ~ chill (+0.5) │
│     │                   │                │                 │         │ energy 0.40 vs target 0.35 (+1.90)   │
└─────┴───────────────────┴────────────────┴─────────────────┴─────────┴──────────────────────────────────────┘
```

- **Steve:** chill lofi songs move to #2 and #3, ahead of *Rainy Window Bars* (hip-hop but only "relaxed"). The list becomes more about *vibe* than *genre*.
- **High-Energy Pop:** same top 3 order, but the scores spread out and non-pop songs with the right energy close the gap.
- **Verdict:** more accurate for vibe-based listeners; weaker for genre-loyal ones. Defaults were kept so genre still leads.

### 3. Diversity penalty (`--diverse`)

```
Loaded songs: 20
Weights: {'genre': 2.0, 'mood': 1.0, 'energy': 1.0}
Diversity penalty: ON

Profile: Steve - Chill Hip-Hop  (genre=hip-hop, mood=chill, energy=0.35)
┌─────┬────────────────────┬────────────────┬─────────────────┬─────────┬──────────────────────────────────────┐
│ #   │ Title              │ Artist         │ Genre/Mood      │ Score   │ Why                                  │
├─────┼────────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 1   │ Velvet Corners     │ Lo Kingdom     │ hip-hop/chill   │ 3.97    │ genre match: hip-hop (+2.0)          │
│     │                    │                │                 │         │ mood match: chill (+1.0)             │
│     │                    │                │                 │         │ energy 0.38 vs target 0.35 (+0.97)   │
├─────┼────────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 2   │ Library Rain       │ Paper Lanterns │ lofi/chill      │ 3.00    │ related genre: lofi ~ hip-hop (+1.0) │
│     │                    │                │                 │         │ mood match: chill (+1.0)             │
│     │                    │                │                 │         │ energy 0.35 vs target 0.35 (+1.00)   │
├─────┼────────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 3   │ Rainy Window Bars  │ Mellow Cipher  │ hip-hop/relaxed │ 2.90    │ genre match: hip-hop (+2.0)          │
│     │                    │                │                 │         │ related mood: relaxed ~ chill (+0.5) │
│     │                    │                │                 │         │ energy 0.45 vs target 0.35 (+0.90)   │
│     │                    │                │                 │         │ diversity penalty (-0.5)             │
├─────┼────────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 4   │ Midnight Coding    │ LoRoom         │ lofi/chill      │ 2.43    │ related genre: lofi ~ hip-hop (+1.0) │
│     │                    │                │                 │         │ mood match: chill (+1.0)             │
│     │                    │                │                 │         │ energy 0.42 vs target 0.35 (+0.93)   │
│     │                    │                │                 │         │ diversity penalty (-0.5)             │
├─────┼────────────────────┼────────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 5   │ Spacewalk Thoughts │ Orbit Bloom    │ ambient/chill   │ 1.93    │ mood match: chill (+1.0)             │
│     │                    │                │                 │         │ energy 0.28 vs target 0.35 (+0.93)   │
└─────┴────────────────────┴────────────────┴─────────────────┴─────────┴──────────────────────────────────────┘

Profile: Gym - Intense Hip-Hop  (genre=hip-hop, mood=intense, energy=0.92)
┌─────┬───────────────────┬───────────────┬─────────────────┬─────────┬──────────────────────────────────────┐
│ #   │ Title             │ Artist        │ Genre/Mood      │ Score   │ Why                                  │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 1   │ Iron Reps         │ Block Theory  │ hip-hop/intense │ 3.98    │ genre match: hip-hop (+2.0)          │
│     │                   │               │                 │         │ mood match: intense (+1.0)           │
│     │                   │               │                 │         │ energy 0.94 vs target 0.92 (+0.98)   │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 2   │ Rainy Window Bars │ Mellow Cipher │ hip-hop/relaxed │ 2.03    │ genre match: hip-hop (+2.0)          │
│     │                   │               │                 │         │ energy 0.45 vs target 0.92 (+0.53)   │
│     │                   │               │                 │         │ diversity penalty (-0.5)             │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 3   │ Storm Runner      │ Voltline      │ rock/intense    │ 1.99    │ mood match: intense (+1.0)           │
│     │                   │               │                 │         │ energy 0.91 vs target 0.92 (+0.99)   │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 4   │ Gym Hero          │ Max Pulse     │ pop/intense     │ 1.99    │ mood match: intense (+1.0)           │
│     │                   │               │                 │         │ energy 0.93 vs target 0.92 (+0.99)   │
├─────┼───────────────────┼───────────────┼─────────────────┼─────────┼──────────────────────────────────────┤
│ 5   │ Midnight Coding   │ LoRoom        │ lofi/chill      │ 1.50    │ related genre: lofi ~ hip-hop (+1.0) │
│     │                   │               │                 │         │ energy 0.42 vs target 0.92 (+0.50)   │
└─────┴───────────────────┴───────────────┴─────────────────┴─────────┴──────────────────────────────────────┘
```

- **Steve:** the second LoRoom/lofi track (*Focus Flow*) is pushed out, and *Spacewalk Thoughts* (ambient, chill) enters, so the list now spans hip-hop, lofi, and ambient.
- **Gym:** only two hip-hop songs survive, and *Velvet Corners* (chill) is dropped. **Side effect:** *Midnight Coding* (a chill lofi track) fills slot #5. Diversity bought variety at the cost of fit.

---

## Limitations and Risks

- Tiny catalog (20 songs); most genres appear only once.
- The genre/mood "families" are hand-picked, so they encode one person's opinion of which styles are related.
- Genre weight still dominates for some profiles: the gym profile still sees chill hip-hop at #2–#3 without `--diverse`.
- Ignores tempo, valence, danceability, acousticness, lyrics, and listening history.
- *Gym Hero* still appears across 4 of 5 profiles. The diversity penalty works *within* one list, not *across* users.

See the [**Model Card**](model_card.md) for the full analysis.

---

## Reflection

Read the full [**Model Card**](model_card.md).

Building VibeFinder made the path from data to prediction concrete. Every recommendation starts as features (genre, mood, energy), gets compared against a user's stated preferences by a scoring rule, and only becomes a "recommendation" after a ranking rule sorts every song against every other. Real systems like Spotify follow the same shape. The difference is that they learn their weights from millions of users' plays and skips, while mine were set by hand. That makes mine easy to explain, but only as good as my guesses.

Bias showed up quickly, and in places I didn't expect. Exact label matching meant "indie pop" scored zero for a pop fan, and a heavy genre weight pushed an intense gym track into a chill listener's list. Partial credit fixed those, but it also introduced a new kind of bias: someone had to decide which genres count as "related", and that was a judgment call. Even after adding a diversity penalty, *Gym Hero* still showed up for four of five profiles. That's a small version of how real platforms keep resurfacing the same popular tracks and narrow what people discover.

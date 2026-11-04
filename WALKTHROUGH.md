# 🧭 Walkthrough: How This Project Was Built (Side-by-Side Reference)

A step-by-step record of the redo. Each step shows **where** the work happened, **what** was done, **why**, and which **rubric item** it earns.

**Where legend:** 🌐 GitHub (browser) · 💻 Terminal (VS Code, PowerShell) · 📝 Editor (VS Code) · 🤖 AI assistant (Claude)

---

## Phase 0: Setup

| # | Where | What we did | Why | Rubric |
|---|---|---|---|---|
| 0.1 | 🌐 | Forked `codepath/ai110-module3show-musicrecommendersimulation-starter` to `VignoneRobotics` | A fork is *your own copy* on GitHub; you can push to it without touching CodePath's original. | Submission: correct repo |
| 0.2 | 💻 | `git clone <fork URL> music-rec` | Downloads the repo + full history to your computer so you can edit and run it. | — |
| 0.3 | 💻 | `python -m venv .venv` → `.\.venv\Scripts\Activate.ps1` → `pip install -r requirements.txt` | A virtual environment is a private toolbox per project, so package versions don't clash across projects. | — |

## Phase 1: Understanding the Problem

| # | Where | What we did | Why | Rubric |
|---|---|---|---|---|
| 1.1 | 🤖 | Asked: *"Explain how Spotify/YouTube recommend songs. Contrast collaborative filtering (other users' behavior) with content-based filtering (song attributes)."* | You need the vocabulary before building: real systems mix both; ours is content-based only. | Explanation of real systems (3 pts) |
| 1.2 | 📝 | Read `data/songs.csv`: columns `genre, mood, energy, tempo_bpm, valence, danceability, acousticness` | Features are the raw ingredients. Picked **genre, mood, energy** because they map most directly to a "vibe". | — |
| 1.3 | 🤖 | Asked: *"How do I score a numeric feature so songs closer to the target win, instead of just higher = better?"* → `1 − |song − target|` | "Closeness" is the key idea: a chill listener wants 0.35 energy, not the maximum. | Scoring reflects features |
| 1.4 | 🤖 | Asked why we need a **Scoring Rule** *and* a **Ranking Rule** | Scoring judges one song; ranking compares all scores. A score of 2.9 means nothing until you know the others. | Distinguishes input / prefs / ranking |
| 1.5 | 📝 | Wrote **How The System Works** in `README.md` | Locks in the concept before coding. | Explanation (3 pts) |

## Phase 2: Designing the Simulation

| # | Where | What we did | Why | Rubric |
|---|---|---|---|---|
| 2.1 | 🤖📝 | Added 10 songs (ids 11–20) to `songs.csv`: 3 hip-hop + country, metal, classical, EDM, folk, R&B, Latin | Starter had 10 songs and **no hip-hop**, so the personal profile would have had nothing to match. New songs add missing genres and moods (sad, angry, euphoric…). | Dataset ≥15–20 songs, ≥3 attributes (3 pts) |
| 2.2 | 📝 | Defined 5 profiles: High-Energy Pop, Kyle (chill hip-hop), Gym (intense hip-hop), Deep Intense Rock, Sad-but-Hyped (adversarial) | Two profiles share a genre but have opposite vibes, which is a clean test of whether genre overpowers vibe. The adversarial one asks for something that doesn't exist. | ≥3 distinct profiles |
| 2.3 | 🤖 | Decided on recipe: **genre +2, mood +1, energy up to +1**. Considered and **rejected** −2/−1 mismatch penalties | Ranking only cares about *gaps* between songs, so a −2 penalty is just a disguised +4 genre weight. | Scoring function |
| 2.4 | 📝 | Documented recipe, data-flow sketch, and expected biases in `README.md` | Predicting bias *before* testing makes the Phase 4 results meaningful. | — |

**Commit:** `git add data/songs.csv` → `git commit -m "Expand dataset to 20 songs with hip-hop and missing genres/moods"`

## Phase 3: Implementation

| # | Where | What we did | Why | Rubric |
|---|---|---|---|---|
| 3.1 | 📝 | `load_songs()` uses `csv.DictReader` and converts numeric columns with `float()`/`int()` | CSV values arrive as **text**: `"0.82" - "0.80"` crashes, `0.82 - 0.80` works. | Dataset loads without errors |
| 3.2 | 📝 | `score_song()` returns `(score, reasons)` | The reasons list is what makes the output explainable ("genre match: pop (+2.0)"). | Scoring (3 pts) + Explanations |
| 3.3 | 📝 | `recommend_songs()` scores every song, then `sorted(..., reverse=True)[:k]` | `sorted()` returns a **new** list; `.sort()` changes the original in place. A new list is safer, since the catalog stays untouched. | Sorted list (3 pts) |
| 3.4 | 📝 | Filled in the OOP `Recommender` class by **reusing** `score_song` | The tests use classes, `main.py` uses dicts. One scoring function feeding both means the two can never disagree. | Tests pass |
| 3.5 | 📝 | **Bug fixed:** `main.py` said `from recommender import …`; changed to `from src.recommender import …` | The lab runs `python -m src.main` from the repo root, where Python looks for `src.recommender`, not `recommender`. The starter import would crash. | Runs without errors |
| 3.6 | 💻 | `python -m src.main` → top 5 per profile; `pytest` → 2 passed | Verify before documenting. Never paste output you didn't actually run. | Runs for different profiles |
| 3.7 | 📝 | Pasted real output into README **as a fenced code block** | The rubric explicitly wants text, not screenshots. | Outputs as text (Explanations, Profiles) |

**Commit:** `git add src/` → `git commit -m "Implement working CLI-first recommender: load CSV, score with reasons, rank top-k"`

## Phase 4: Evaluate and Explain

| # | Where | What we did | Why | Rubric |
|---|---|---|---|---|
| 4.1 | 💻 | Ran all 5 profiles and compared results to intuition | **Finding:** *Iron Reps* (gym track) ranked #3 for the chill listener, so genre weight overpowers vibe. | Profiles (3 pts) |
| 4.2 | 📝 | Added `EXPERIMENT_WEIGHTS` + `--experiment` flag (genre 2→1, energy 1→2) | Keeping weights in one dictionary means an experiment is a one-line change, not a rewrite. | Experiment |
| 4.3 | 💻 | `python -m src.main --experiment` | Result: *Iron Reps* drops out of the chill top 5; *Rooftop Lights* rises for pop. **More accurate**, with weaker genre loyalty as the trade-off. | — |
| 4.4 | 📝 | Wrote pairwise profile comparisons + bias section in `model_card.md` | Shows you understand *why* outputs differ, not just *that* they differ. | Comments on differences; Model card |

**Commit:** `git add README.md model_card.md` → `git commit -m "Document design, sample output, profile experiments, and bias analysis"`

## Phase 5: Reflection and Model Card

| # | Where | What we did | Why | Rubric |
|---|---|---|---|---|
| 5.1 | 📝 | Completed model card sections 1–8 | Industry practice: document intended use, data limits, and known biases. | Model card (3 pts) |
| 5.2 | 📝 | **Kyle writes** section 9 (Personal Reflection) and the README *Reflection* | A reflection only counts if it's yours. | Submission: reflection |

**Commit + push:** `git add WALKTHROUGH.md` → `git commit -m "Add side-by-side build walkthrough"`, then after the reflection: `git add README.md model_card.md` → `git commit -m "Add personal reflection"` → `git push origin main`

---

## Rubric Coverage Summary

| Required feature (3 pts each) | Where it lives |
|---|---|
| Explanation of real recommenders | README → *How The System Works* |
| Structured song dataset | `data/songs.csv` (20 songs, 7 attributes) |
| Scoring function | `src/recommender.py` → `score_song` |
| Sorted recommendation function | `src/recommender.py` → `recommend_songs` |
| Explanations for recommendations | "Why:" lines in README *Sample Output* |
| Experiments with multiple profiles | README *Sample Output* + *Experiments*, model card §7 |
| Completed model card | `model_card.md` |

Stretch features: not attempted.

# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

- **What it does:** Suggests the top 5 songs from a small catalog that best fit a user's stated favorite genre, favorite mood, and target energy level. Every suggestion comes with the reasons it earned its points.
- **Assumptions about the user:** The user can describe their taste with one genre, one mood, and one energy number. It assumes taste is stable and fits in those three boxes.
- **Who it is for:** Classroom exploration of how recommenders turn data into rankings.

**Not intended for:** real users or a real product, judging music quality, or any decision that matters (it has no listening history, no consent model, and only 20 songs).

---

## 3. How the Model Works

Think of it as a judge with a scorecard that looks at every song one at a time.

- If the song's **genre** is exactly the user's favorite, it gets **2 points**.
- If the song's **mood** is exactly the user's favorite, it gets **1 point**.
- It then checks **energy** (how intense the song feels, from 0 to 1). The closer the song is to the user's target, the more of **1 bonus point** it earns. A perfect match earns the full point; a song that is far off earns little.

After every song has a score, the list is sorted from highest to lowest and the top 5 are shown, along with a "Why" line listing exactly which points each song earned.

**Changes from the starter:** implemented CSV loading with number conversion, the scoring rule above, sorting/ranking, readable explanations, five test profiles, and a switchable weight experiment (`--experiment`). There are deliberately no penalty points: subtracting points from mismatches would just be a hidden way of making genre matter more.

---

## 4. Data

- **Size:** 20 songs (10 from the starter + 10 added).
- **Attributes per song:** genre, mood, energy, tempo (BPM), valence (how positive it sounds), danceability, acousticness. Only genre, mood, and energy are used for scoring.
- **Added:** 10 songs covering genres and moods missing from the starter: hip-hop (3), country, metal, classical, EDM, folk, R&B, Latin; moods like sad, angry, nostalgic, euphoric, romantic, peaceful, playful.
- **Gaps:** most genres have only one song. There are no lyrics, no language, no release era, no popularity, and no song that is both "sad" and high-energy. The labels were assigned by hand, so they reflect one person's sense of what "chill" or "intense" means.

---

## 5. Strengths

- **Clear-cut tastes work well.** When a song matches genre, mood, and energy (e.g. *Storm Runner* for the rock profile, *Iron Reps* for the gym profile), it lands at #1 with a near-perfect 3.9+ score.
- **Fully explainable.** Every score can be traced line by line in the "Why" output, which makes errors easy to spot.
- **Energy closeness works as designed.** It rewards songs *near* the target, so a chill listener isn't pushed toward the loudest tracks.

---

## 6. Limitations and Bias

The biggest weakness found is **genre dominance**: because a genre match (+2) is worth twice a mood match (+1), genre can override vibe. For the chill hip-hop profile, *Iron Reps*, a 0.94-energy gym track, ranked **#3**, above two genuinely chill lofi songs, purely because it is labeled hip-hop. The system also uses **exact text matching**, so *Rooftop Lights* ("indie pop") gets zero genre credit from a pop fan, and "relaxed" gets no credit as a near-match for "chill". High-energy songs like *Gym Hero* show up for **four of the five profiles**, a small version of a "filter bubble" where the same tracks keep resurfacing. Finally, genres with only one song in the catalog (most of them) can never fill a top 5, so users with niche tastes are underserved.

---

## 7. Evaluation

**Profiles tested:** High-Energy Pop, Kyle – Chill Hip-Hop, Gym – Intense Hip-Hop, Deep Intense Rock, and an adversarial "Sad but Hyped" profile (pop, sad, energy 0.9). Full outputs are in the README under *Sample Recommendation Output*.

**What I looked for:** whether the #1 song "felt right", whether the explanations matched the math, and whether a song showed up where it didn't belong.

**Comparisons between profiles:**

- **Kyle (chill hip-hop) vs. Gym (intense hip-hop):** Same genre, opposite energy. Both lists are led by hip-hop, but the #1 flips: *Velvet Corners* (0.38 energy) for chill, *Iron Reps* (0.94) for gym. This makes sense because mood and energy are the only things separating them. The surprise is that each profile still gets the *other's* signature song at #3, because genre points outweigh the energy gap.
- **High-Energy Pop vs. Deep Intense Rock:** Both want high energy, so *Gym Hero* appears in both. For pop it ranks #2 through the genre match; for rock it ranks #2 through the mood match ("intense"). Same song, two different reasons, which shows how a single high-energy track can slip into many lists.
- **Gym vs. Deep Intense Rock:** Both share the "intense" mood, so *Storm Runner*, *Iron Reps*, and *Gym Hero* appear in both lists, just in different orders. Genre decides who gets #1.
- **High-Energy Pop vs. Sad but Hyped (adversarial):** Both ask for pop, so the pop songs dominate both. The only "sad" song (*Salt and Sorrow*, a quiet folk track) climbs to #3 on mood alone even though its energy is far off. The system cannot satisfy contradictory requests, so it falls back on genre.

**Why does *Gym Hero* keep showing up for people who want "Happy Pop"?** It is labeled pop, so it gets the big +2 genre bonus, and its energy (0.93) is close to the 0.8 target. The system cannot tell that "intense workout pop" and "happy pop" feel different, because the mood bonus (+1) is smaller than the genre bonus.

**Experiment (weight shift):** Halving genre (2→1) and doubling energy (1→2) removed *Iron Reps* from the chill listener's top 5 and moved *Rooftop Lights* up to #2 for happy pop. Recommendations became **more accurate** for vibe-based listeners, at the cost of weaker genre loyalty.

**Automated tests:** `pytest`; both starter tests pass (pop/happy song ranks first; explanations are non-empty).

---

## 8. Future Work

- **Partial credit for similar labels:** treat "indie pop" as close to "pop" and "relaxed" as close to "chill", instead of all-or-nothing matches.
- **Use the unused features:** score `likes_acoustic` against acousticness, and add tempo and valence closeness.
- **Diversity rule:** penalize repeating the same artist or genre in the top 5, so lists aren't five near-identical songs.

---

## 9. Personal Reflection

<!-- KYLE: your own words. Prompts from the lab:
     - What was your biggest learning moment during this project?
     - How did using AI tools help you, and when did you need to double-check them?
     - What surprised you about how simple algorithms can still "feel" like recommendations?
     - What would you try next if you extended this project? -->

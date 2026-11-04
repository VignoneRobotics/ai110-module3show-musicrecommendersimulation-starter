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

- If the song's **genre** is exactly the user's favorite, it gets **2 points**. If it's a close cousin (indie pop for a pop fan, lofi for a hip-hop fan, metal for a rock fan), it gets **1 point**.
- If the song's **mood** is exactly the user's favorite, it gets **1 point**. A close cousin (relaxed for chill, angry for intense) gets **half a point**.
- It then checks **energy** (how intense the song feels, from 0 to 1). The closer the song is to the user's target, the more of **1 bonus point** it earns.

After every song has a score, the list is sorted from highest to lowest and the top 5 are shown in a table, with a "Why" column listing exactly which points each song earned.

**Optional diversity mode:** the top 5 is picked one song at a time, and a song loses 1 point if its artist is already on the list and half a point for each song of its genre already on the list.

**Changes from the starter:** CSV loading with number conversion, the scoring rule above, partial credit for related labels, sorting/ranking, readable explanations in a table, five test profiles, and two switchable modes (`--experiment` weight shift, `--diverse` penalty). There are deliberately no penalty points for mismatches: subtracting points from misses would just be a hidden way of making genre matter more.

---

## 4. Data

- **Size:** 20 songs (10 from the starter + 10 added).
- **Attributes per song:** genre, mood, energy, tempo (BPM), valence (how positive it sounds), danceability, acousticness. Only genre, mood, and energy are used for scoring.
- **Added:** 10 songs covering genres and moods missing from the starter: hip-hop (3), country, metal, classical, EDM, folk, R&B, Latin; moods like sad, angry, nostalgic, euphoric, romantic, peaceful, playful.
- **Gaps:** most genres have only one song. There are no lyrics, no language, no release era, no popularity, and no song that is both "sad" and high-energy. The labels were assigned by hand, so they reflect one person's sense of what "chill" or "intense" means.

---

## 5. Strengths

- **Clear-cut tastes work well.** When a song matches genre, mood, and energy (e.g. *Storm Runner* for rock, *Iron Reps* for gym, *Velvet Corners* for chill hip-hop), it lands at #1 with a 3.9+ score.
- **Fully explainable.** Every score can be traced point by point in the "Why" column, which made each bias in this card easy to find.
- **Near-misses aren't thrown away.** Partial credit lets "indie pop" and "relaxed" count for something, which matches how people actually describe music.

---

## 6. Limitations and Bias

The biggest weakness found was **genre dominance with exact matching**. In the first version, *Iron Reps*, a 0.94-energy gym track, ranked #3 for a *chill* hip-hop listener only because of its genre label, while *Rooftop Lights* ("indie pop") got zero credit from a pop fan. Partial credit fixed both cases, but the weighting still favors genre: the gym profile still gets two chill hip-hop songs at #2–#3. The genre and mood "families" are hand-chosen, so they bake one person's opinion of which styles are related into the scores. High-energy songs like *Gym Hero* appear in **four of five profiles**, a small "filter bubble" where the same tracks keep resurfacing for different people. Most genres have only one song, so listeners with niche tastes are underserved no matter how the weights are set.

### Diversity penalty and fairness

Without a diversity rule, a top 5 can fill up with one artist or one genre, which over-rewards whatever is most common in the catalog. The `--diverse` mode subtracts points for repeat artists (−1.0) and repeat genres (−0.5 each) *while* the list is being built, so the second lofi track has to beat a different-genre song on adjusted score to earn a slot. For the chill profile this replaced a second LoRoom track with an ambient song, widening the list across three genres. The trade-off: for the gym profile it let in a chill lofi track at #5, a worse fit. It improves **variety within one list**, but it does **not** stop *Gym Hero* from appearing across many users' lists. That would need a cross-user rule.

---

## 7. Evaluation

**Profiles tested:** High-Energy Pop, Kyle – Chill Hip-Hop, Gym – Intense Hip-Hop, Deep Intense Rock, and an adversarial "Sad but Hyped" profile (pop, sad, energy 0.9). Full outputs are in the README under *Sample Recommendation Output*.

**What I looked for:** whether the #1 song "felt right", whether the explanations matched the math, and whether a song showed up where it didn't belong.

**Comparisons between profiles:**

- **Kyle (chill hip-hop) vs. Gym (intense hip-hop):** Same genre, opposite energy. The #1 flips: *Velvet Corners* (0.38 energy) for chill, *Iron Reps* (0.94) for gym. The chill list fills out with chill lofi tracks (related genre plus mood match). The gym list, though, still pulls in the two *calmer* hip-hop songs at #2–#3 on genre points alone, ahead of intense rock and pop. The genre bonus is strong enough to override a 0.5 energy gap.
- **High-Energy Pop vs. Deep Intense Rock:** Both want high energy, so *Gym Hero* appears in both: through the genre match for pop, through the "intense" mood match for rock. Same song, two different reasons, which shows how one high-energy track slips into many lists.
- **Gym vs. Deep Intense Rock:** They share the "intense" mood, so *Storm Runner*, *Iron Reps*, and *Gym Hero* appear in both lists in different orders. Genre decides #1. *Broken Static* (metal) now shows up for rock through the rock–metal family.
- **High-Energy Pop vs. Sad but Hyped (adversarial):** Both ask for pop, so pop songs dominate both lists. No song is both sad and high-energy, so the system falls back on genre and energy. The only truly sad song (*Salt and Sorrow*) sits at #4 because its energy is far off. Contradictory requests get the "least wrong" answer, not a good one.

**Why does *Gym Hero* keep showing up for people who want "Happy Pop"?** It's labeled pop, so it gets the big +2 genre bonus, and its energy (0.93) is near the 0.8 target. The system can't tell "intense workout pop" from "happy pop" well, because the mood bonus (+1) is smaller than the genre bonus.

**Experiments:**

1. **Partial label credit:** removed *Iron Reps* from the chill top 5 and moved *Rooftop Lights* to #2 for happy pop. Kept as the default.
2. **Weight shift** (genre 2→1, energy 1→2): pushed chill lofi songs above "relaxed" hip-hop for Kyle, making the list more about vibe than genre. Recommendations got **more accurate** for vibe-based listeners, at the cost of genre loyalty.
3. **Diversity penalty:** more variety per list, with an occasional weaker fit (see section 6).

**Automated tests:** `pytest`; both starter tests pass (pop/happy song ranks first; explanations are non-empty).

---

## 8. Future Work

- **Cross-user diversity:** track how often a song is recommended across all users and gently down-rank "everywhere" songs like *Gym Hero*.
- **Use the unused features:** score `likes_acoustic` against acousticness, and add tempo and valence closeness.
- **Learn the families instead of hand-picking them:** group genres and moods by their audio features rather than one person's opinion.

---

## 9. Personal Reflection

<!-- KYLE: your own words. Prompts from the lab:
     - What was your biggest learning moment during this project?
     - How did using AI tools help you, and when did you need to double-check them?
     - What surprised you about how simple algorithms can still "feel" like recommendations?
     - What would you try next if you extended this project? -->

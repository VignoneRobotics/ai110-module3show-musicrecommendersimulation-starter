"""
Command line runner for VibeFinder 1.0.

Run from the repo root:
    python -m src.main               # default weights
    python -m src.main --experiment  # Phase 4 weight-shift experiment
    python -m src.main --diverse     # apply the artist/genre diversity penalty
(flags can be combined)
"""

import sys

from tabulate import tabulate

from src.recommender import (
    load_songs,
    recommend_songs,
    DEFAULT_WEIGHTS,
    EXPERIMENT_WEIGHTS,
)

PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Kyle - Chill Hip-Hop": {"genre": "hip-hop", "mood": "chill", "energy": 0.35},
    "Gym - Intense Hip-Hop": {"genre": "hip-hop", "mood": "intense", "energy": 0.92},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
    # Adversarial: no song in the catalog is both "sad" and high-energy.
    "Edge Case - Sad but Hyped": {"genre": "pop", "mood": "sad", "energy": 0.9},
}


def print_recommendations(name: str, prefs: dict, recs: list) -> None:
    """Print one profile's top results as a table with scores and reasons."""
    print(f"Profile: {name}  (genre={prefs['genre']}, mood={prefs['mood']}, energy={prefs['energy']})")
    rows = [
        [rank, song["title"], song["artist"], f"{song['genre']}/{song['mood']}",
         f"{score:.2f}", explanation.replace("; ", "\n")]
        for rank, (song, score, explanation) in enumerate(recs, start=1)
    ]
    print(tabulate(rows, headers=["#", "Title", "Artist", "Genre/Mood", "Score", "Why"],
                   tablefmt="simple_grid", disable_numparse=True))
    print()


def main() -> None:
    """Load the catalog and print the top 5 for every profile."""
    songs = load_songs("data/songs.csv")

    experiment = "--experiment" in sys.argv
    diverse = "--diverse" in sys.argv
    weights = EXPERIMENT_WEIGHTS if experiment else DEFAULT_WEIGHTS
    print(f"Weights: {weights}{'  (EXPERIMENT)' if experiment else ''}")
    print(f"Diversity penalty: {'ON' if diverse else 'OFF'}\n")

    for name, prefs in PROFILES.items():
        recs = recommend_songs(prefs, songs, k=5, weights=weights, diverse=diverse)
        print_recommendations(name, prefs, recs)


if __name__ == "__main__":
    main()

"""
VibeFinder 1.0 - core recommendation logic.

Flow: load_songs (CSV -> list of dicts) -> score_song (judge ONE song)
      -> recommend_songs (judge EVERY song, sort, keep the top k).
"""

import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple

# The "Algorithm Recipe". Kept in one place so experiments change one line.
DEFAULT_WEIGHTS = {
    "genre": 2.0,   # exact genre match
    "mood": 1.0,    # exact mood match
    "energy": 1.0,  # max points for a perfect energy match
}

# Phase 4 experiment: energy counts double, genre counts half.
EXPERIMENT_WEIGHTS = {
    "genre": 1.0,
    "mood": 1.0,
    "energy": 2.0,
}

NUMERIC_FIELDS = {
    "id": int,
    "energy": float,
    "tempo_bpm": float,
    "valence": float,
    "danceability": float,
    "acousticness": float,
}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile object into the prefs dict that score_song expects."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user, best first."""
        prefs = _profile_to_prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda s: score_song(prefs, asdict(s))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable sentence listing why this song earned its points."""
        _, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV into a list of dicts, converting numeric columns to numbers."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field, cast in NUMERIC_FIELDS.items():
                row[field] = cast(row[field])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict, weights: Dict = None) -> Tuple[float, List[str]]:
    """Score one song against the user's prefs; return (score, list of reasons)."""
    w = weights or DEFAULT_WEIGHTS
    score = 0.0
    reasons = []

    if song["genre"].lower() == user_prefs["genre"].lower():
        score += w["genre"]
        reasons.append(f"genre match: {song['genre']} (+{w['genre']:.1f})")

    if song["mood"].lower() == user_prefs["mood"].lower():
        score += w["mood"]
        reasons.append(f"mood match: {song['mood']} (+{w['mood']:.1f})")

    # Closeness, not "more is better": a perfect match earns the full weight,
    # and points shrink as the gap between song and target grows.
    gap = abs(song["energy"] - user_prefs["energy"])
    energy_points = w["energy"] * (1 - gap)
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} (+{energy_points:.2f})"
    )

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    weights: Dict = None) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest-first, and return the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append((song, score, "; ".join(reasons)))
    # sorted() returns a NEW list and leaves `scored` untouched (.sort() would mutate it).
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]

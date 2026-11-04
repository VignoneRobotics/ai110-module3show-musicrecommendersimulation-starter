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

# Partial credit: labels in the same "family" earn PARTIAL_CREDIT x the full weight.
# Fixes the exact-match bias ("indie pop" earned nothing from a "pop" fan).
PARTIAL_CREDIT = 0.5
RELATED_GENRES = [
    {"pop", "indie pop"},
    {"hip-hop", "lofi"},        # lofi grew out of chilled-out hip-hop beats
    {"rock", "metal"},
    {"edm", "synthwave"},
    {"folk", "country"},
]
RELATED_MOODS = [
    {"chill", "relaxed", "peaceful", "focused"},
    {"intense", "angry"},
    {"happy", "playful", "euphoric"},
    {"sad", "moody", "nostalgic"},
]

# Diversity penalty (applied while picking the top k, not to the raw score).
ARTIST_REPEAT_PENALTY = 1.0   # per song by the same artist already picked
GENRE_REPEAT_PENALTY = 0.5    # per song of the same genre already picked

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


def _label_points(wanted: str, actual: str, families: List[set], weight: float) -> Tuple[float, str]:
    """Return (points, kind): full weight for an exact match, partial for a related label."""
    wanted, actual = wanted.lower(), actual.lower()
    if wanted == actual:
        return weight, "match"
    if any(wanted in fam and actual in fam for fam in families):
        return weight * PARTIAL_CREDIT, "related"
    return 0.0, ""


def score_song(user_prefs: Dict, song: Dict, weights: Dict = None) -> Tuple[float, List[str]]:
    """Score one song against the user's prefs; return (score, list of reasons)."""
    w = weights or DEFAULT_WEIGHTS
    score = 0.0
    reasons = []

    for feature, families in (("genre", RELATED_GENRES), ("mood", RELATED_MOODS)):
        points, kind = _label_points(user_prefs[feature], song[feature], families, w[feature])
        if kind == "match":
            reasons.append(f"{feature} match: {song[feature]} (+{points:.1f})")
        elif kind == "related":
            reasons.append(f"related {feature}: {song[feature]} ~ {user_prefs[feature]} (+{points:.1f})")
        score += points

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
                    weights: Dict = None, diverse: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score every song, then return the top k as (song, score, explanation), best first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append((song, score, "; ".join(reasons)))
    # sorted() returns a NEW list and leaves `scored` untouched (.sort() would mutate it).
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    if not diverse:
        return ranked[:k]
    return _diversify(ranked, k)


def _diversify(ranked: List[Tuple[Dict, float, str]], k: int) -> List[Tuple[Dict, float, str]]:
    """Greedy re-rank: pick one song at a time, penalizing artists/genres already picked."""
    picked, remaining = [], list(ranked)
    while remaining and len(picked) < k:
        best_i, best_score, best_note = 0, float("-inf"), ""
        for i, (song, score, _) in enumerate(remaining):
            same_artist = sum(p[0]["artist"] == song["artist"] for p in picked)
            same_genre = sum(p[0]["genre"] == song["genre"] for p in picked)
            penalty = same_artist * ARTIST_REPEAT_PENALTY + same_genre * GENRE_REPEAT_PENALTY
            if score - penalty > best_score:
                best_i, best_score = i, score - penalty
                best_note = f"diversity penalty (-{penalty:.1f})" if penalty else ""
        song, _, explanation = remaining.pop(best_i)
        if best_note:
            explanation = f"{explanation}; {best_note}"
        picked.append((song, round(best_score, 2), explanation))
    return picked

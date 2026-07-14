import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5
ACOUSTIC_THRESHOLD = 0.5

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        """Scores a single song against a user profile using the Algorithm Recipe weights."""
        score = 0.0
        if song.genre == user.favorite_genre:
            score += GENRE_WEIGHT
        if song.mood == user.favorite_mood:
            score += MOOD_WEIGHT
        score += ENERGY_WEIGHT * max(0.0, 1 - abs(song.energy - user.target_energy))
        acoustic_match = (song.acousticness > ACOUSTIC_THRESHOLD) == user.likes_acoustic
        if acoustic_match:
            score += ACOUSTIC_WEIGHT
        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Ranks all songs by score against the user profile and returns the top k."""
        ranked = sorted(self.songs, key=lambda song: self._score(user, song), reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Builds a human-readable reason string for why a song scored the way it did."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"matches your favorite genre ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"matches your favorite mood ({song.mood})")
        energy_gap = abs(song.energy - user.target_energy)
        if energy_gap <= 0.1:
            reasons.append(f"energy ({song.energy:.2f}) is close to your target ({user.target_energy:.2f})")
        acoustic_match = (song.acousticness > ACOUSTIC_THRESHOLD) == user.likes_acoustic
        if acoustic_match:
            reasons.append("fits your acoustic preference")
        if not reasons:
            return "No strong matches, included to fill out the list."
        return "Because it " + "; ".join(reasons) + "."

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        songs = []
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
        return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match (+{GENRE_WEIGHT})")

    if song["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match (+{MOOD_WEIGHT})")

    energy_gap = abs(song["energy"] - user_prefs["target_energy"])
    energy_score = ENERGY_WEIGHT * max(0.0, 1 - energy_gap)
    score += energy_score
    if energy_score > 0:
        reasons.append(f"energy similarity (+{energy_score:.2f})")

    acoustic_match = (song["acousticness"] > ACOUSTIC_THRESHOLD) == user_prefs["likes_acoustic"]
    if acoustic_match:
        score += ACOUSTIC_WEIGHT
        reasons.append(f"acoustic fit (+{ACOUSTIC_WEIGHT})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    return [
        (song, score, "; ".join(reasons) if reasons else "No strong matches, included to fill out the list.")
        for song, score, reasons in ranked[:k]
    ]

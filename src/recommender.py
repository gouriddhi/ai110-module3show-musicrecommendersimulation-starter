import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv into a list of dicts, converting numeric columns to int/float."""
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

# Highest possible score: genre 1.5 + mood 1.5 + energy 3.0 + acoustic 0.5
MAX_SCORE = 6.5

# Genres and moods that sound alike, so a near-miss earns partial credit
RELATED_GENRES = [
    {"rock", "metal", "pop punk"},
    {"lofi", "ambient"},
    {"edm", "synthwave"},
]
RELATED_MOODS = [
    {"intense", "angry"},
    {"chill", "relaxed", "peaceful"},
    {"sad", "nostalgic", "bitter"},
    {"happy", "euphoric"},
]

def is_related(a: str, b: str, families: List[set]) -> bool:
    """Return True if a and b belong to the same family of related labels."""
    return any(a in family and b in family for family in families)

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return (score, list of reasons)."""
    score = 0.0
    reasons = []

    # Genre: +1.5 exact match, +0.75 partial match (one name contains the other, or related genres)
    fav_genre = user_prefs["favorite_genre"].strip().lower()
    song_genre = song["genre"].strip().lower()
    if song_genre == fav_genre:
        score += 1.5
        reasons.append(f"genre match: {song['genre']} (+1.5)")
    elif fav_genre in song_genre or song_genre in fav_genre:
        score += 0.75
        reasons.append(f"partial genre match: {song['genre']} ~ {user_prefs['favorite_genre']} (+0.75)")
    elif is_related(fav_genre, song_genre, RELATED_GENRES):
        score += 0.75
        reasons.append(f"related genre: {song['genre']} ~ {user_prefs['favorite_genre']} (+0.75)")

    # Mood: +1.5 exact match, +0.75 related mood
    fav_mood = user_prefs["favorite_mood"].strip().lower()
    song_mood = song["mood"].strip().lower()
    if song_mood == fav_mood:
        score += 1.5
        reasons.append(f"mood match: {song['mood']} (+1.5)")
    elif is_related(fav_mood, song_mood, RELATED_MOODS):
        score += 0.75
        reasons.append(f"related mood: {song['mood']} ~ {user_prefs['favorite_mood']} (+0.75)")

    # Energy closeness: 3.0 * (1 - |target - energy|), 0 to +3.0
    target = user_prefs["target_energy"]
    energy_points = 3.0 * (1 - abs(target - song["energy"]))
    score += energy_points
    reasons.append(f"energy {song['energy']:.2f} vs. target {target:.2f} (+{energy_points:.2f})")

    # Acoustic fit: rewards acoustic songs if liked, produced songs otherwise, 0 to +0.5
    if user_prefs["likes_acoustic"]:
        acoustic_points = 0.5 * song["acousticness"]
        reasons.append(f"acoustic sound (+{acoustic_points:.2f})")
    else:
        acoustic_points = 0.5 * (1 - song["acousticness"])
        reasons.append(f"produced/electronic sound (+{acoustic_points:.2f})")
    score += acoustic_points

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank all songs by score (ties by energy closeness) and return the top k as (song, score, explanation)."""
    target = user_prefs["target_energy"]
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Highest score first; ties go to the song whose energy is closer to the target
    ranked = sorted(
        scored,
        key=lambda item: (-item[1], abs(target - item[0]["energy"])),
    )

    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]

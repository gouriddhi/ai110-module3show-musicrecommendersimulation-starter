"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


# Taste profiles to compare side by side
PROFILES = {
    # A listener into mellow, emotional pop ballads
    "Sad Pop Ballads": {
        "favorite_genre": "pop",
        "favorite_mood": "sad",
        "target_energy": 0.45,   # calm-to-mid energy, not quiet ambient or loud tracks
        "likes_acoustic": True,  # prefers piano/guitar-driven sound over heavy production
    },
    # Upbeat, polished pop for workouts and parties
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "likes_acoustic": False,
    },
    # Quiet, soft background music for studying
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    # Loud, driving guitar music
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Print one profile's recommendations as a formatted terminal report."""
    width = 60
    print()
    print("=" * width)
    print(f" {name}: top {len(recommendations)} recommendations".center(width))
    print(f" {user_prefs['favorite_genre']} / {user_prefs['favorite_mood']} / "
          f"energy {user_prefs['target_energy']:.2f}".center(width))
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print()
        print(f" #{rank}  {song['title']} by {song['artist']}")
        print(f"     Score: {score:.2f} / 6.00")
        for reason in explanation.split("; "):
            print(f"       - {reason}")

    print()
    print("=" * width)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()

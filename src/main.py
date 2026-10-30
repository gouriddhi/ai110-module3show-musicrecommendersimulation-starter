"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile: a listener into mellow, emotional pop ballads
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "sad",
        "target_energy": 0.45,   # calm-to-mid energy, not quiet ambient or loud tracks
        "likes_acoustic": True,  # prefers piano/guitar-driven sound over heavy production
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 60
    print()
    print("=" * width)
    print(f" Top {len(recommendations)} recommendations".center(width))
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


if __name__ == "__main__":
    main()

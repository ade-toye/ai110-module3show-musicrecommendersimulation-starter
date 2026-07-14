"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from src.recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile: target values the recommender compares each song against.
    # Keys match the UserProfile fields (favorite_genre, favorite_mood,
    # target_energy, likes_acoustic) so score_song can use the same names
    # whether it's given a UserProfile or a plain dict.
    user_prefs = {
        "favorite_genre": "afrobeats",
        "favorite_mood": "romantic",
        "target_energy": 0.6,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    header = f"Top {len(recommendations)} Recommendations for {user_prefs['favorite_genre']} / {user_prefs['favorite_mood']}"
    print(f"\n{header}")
    print("=" * len(header))
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} — {song['artist']}")
        print(f"   Score:   {score:.2f}")
        print(f"   Reasons: {explanation}")


if __name__ == "__main__":
    main()

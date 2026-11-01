# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube combine two main approaches. **Collaborative filtering** recommends what similar listeners played, skipped, or saved ("people who liked X also liked Y"). **Content-based filtering** compares the attributes of the songs themselves, such as genre, tempo, energy, and mood. Large systems blend both with signals like listening history, time of day, and context, and they retrain constantly on millions of users. My version is a small content-based recommender: it has no other users to learn from, so it scores each song by how well its attributes match a single user's taste profile. It prioritizes **genre** first (the most stable sign of taste), then **mood**, then how **close** a song's energy is to the user's target. Closeness matters more than whether a value is simply higher or lower, so a user who wants calm music gets calm songs instead of the most intense ones. Acousticness acts as a small tiebreaker, and every recommendation comes with a plain-language explanation of why it was chosen.

**`Song` features**

| Feature | Type | Used in scoring? |
|---|---|---|
| `id`, `title`, `artist` | int / str | No, used for identification and display |
| `genre` | str | Yes: +2.0 for an exact match, +1.0 for a partial match (e.g. "indie pop" vs. "pop") |
| `mood` | str | Yes: +1.5 for a match |
| `energy` | float (0–1) | Yes: up to +2.0, based on closeness to the user's target |
| `acousticness` | float (0–1) | Yes: up to +0.5, based on the user's acoustic preference |
| `valence` | float (0–1) | Not yet; candidate for experiments (sad ↔ happy) |
| `tempo_bpm` | float | No; tracks energy closely (correlation 0.71) and is on a different scale (60–168 BPM) |
| `danceability` | float (0–1) | No; largely overlaps with energy (correlation 0.69) |

**`UserProfile` features**

| Feature | Type | Purpose |
|---|---|---|
| `favorite_genre` | str | Compared with `Song.genre` |
| `favorite_mood` | str | Compared with `Song.mood` |
| `target_energy` | float (0–1) | The energy level the user wants; songs closer to it score higher |
| `likes_acoustic` | bool | True rewards acoustic songs; False rewards electronic/produced ones |

### Data Flow

```
INPUT     data/songs.csv ──load_songs()──► list of song dicts (numeric columns cast to float)
          user_prefs = {favorite_genre, favorite_mood, target_energy, likes_acoustic}
             │
             ▼
PROCESS   for each song: score_song(user_prefs, song) ──► (score, reasons)
          every song is judged on its own; no song sees any other song
             │
             ▼
OUTPUT    sort by score (highest first) ──► top k ──► [(song, score, explanation), ...]
```

Example: `drivers license` (pop, sad, energy 0.43, acousticness 0.72) for a pop / sad / 0.45 / acoustic user scores
2.0 (genre) + 1.5 (mood) + 1.96 (energy) + 0.36 (acoustic) = **5.82** and ranks #1.

### Algorithm Recipe

**Step 1: Score every song** (maximum 6.0 points). Each rule that awards points also adds a reason to the song's explanation.

| Rule | Points |
|---|---|
| **Genre**: exact match with `favorite_genre` | +2.0 |
| **Genre**: partial match, where one name contains the other (e.g. "indie pop" or "pop punk" for a "pop" fan) | +1.0 |
| **Mood**: exact match with `favorite_mood` | +1.5 |
| **Energy closeness**: `2.0 × (1 − \|target_energy − song.energy\|)` | 0 to +2.0 |
| **Acoustic fit**: `0.5 × acousticness` if `likes_acoustic`, otherwise `0.5 × (1 − acousticness)` | 0 to +0.5 |

**Step 2: Rank.** Sort songs from highest to lowest score. If two songs tie, the one whose energy is closer to the target ranks higher.

**Step 3: Recommend.** Return the top `k` songs (default 5), each with its score and an explanation such as *"matches your favorite genre (pop); matches your mood (sad); energy 0.43 is close to your target 0.45"*.

**Why these rules**

- **Genre is worth the most** because it is the most stable sign of a listener's taste.
- **Mood is worth nearly as much (+1.5).** With the original +1.0, a genre-only match (about 3 points) easily beat a song that fit the listener's mood and energy. At +1.5, mood plus close energy (about 3.5) can compete with genre alone, and genre plus a good vibe beats either one.
- **Energy has the largest continuous weight** because genre and mood are sparse in this catalog (15 genres and 14 moods across 20 songs). Most songs match neither, so energy is what separates them.
- **Energy is scored by distance, not size.** A user who wants 0.45 should get songs near 0.45, not the most or least intense songs in the catalog.
- **Acousticness is worth little** because in this dataset it is almost the exact opposite of energy (correlation −0.97). A larger weight would count the same signal twice.
- **Partial genre credit** stops related genres from being treated as total mismatches.

### Expected Biases

- **Genre over-prioritization.** The +2.0 genre bonus can outweigh a large energy and mood mismatch. For a sad, low-energy pop fan, the high-energy *Gym Hero* (pop, intense, 0.93) still ranks #4, ahead of calmer songs that fit the mood better.
- **Exact-label matching.** Mood is compared as an exact string, so "nostalgic" or "bitter" earns nothing for a "sad" listener even though they are emotionally close. Partial genre credit only helps when the names share a word ("indie pop" ↔ "pop"), not when genres are related in sound (lofi ↔ ambient).
- **Catalog imbalance.** Pop-family genres make up 8 of the 20 songs, so pop fans get many partial matches while metal, classical, or jazz fans get one genre match at most. Their lists fill up with songs chosen on energy alone.
- **Hidden double-counting.** Acousticness is almost the inverse of energy (correlation −0.97), so the acoustic bonus quietly rewards low energy a second time. Its small weight (0.5) limits this, but it still slightly favors calm songs for acoustic fans.
- **One taste per user.** The profile holds a single genre and a single mood, so listeners with mixed or situational tastes are reduced to one slice of what they like.

Adding a `target_valence` (happiness) preference and testing a lower genre weight (+1.5) are the first planned experiments.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python3 src/main.py`, which loads all 20 songs (`Loaded songs: 20`) and runs each taste profile below.

### Sad Pop Ballads

`favorite_genre=pop`, `favorite_mood=sad`, `target_energy=0.45`, `likes_acoustic=True`

```
============================================================
           Sad Pop Ballads: top 5 recommendations
                   pop / sad / energy 0.45
============================================================

 #1  drivers license by Olivia Rodrigo
     Score: 5.82 / 6.00
       - genre match: pop (+2.0)
       - mood match: sad (+1.5)
       - energy 0.43 vs. target 0.45 (+1.96)
       - acoustic sound (+0.36)

 #2  Sunrise City by Neon Echo
     Score: 3.35 / 6.00
       - genre match: pop (+2.0)
       - energy 0.82 vs. target 0.45 (+1.26)
       - acoustic sound (+0.09)

 #3  I Love You I'm Sorry by Gracie Abrams
     Score: 3.26 / 6.00
       - partial genre match: indie pop ~ pop (+1.0)
       - energy 0.38 vs. target 0.45 (+1.86)
       - acoustic sound (+0.40)

 #4  Gym Hero by Max Pulse
     Score: 3.06 / 6.00
       - genre match: pop (+2.0)
       - energy 0.93 vs. target 0.45 (+1.04)
       - acoustic sound (+0.03)

 #5  good 4 u by Olivia Rodrigo
     Score: 2.75 / 6.00
       - partial genre match: pop punk ~ pop (+1.0)
       - energy 0.66 vs. target 0.45 (+1.58)
       - acoustic sound (+0.17)

============================================================
```

### High-Energy Pop

`favorite_genre=pop`, `favorite_mood=happy`, `target_energy=0.85`, `likes_acoustic=False`

```
============================================================
           High-Energy Pop: top 5 recommendations
                  pop / happy / energy 0.85
============================================================

 #1  Sunrise City by Neon Echo
     Score: 5.85 / 6.00
       - genre match: pop (+2.0)
       - mood match: happy (+1.5)
       - energy 0.82 vs. target 0.85 (+1.94)
       - produced/electronic sound (+0.41)

 #2  Rooftop Lights by Indigo Parade
     Score: 4.65 / 6.00
       - partial genre match: indie pop ~ pop (+1.0)
       - mood match: happy (+1.5)
       - energy 0.76 vs. target 0.85 (+1.82)
       - produced/electronic sound (+0.33)

 #3  Gym Hero by Max Pulse
     Score: 4.31 / 6.00
       - genre match: pop (+2.0)
       - energy 0.93 vs. target 0.85 (+1.84)
       - produced/electronic sound (+0.47)

 #4  drivers license by Olivia Rodrigo
     Score: 3.30 / 6.00
       - genre match: pop (+2.0)
       - energy 0.43 vs. target 0.85 (+1.16)
       - produced/electronic sound (+0.14)

 #5  Here Comes the Sun by The Beatles
     Score: 3.23 / 6.00
       - mood match: happy (+1.5)
       - energy 0.55 vs. target 0.85 (+1.40)
       - produced/electronic sound (+0.33)

============================================================
```

### Chill Lofi

`favorite_genre=lofi`, `favorite_mood=chill`, `target_energy=0.35`, `likes_acoustic=True`

```
============================================================
              Chill Lofi: top 5 recommendations
                 lofi / chill / energy 0.35
============================================================

 #1  Library Rain by Paper Lanterns
     Score: 5.93 / 6.00
       - genre match: lofi (+2.0)
       - mood match: chill (+1.5)
       - energy 0.35 vs. target 0.35 (+2.00)
       - acoustic sound (+0.43)

 #2  Midnight Coding by LoRoom
     Score: 5.71 / 6.00
       - genre match: lofi (+2.0)
       - mood match: chill (+1.5)
       - energy 0.42 vs. target 0.35 (+1.86)
       - acoustic sound (+0.35)

 #3  Focus Flow by LoRoom
     Score: 4.29 / 6.00
       - genre match: lofi (+2.0)
       - energy 0.40 vs. target 0.35 (+1.90)
       - acoustic sound (+0.39)

 #4  Spacewalk Thoughts by Orbit Bloom
     Score: 3.82 / 6.00
       - mood match: chill (+1.5)
       - energy 0.28 vs. target 0.35 (+1.86)
       - acoustic sound (+0.46)

 #5  Coffee Shop Stories by Slow Stereo
     Score: 2.40 / 6.00
       - energy 0.37 vs. target 0.35 (+1.96)
       - acoustic sound (+0.45)

============================================================
```

### Deep Intense Rock

`favorite_genre=rock`, `favorite_mood=intense`, `target_energy=0.9`, `likes_acoustic=False`

```
============================================================
          Deep Intense Rock: top 5 recommendations
                rock / intense / energy 0.90
============================================================

 #1  Storm Runner by Voltline
     Score: 5.93 / 6.00
       - genre match: rock (+2.0)
       - mood match: intense (+1.5)
       - energy 0.91 vs. target 0.90 (+1.98)
       - produced/electronic sound (+0.45)

 #2  Gym Hero by Max Pulse
     Score: 3.92 / 6.00
       - mood match: intense (+1.5)
       - energy 0.93 vs. target 0.90 (+1.94)
       - produced/electronic sound (+0.47)

 #3  Here Comes the Sun by The Beatles
     Score: 3.62 / 6.00
       - genre match: rock (+2.0)
       - energy 0.55 vs. target 0.90 (+1.30)
       - produced/electronic sound (+0.33)

 #4  Laser Bloom by Kinetic Drift
     Score: 2.38 / 6.00
       - energy 0.95 vs. target 0.90 (+1.90)
       - produced/electronic sound (+0.48)

 #5  Iron Tempest by Graveforge
     Score: 2.35 / 6.00
       - energy 0.97 vs. target 0.90 (+1.86)
       - produced/electronic sound (+0.48)

============================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this




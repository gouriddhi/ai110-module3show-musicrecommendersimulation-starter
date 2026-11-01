# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version is **VibeCheck 1.0**, a command-line recommender for a 20-song catalog. You give it a taste profile: a favorite genre, a favorite mood, a target energy level, and whether you like acoustic music. It scores every song out of 6.5 points, giving the most weight to how close a song's energy is to your target, with partial credit for related genres and moods (like metal for a rock fan). It prints the top 5 songs, each with the reasons behind its score. I tested it on four taste profiles and a set of tricky edge cases, tried several weight settings, and documented the biases I found.

---

## How The System Works

Real-world platforms like Spotify and YouTube combine two main approaches. **Collaborative filtering** recommends what similar listeners played, skipped, or saved ("people who liked X also liked Y"). **Content-based filtering** compares the attributes of the songs themselves, such as genre, tempo, energy, and mood. Large systems blend both with signals like listening history, time of day, and context, and they retrain constantly on millions of users. My version is a small content-based recommender: it has no other users to learn from, so it scores each song by how well its attributes match a single user's taste profile. It rewards a matching **genre** and **mood** (with partial credit for related ones, like metal for a rock fan), and gives the most weight to how **close** a song's energy is to the user's target. Closeness matters more than whether a value is simply higher or lower, so a user who wants calm music gets calm songs instead of the most intense ones. Acousticness acts as a small tiebreaker, and every recommendation comes with a plain-language explanation of why it was chosen.

**`Song` features**

| Feature | Type | Used in scoring? |
|---|---|---|
| `id`, `title`, `artist` | int / str | No, used for identification and display |
| `genre` | str | Yes: +1.5 for an exact match, +0.75 for a partial or related match (e.g. "indie pop" or "metal" for a rock fan) |
| `mood` | str | Yes: +1.5 for an exact match, +0.75 for a related mood (e.g. "angry" for "intense") |
| `energy` | float (0–1) | Yes: up to +3.0, based on closeness to the user's target |
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
1.5 (genre) + 1.5 (mood) + 2.94 (energy) + 0.36 (acoustic) = **6.30** and ranks #1.

### Algorithm Recipe

**Step 1: Score every song** (maximum 6.5 points). Each rule that awards points also adds a reason to the song's explanation.

| Rule | Points |
|---|---|
| **Genre**: exact match with `favorite_genre` | +1.5 |
| **Genre**: partial match, where one name contains the other (e.g. "indie pop" or "pop punk" for a "pop" fan) | +0.75 |
| **Genre**: related genre (rock ↔ metal ↔ pop punk, lofi ↔ ambient, edm ↔ synthwave) | +0.75 |
| **Mood**: exact match with `favorite_mood` | +1.5 |
| **Mood**: related mood (intense ↔ angry, chill ↔ relaxed ↔ peaceful, sad ↔ nostalgic ↔ bitter, happy ↔ euphoric) | +0.75 |
| **Energy closeness**: `3.0 × (1 − \|target_energy − song.energy\|)` | 0 to +3.0 |
| **Acoustic fit**: `0.5 × acousticness` if `likes_acoustic`, otherwise `0.5 × (1 − acousticness)` | 0 to +0.5 |

**Step 2: Rank.** Sort songs from highest to lowest score. If two songs tie, the one whose energy is closer to the target ranks higher.

**Step 3: Recommend.** Return the top `k` songs (default 5), each with its score and an explanation such as *"genre match: pop (+1.5); mood match: sad (+1.5); energy 0.43 vs. target 0.45 (+2.94)"*.

**Why these rules**

- **Genre and mood are worth the same (+1.5).** Genre started at +2.0, but that let a song win on its label alone, such as a gentle Beatles song for an intense-rock fan (see Experiments). Mood started at +1.0, which let a genre-only match easily beat a song that fit the listener's mood and energy.
- **Energy has the largest weight (up to +3.0)** because genre and mood are sparse in this catalog (13 genres and 14 moods across 20 songs). Most songs match neither, so energy is what separates them.
- **Energy is scored by distance, not size.** A user who wants 0.45 should get songs near 0.45, not the most or least intense songs in the catalog.
- **Acousticness is worth little** because in this dataset it is almost the exact opposite of energy (correlation −0.97). A larger weight would count the same signal twice.
- **Partial and related credit** (half of an exact match) stops similar genres and moods from being treated as total mismatches. Without it, metal earned nothing for a rock fan and "nostalgic" earned nothing for a sad listener.

### Expected Biases

- **Genre over-prioritization.** A genre bonus can still outweigh a large energy and mood mismatch. With the original +2.0, the high-energy *Gym Hero* (pop, intense, 0.93) ranked #4 for a sad, low-energy pop fan. Lowering genre to +1.5 pushed it out of that list, but *Here Comes the Sun* still makes the intense-rock list on its label alone.
- **Hand-picked similarity.** Related genres and moods only get partial credit when they are listed in `RELATED_GENRES` or `RELATED_MOODS`. Those lists reflect my own judgment, and any label left out (for example jazz, classical, or "moody") is still treated as a total mismatch.
- **Catalog imbalance.** Pop-family genres make up 8 of the 20 songs, so pop fans get many partial matches while metal, classical, or jazz fans get one genre match at most. Their lists fill up with songs chosen on energy alone.
- **Hidden double-counting.** Acousticness is almost the inverse of energy (correlation −0.97), so the acoustic bonus quietly rewards low energy a second time. Its small weight (0.5) limits this, but it still slightly favors calm songs for acoustic fans.
- **One taste per user.** The profile holds a single genre and a single mood, so listeners with mixed or situational tastes are reduced to one slice of what they like.

Adding a `target_valence` (happiness) preference is the next planned experiment.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

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
     Score: 6.30 / 6.50
       - genre match: pop (+1.5)
       - mood match: sad (+1.5)
       - energy 0.43 vs. target 0.45 (+2.94)
       - acoustic sound (+0.36)

 #2  I Love You I'm Sorry by Gracie Abrams
     Score: 4.69 / 6.50
       - partial genre match: indie pop ~ pop (+0.75)
       - related mood: nostalgic ~ sad (+0.75)
       - energy 0.38 vs. target 0.45 (+2.79)
       - acoustic sound (+0.40)

 #3  That's So True by Gracie Abrams
     Score: 3.81 / 6.50
       - partial genre match: indie pop ~ pop (+0.75)
       - related mood: bitter ~ sad (+0.75)
       - energy 0.72 vs. target 0.45 (+2.19)
       - acoustic sound (+0.12)

 #4  Sunrise City by Neon Echo
     Score: 3.48 / 6.50
       - genre match: pop (+1.5)
       - energy 0.82 vs. target 0.45 (+1.89)
       - acoustic sound (+0.09)

 #5  good 4 u by Olivia Rodrigo
     Score: 3.29 / 6.50
       - partial genre match: pop punk ~ pop (+0.75)
       - energy 0.66 vs. target 0.45 (+2.37)
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
     Score: 6.32 / 6.50
       - genre match: pop (+1.5)
       - mood match: happy (+1.5)
       - energy 0.82 vs. target 0.85 (+2.91)
       - produced/electronic sound (+0.41)

 #2  Rooftop Lights by Indigo Parade
     Score: 5.31 / 6.50
       - partial genre match: indie pop ~ pop (+0.75)
       - mood match: happy (+1.5)
       - energy 0.76 vs. target 0.85 (+2.73)
       - produced/electronic sound (+0.33)

 #3  Gym Hero by Max Pulse
     Score: 4.73 / 6.50
       - genre match: pop (+1.5)
       - energy 0.93 vs. target 0.85 (+2.76)
       - produced/electronic sound (+0.47)

 #4  Laser Bloom by Kinetic Drift
     Score: 3.93 / 6.50
       - related mood: euphoric ~ happy (+0.75)
       - energy 0.95 vs. target 0.85 (+2.70)
       - produced/electronic sound (+0.48)

 #5  Here Comes the Sun by The Beatles
     Score: 3.93 / 6.50
       - mood match: happy (+1.5)
       - energy 0.55 vs. target 0.85 (+2.10)
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
     Score: 6.43 / 6.50
       - genre match: lofi (+1.5)
       - mood match: chill (+1.5)
       - energy 0.35 vs. target 0.35 (+3.00)
       - acoustic sound (+0.43)

 #2  Midnight Coding by LoRoom
     Score: 6.14 / 6.50
       - genre match: lofi (+1.5)
       - mood match: chill (+1.5)
       - energy 0.42 vs. target 0.35 (+2.79)
       - acoustic sound (+0.35)

 #3  Spacewalk Thoughts by Orbit Bloom
     Score: 5.50 / 6.50
       - related genre: ambient ~ lofi (+0.75)
       - mood match: chill (+1.5)
       - energy 0.28 vs. target 0.35 (+2.79)
       - acoustic sound (+0.46)

 #4  Focus Flow by LoRoom
     Score: 4.74 / 6.50
       - genre match: lofi (+1.5)
       - energy 0.40 vs. target 0.35 (+2.85)
       - acoustic sound (+0.39)

 #5  Coffee Shop Stories by Slow Stereo
     Score: 4.13 / 6.50
       - related mood: relaxed ~ chill (+0.75)
       - energy 0.37 vs. target 0.35 (+2.94)
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
     Score: 6.42 / 6.50
       - genre match: rock (+1.5)
       - mood match: intense (+1.5)
       - energy 0.91 vs. target 0.90 (+2.97)
       - produced/electronic sound (+0.45)

 #2  Gym Hero by Max Pulse
     Score: 4.88 / 6.50
       - mood match: intense (+1.5)
       - energy 0.93 vs. target 0.90 (+2.91)
       - produced/electronic sound (+0.47)

 #3  Iron Tempest by Graveforge
     Score: 4.78 / 6.50
       - related genre: metal ~ rock (+0.75)
       - related mood: angry ~ intense (+0.75)
       - energy 0.97 vs. target 0.90 (+2.79)
       - produced/electronic sound (+0.48)

 #4  good 4 u by Olivia Rodrigo
     Score: 4.12 / 6.50
       - related genre: pop punk ~ rock (+0.75)
       - related mood: angry ~ intense (+0.75)
       - energy 0.66 vs. target 0.90 (+2.28)
       - produced/electronic sound (+0.33)

 #5  Here Comes the Sun by The Beatles
     Score: 3.78 / 6.50
       - genre match: rock (+1.5)
       - energy 0.55 vs. target 0.90 (+1.95)
       - produced/electronic sound (+0.33)

============================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

I ran each experiment against the same four taste profiles (Sad Pop Ballads, High-Energy Pop, Chill Lofi, Deep Intense Rock) and compared their top 5 lists.

**1. Related genres and moods.** Originally, partial credit only applied when one genre name contained the other ("pop" inside "pop punk"). For the Deep Intense Rock profile, the metal song *Iron Tempest* (angry, energy 0.97) ranked #5 behind the gentle *Here Comes the Sun*, which won on its "rock" label alone. I added short lists of related genres and moods that earn half credit.

- *Iron Tempest* jumped from #5 to #2 for Deep Intense Rock.
- The nostalgic and bitter Gracie Abrams songs moved up for Sad Pop Ballads, above the upbeat *Sunrise City*.
- Every #1 stayed the same.

**2. Weight shift.** I tested how sensitive the rankings are to the genre and energy weights.

| Setting | Genre (exact) | Energy (max) | Max score | What happened |
|---|---|---|---|---|
| Original | 2.0 | 2.0 | 6.0 | Songs won on genre labels alone: the slow ballad *drivers license* ranked #4 for High-Energy Pop, and *Gym Hero* made the Sad Pop Ballads list. |
| Big shift (genre halved, energy doubled) | 1.0 | 4.0 | 7.0 | The label-only mistakes disappeared, but lists drifted across genres. Sad Pop Ballads picked up two calm lofi study tracks, and EDM entered the rock list. |
| **Middle (kept)** | **1.5** | **3.0** | **6.5** | Kept the fixes from the big shift while staying on genre. All five Sad Pop Ballads picks are pop-family songs, and *Laser Bloom* replaced *drivers license* for High-Energy Pop. |

- **The #1 song never changed** for any profile across all three settings, because each #1 matches on every rule.
- **Chill Lofi stayed the same in every setting.** Its genre, mood, and energy all point to the same songs.
- **The weight shift made results more accurate, not just different,** but it overcorrected at the extreme. The middle setting is now the default.

---

## Limitations and Risks

- **Tiny, uneven catalog.** There are only 20 songs, and 7 of them are pop-type. Pop fans get several strong matches, while fans of hip hop, EDM, synthwave, or metal have one song in their genre.
- **Labels, not sound.** It only sees genre and mood labels plus a few numbers. It can't hear the music or understand lyrics, so a pop workout song can still land in a sad-pop list.
- **"Acoustic" means "calm."** No song is both acoustic and high-energy, so someone who likes loud acoustic music can't be served.
- **Hand-picked similarity.** Related genres and moods only get partial credit if they're in my lists. Labels with no relatives (like hip hop or "confident") only score on an exact match, so those songs are rarely recommended.
- **No input checks.** An empty genre gives every song points, energy outside 0 to 1 gives negative points, and missing or text values can crash the program.
- **One taste per person.** Each profile allows one genre and one mood, so mixed tastes get flattened.

See Sections 5 and 6 of the [model card](model_card.md) for the numbers behind these.

---

## Reflection

See the full [**Model Card**](model_card.md) for details on the data, scoring, evaluation, and biases.

Building this showed me that a recommender doesn't "know" music. It turns each song into a few numbers and labels, compares them to what the listener asked for, and adds up points. That simple process still feels personal. When *drivers license* came back first for my sad-pop profile, with reasons attached, it felt like the app understood the request. But the same rules also put a gym anthem in that sad list, because it matched on genre. A prediction is only as good as the features it can see. My system can't hear that *Gym Hero* sounds pumped up, not sad. It only sees "pop" and an energy number.

I also learned that bias can come from the data, not just the rules. My scoring treats every user the same way, but the catalog doesn't. Pop-type songs make up 7 of the 20, so pop fans get several strong matches, while hip hop or metal fans get one and then songs picked mostly on energy. Labels add more bias: until I added related genres, a metal song got zero credit for a rock fan, and songs whose mood had no "similar" match were almost never recommended. In a real app with millions of users, these gaps would decide which artists get heard and which listeners get worse suggestions, often without anyone noticing.




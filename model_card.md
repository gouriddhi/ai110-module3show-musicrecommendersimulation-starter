# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeCheck 1.0**

It checks how well each song matches your vibe: your favorite genre, your mood, and how much energy you want.

---

## 2. Goal / Task

VibeCheck suggests songs a listener will probably enjoy.

You tell it four things about your taste. It scores every song in the catalog against that taste. Then it shows you the top 5, with a short reason for each pick.

It does not learn from other users. It only compares the songs' own features to what you asked for. This is called content-based filtering.

---

## 3. Data Used

- **Size:** 20 songs. The starter file had 10. I added 10 more to cover more genres and moods.
- **Features per song:** title, artist, genre, mood, energy, tempo, valence (happiness), danceability, and acousticness. The number features run from 0 to 1, except tempo, which is in beats per minute.
- **Variety:** 13 genres and 14 moods. Most genres have only one song.
- **What the model uses:** genre, mood, energy, and acousticness. It ignores tempo and danceability because they mostly repeat what energy says. It ignores valence for now.

**Limits of the data:**

- It is tiny. Real apps have millions of songs.
- It leans toward pop. 7 of the 20 songs are pop or a pop mix (indie pop, country pop, pop punk).
- There are gaps in energy. Nothing is calmer than 0.18, and only one song sits between 0.43 and 0.66.
- No song is both acoustic and high-energy. So there is nothing for someone who likes loud acoustic music.
- There are no lyrics, languages, release dates, or listening history.

---

## 4. Algorithm Summary

Each song gets points out of 6.5. Higher means a better match.

- **Genre (up to 1.5 points).** Same genre gets 1.5. A close genre gets 0.75. For example, "indie pop" for a pop fan, or metal for a rock fan.
- **Mood (up to 1.5 points).** Same mood gets 1.5. A similar mood gets 0.75. For example, "angry" for someone who wants "intense."
- **Energy (up to 3 points).** This is the biggest part. The closer a song's energy is to what you want, the more points it gets. A song right on target gets all 3. So if you want calm music, you get calm music, not the loudest songs.
- **Acoustic sound (up to 0.5 points).** A small bonus if the song matches your taste for acoustic or electronic sound. It stays small because acoustic songs here are almost always calm, so a big bonus would count calmness twice.

The points are added up. Songs are sorted from highest to lowest. If two songs tie, the one with closer energy wins. The top 5 are shown with their reasons, like "genre match: pop (+1.5)."

**How it changed over time.** The starter code did no scoring. It just returned the first 5 songs. I built the point system. Then I made three changes after testing:

1. I raised mood from 1 to 1.5 points. Before, genre alone beat songs that fit the mood.
2. I added partial credit for similar genres and moods. Before, metal got zero points for a rock fan.
3. I lowered genre from 2 to 1.5 points and raised energy from 2 to 3. Before, songs could win on their genre label alone.

---

## 5. Observed Behavior / Biases

**Pop fans get better results.** The catalog has 7 pop-type songs. So a pop fan always has several good matches. A hip hop, EDM, synthwave, or metal fan has only one song in their genre. When I tested every possible taste, a pop fan's best match scored 4.75 on average. For those one-song genres, it was only about 4.25. Their lists fill up with songs that just have similar energy. The rules are the same for everyone, but the data is not.

**Other patterns I noticed:**

- **"Likes acoustic" really means "likes calm."** No song is both acoustic and energetic, so the two settings always point to the same songs.
- **Some songs almost never get picked.** *Concrete Crown* (hip hop, "confident") made a top 5 only 12% of the time. *Spacewalk Thoughts* (ambient, "chill") made it 42% of the time. Songs with no "similar" genres or moods only score on an exact match.
- **The same artist can show up twice.** This happened in 37% of tested tastes. Nothing in the rules asks for variety.

**Strengths.** When the catalog has a song that fits, VibeCheck finds it. Every profile's #1 pick was a near-perfect match. Calm, well-stocked tastes like lofi get a strong list all the way down.

---

## 6. Evaluation Process

**Profiles I tested.** I used four main tastes:

| Profile | Genre | Mood | Energy | Acoustic? |
|---|---|---|---|---|
| Sad Pop Ballads | pop | sad | 0.45 | Yes |
| High-Energy Pop | pop | happy | 0.85 | No |
| Chill Lofi | lofi | chill | 0.35 | Yes |
| Deep Intense Rock | rock | intense | 0.90 | No |

I also tried 12 tricky tastes. Examples: sad music at very high energy, a genre not in the catalog, an empty genre, energy outside 0 to 1, and settings typed as text.

**What I looked for.** I read each top 5 and asked: would this actually feel right to that listener? I watched for songs that ranked high on one label but sounded wrong.

**What surprised me.**

- The #1 song never changed in any experiment. The rest of the list changed a lot.
- At first, a gentle Beatles song beat a heavy metal song for the rock fan, just because it was labeled "rock."
- The workout song *Gym Hero* showed up in 3 of the 4 lists, even the sad one.
- The tricky tastes found bugs. An empty genre gave every song points. Energy above 1 gave negative points. The text "False" was treated as true. Two inputs crashed the program.

**Experiments I ran.**

- **Similar genres and moods.** The metal song jumped from #5 to #2 for the rock fan.
- **Weight shift.** I tried three settings. The original let labels win too easily. The big shift (genre halved, energy doubled) let lofi songs into the sad-pop list. The middle setting (genre 1.5, energy 3) worked best, so I kept it.
- **Every possible taste.** I ran all 1,820 combinations and counted how often each song was picked. The most-picked song showed up 3.7 times as often as the least-picked one.

I also checked that each song's reasons always add up to its score.

### Comparing profiles side by side

| Rank | Sad Pop Ballads | High-Energy Pop | Chill Lofi | Deep Intense Rock |
|---|---|---|---|---|
| #1 | drivers license | Sunrise City | Library Rain | Storm Runner |
| #2 | I Love You I'm Sorry | Rooftop Lights | Midnight Coding | Gym Hero |
| #3 | That's So True | Gym Hero | Spacewalk Thoughts | Iron Tempest |
| #4 | Sunrise City | Laser Bloom | Focus Flow | good 4 u |
| #5 | good 4 u | Here Comes the Sun | Coffee Shop Stories | Here Comes the Sun |

**Sad Pop vs. High-Energy Pop.** Same genre, opposite moods and energy. The sad list is slow and emotional. The happy list is bright and danceable. They share only *Sunrise City*. It's #1 for the happy fan, but only #4 for the sad fan, where it gets in just for being pop. This makes sense. Liking the same genre isn't enough to get the same songs.

**Sad Pop vs. Chill Lofi.** Both want calm, acoustic music at similar energy. Still, they share no songs. One gets ballads, the other gets study beats. This shows genre and mood are working. If only energy counted, these two would get the same list.

**Sad Pop vs. Deep Intense Rock.** Opposites in almost every way. They share one song: *good 4 u*, a pop punk song. It's part pop and part rock, with middle energy. So it earns a few points from both sides. That feels right, since pop punk sits between those two tastes.

**High-Energy Pop vs. Chill Lofi.** Total opposites, and they share nothing. Loud, polished pop versus quiet background music. That's exactly what should happen.

**High-Energy Pop vs. Deep Intense Rock.** Both want loud, energetic music. So they overlap the most: *Gym Hero* and *Here Comes the Sun* are in both. The pop fan gets brighter songs. The rock fan gets heavier ones.

*Why does Gym Hero keep showing up for someone who wants happy pop?* *Gym Hero* is a pop workout song. It's very energetic, but its mood is "intense," not "happy." So it gets no mood points. But it gets points for being pop, and lots of points for having almost the exact energy the listener wants. That's enough to beat most songs. Also, only one song in the catalog is both pop and happy, so there's little competition. Basically, the recommender thinks: "It's pop and it's pumped up. Close enough." A person would notice a gym anthem doesn't feel cheerful.

**Chill Lofi vs. Deep Intense Rock.** Opposites, with nothing shared. The interesting part is how scores drop. The lofi list stays high through #3, because there are several lofi songs. The rock list drops sharply after #1, because only one song is both rock and intense. The catalog matters as much as the rules.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**

- Learning how recommender systems turn data into suggestions.
- Classroom experiments, like changing weights and seeing what happens.
- Seeing clearly *why* a song was picked, since every pick shows its reasons.

**Not intended for:**

- Real users or a real music app. The catalog is too small and the rules are too simple.
- Judging what music is "good." It only measures how well songs match one taste.
- Listeners with mixed tastes. It only allows one genre and one mood per person.
- Any decision that matters. It has known biases (see Section 5) and doesn't check user input carefully.

---

## 8. Ideas for Improvement

1. **Add more songs and balance the catalog.** Give every genre several songs. Fill the energy gaps. Add some loud acoustic songs.
2. **Recommend a more varied list.** Don't show the same artist twice in the top 5. Give every genre and mood at least one "similar" match, so no song gets left out.
3. **Let people describe richer tastes.** Allow more than one favorite genre or mood. Use valence (happiness) so sad and happy songs can be told apart even when the mood label is off.

---

## 9. Personal Reflection

**Biggest learning moment.** My biggest lesson was that the weights matter less than I expected, and the data matters more. I thought lowering the genre weight would fix the rock list, where a gentle Beatles song beat a metal song. When I tested it, the order barely moved. The real problem was that the system didn't know metal and rock are related. Then I ran every possible taste and saw that pop fans just get better results, because there are more pop songs. Fair rules don't help if the catalog isn't fair.

**How AI tools helped, and when I double-checked.** AI helped me write code fast. It built the CSV loader, the scoring function, and the sorting in minutes. It was also great for experiments, like running 1,820 tastes at once, which I would never do by hand. But I had to check its work. It once suggested giving similar moods the same points as an exact match, then caught that this would make "angry" count as fully "intense" and switched to half points. Another time it said lowering genre to 1.5 would fix the rock ranking, but running the numbers showed it didn't. The project README also had a run command (`python -m src.main`) that didn't actually work, and a wrong genre count. I learned to trust what I run and see in the terminal, not just what sounds right.

**What surprised me.** I was surprised how "smart" a few simple rules can feel. It's just adding up points, but when the sad-pop list came back with *drivers license* on top, it felt like the app understood me. The reasons next to each song made it feel even more real. But the same simple rules also made weird picks, like a gym song for a sad listener. A real person would never do that. So recommendations can feel personal without actually understanding music at all.

**What I'd try next.** I'd add more songs so every genre has real choices. I'd stop the same artist from showing up twice. I'd also use valence (happiness) so the system can tell sad from happy songs even when the mood label is off. And I'd let people pick more than one favorite genre, since most people don't like just one kind of music.

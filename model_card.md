# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Think of the recommender as a judge at a talent show who gives every song in the catalog a score out of 6 based on how well it fits one listener, then announces the top five.

**What the listener tells it.** Each listener has four preferences: a favorite genre (like pop), a favorite mood (like sad), how energetic they want the music to be (a number from 0, very calm, to 1, very intense), and whether they like acoustic, unplugged-sounding music or more produced, electronic music.

**What it looks at in each song.** Every song has a genre, a mood, an energy level, and an "acousticness" level that says how unplugged it sounds. The catalog also lists tempo, danceability, and happiness, but the model ignores them for now. Tempo and danceability mostly repeat what energy already says, and happiness is saved for a later experiment.

**How a song earns points.**

- **Genre (up to 2 points).** A song in the listener's favorite genre gets the full 2 points. A close relative, such as "indie pop" or "pop punk" for a pop fan, gets 1 point. Genre is worth the most because it is the most reliable sign of what someone likes.
- **Mood (1.5 points).** A song with exactly the listener's mood gets 1.5 points. Otherwise it gets nothing.
- **Energy (up to 2 points).** This rewards songs whose energy is *close* to what the listener asked for, not simply louder or quieter ones. A song right on target earns the full 2 points, and the further away it is, the fewer it gets. So someone who wants calm music gets calm songs, not the most intense ones in the catalog.
- **Acoustic sound (up to 0.5 points).** A small bonus for songs that match the listener's taste for acoustic or electronic sound. It is kept small because in this catalog acoustic songs are almost always low-energy too, so a bigger bonus would reward calmness twice.

**How it picks the winners.** The points are added up, the songs are lined up from highest to lowest, and the top five are shown. If two songs tie, the one whose energy is closer to the listener's target goes first. Every recommendation comes with its reasons, such as "genre match: pop (+2.0)" or "energy 0.43 vs. target 0.45 (+1.96)", so the listener can see exactly why a song was picked.

**Changes from the starter.** The starter code did no scoring at all; it simply returned the first five songs in the file. I added the whole point system above, plus the plain-language reasons. While designing it I also made two adjustments. I raised mood from 1 point to 1.5, because at 1 point a song that only matched the genre easily beat a song that fit the listener's mood and energy. I also added partial credit for related genres, so "indie pop" isn't treated as a total mismatch for a pop fan.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

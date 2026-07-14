# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

VibeMatch is a small demo that suggests songs based on a taste profile you type in. You give it a favorite genre, favorite mood, a target energy level, and whether you like acoustic songs. It ranks a fixed list of 17 songs and hands back the top 5 that fit best.

This is a classroom project, not a real product. It's meant for learning how scoring rules turn into rankings, not for picking real playlists for real people. It assumes the user already knows their own taste well enough to describe it in four simple fields — it does not learn from listening history or feedback like a real app would.

**Not intended for:** real music recommendations, any use involving real user data, or any claim that it "understands" music the way a person does. It only compares numbers and exact-match text, it doesn't listen to anything.

---

## 3. How the Model Works  

Every song has a genre, a mood, an energy level, and a few other tags. Every user has a favorite genre, a favorite mood, a target energy, and a yes/no on liking acoustic songs. The model compares each song to the user's answers and gives it points:

- If the song's genre matches the user's favorite genre, it gets a big bonus.
- If the song's mood matches the user's favorite mood, it gets a smaller bonus.
- If the song's energy is close to the user's target energy, it gets partial credit — the closer it is, the more points, even if it's not a perfect match.
- If the song's "acoustic-ness" lines up with whether the user likes acoustic songs, it gets a small bonus too.

All those points get added up into one score per song. Then the model just sorts every song from highest score to lowest and shows you the top 5. Genre counts for twice as much as mood, because getting the wrong genre feels like a bigger miss than getting the wrong mood. I kept the starter's basic idea (add up points, then sort) but decided the exact weights myself and added the plain-English "why" explanation for each recommendation.

---

## 4. Data  

The catalog is tiny on purpose — 17 songs total, so it's easy to check the results by hand. Genres include pop, lofi, rock, ambient, jazz, synthwave, indie pop, afrobeats, hip hop, and r&b. Moods range from happy and chill to intense, moody, romantic, heartbroken, hype, and confident. I didn't add or remove any songs — I used the starter dataset as-is.

Because it's so small, whole slices of musical taste are just missing. There's no country, no classical, no metal, no K-pop, and most genres only have 1-3 songs each. If your favorite genre or mood isn't in this list, the model can't ever really match you — it'll just fall back to matching on energy and acoustic-ness alone.

---

## 5. Strengths  

The system does well with users who like a genre that's actually well represented, like afrobeats or lofi (3 songs each), since there's enough variety for the ranking to feel meaningful instead of arbitrary. It also handles "opposite" taste profiles sensibly — a chill/ambient/low-energy user and a hype/hip-hop/high-energy user get pulled toward completely different, appropriate ends of the catalog, which matches what you'd expect from a real recommender.

The energy-closeness scoring (partial credit instead of all-or-nothing) also feels right — a song doesn't need to hit your exact target energy to show up, it just needs to be in the neighborhood, which is closer to how people actually feel about "energy vibes" than a strict cutoff would be.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The clearest bias I found is a **genre-driven filter bubble**: because genre is worth `+2.0` versus energy's max of `+1.0`, a user's favorite genre acts more like a gatekeeper than one signal among several, and in this 17-song catalog each genre only exists within a narrow energy band (lofi songs sit around 0.28-0.42 energy, afrobeats around 0.55-0.62). That means a user who says they like "lofi" but sets `target_energy=0.9` will still only ever get low-energy lofi back — the system can't recommend something energetic in that genre because nothing like it exists in the data, so it just reinforces whatever narrow slice of energy/mood already correlates with that genre instead of surfacing anything that challenges the user's stated taste. On top of that, exact-string genre and mood matching is case-sensitive with no normalization, so a user profile built from real input (e.g., `"Pop"` instead of `"pop"`) silently collapses to zero genre/mood credit and gets treated the same as someone who likes a genre that doesn't exist in the catalog at all — an entire class of users could be getting worse recommendations purely from formatting, with no warning that it happened. Together these mean the system tends to entrench a user's first genre choice rather than exposing them to adjacent taste, and it fails silently rather than flagging when it can't find a real match.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested one baseline profile (afrobeats / romantic / target_energy 0.6) plus 11 "adversarial" profiles designed to try to break or confuse the scoring: conflicting genre-vs-mood-vs-energy combos, the acousticness boundary value (exactly 0.5), out-of-range energy (1.5 and -0.3), genres/moods that don't exist in the catalog, an empty-string profile, and a case-mismatch profile (`"Pop"` instead of `"pop"`). For each I looked at whether the top 5 made intuitive sense given the reasons printed, whether the score ever went negative or the program crashed, and whether small changes to the input (like capitalization) caused proportionally small or wildly disproportionate changes in the output.

**What surprised me:** the system never crashes or produces an invalid score, even on nonsense input — but that "safety" is actually hiding a bug. A profile with a genre that's simply spelled with different capitalization gets silently treated as if that genre doesn't exist anywhere in the world, with no error or fallback. I expected a typo to hurt the recommendations a little; instead it wipes out the entire genre + mood bonus (2.5 of the 4.5 max points) for that user, which is a much bigger effect than the "mistake" should cause.

**Pairwise comparisons:**

- **Baseline (afrobeats/romantic/0.6) vs. Conflicting (afrobeats/heartbroken/0.95):** The heartbroken+high-energy profile still returns the same 3 afrobeats songs, just reordered, with Last Last (the actual "heartbroken" song) now on top instead of Essence. This makes sense: genre match is worth more than anything else, so all 3 afrobeats songs stay in the top group regardless of how badly mood and energy disagree with each other — the conflict shows up as a reshuffle within the genre cluster, not a totally different set of songs.
- **Jazz/hype/low-energy (0.35) vs. Hip-hop/hype/high-energy (1.0):** The jazz profile's own "hype" mood match never actually lands on a jazz song (there's no hype jazz in the catalog), so its #1 pick is just the jazz genre match with no mood bonus. The hip-hop profile's "hype" mood *does* exist on a hip-hop song (Sicko Mode), so that profile gets all four bonuses at once and scores far higher (4.33 vs 2.98). This is exactly what you'd expect: a mood preference only helps if a song in your favorite genre actually carries that mood — otherwise it's a preference the system simply can't satisfy.
- **Boundary pop/happy/0.5 vs. Case-mismatch "Pop"/"Happy"/0.8:** This pair is the clearest illustration of why a song like **Gym Hero** (genre: pop, mood: intense, energy: 0.93) keeps showing up for someone who says they want "Happy Pop." In the boundary test, Gym Hero lands at #2 even though its mood is "intense," not "happy," because it still gets the full `+2.0` genre bonus plus a strong energy-closeness score — the missing mood match (`+1.0`) isn't enough to knock it out of the top few. In plain terms: the system only really checks "is this the right music genre" and "is this roughly the right energy level" — it doesn't check "does this actually feel happy," so a loud, intense gym-workout song can still outrank quieter but genuinely happier songs just because it's tagged "pop" and happens to be playing at the energy level you asked for. Then in the case-mismatch version, capitalizing "Pop" and "Happy" wipes out *even* the genre match, so the results collapse into whatever has the closest energy to 0.8 with no pop/happy connection at all — a strictly worse outcome caused by nothing but a typo.
- **Ambient/chill/0.0 vs. Hip-hop/hype/1.0 (opposite extremes):** These behave like a mirror image of each other — the chill/ambient profile pulls in the catalog's quietest, most acoustic songs (Spacewalk Thoughts, Library Rain), while the hype/hip-hop profile pulls in the loudest, least acoustic songs (Sicko Mode, HUMBLE.). That's exactly the intended behavior: an "EDM-energy" type of profile should shift toward high-energy, non-acoustic tracks, and a "chill/ambient" profile should shift the opposite way, since energy closeness and acoustic fit are both symmetric around the user's stated target.
- **Nonexistent genre/mood ("metal"/"euphoric") vs. empty-string genre/mood ("" / ""):** These two profiles return the *exact same* top 5, in the same order, with identical scores. That makes sense once you see why: neither `"metal"` nor `""` ever equals a real value in the CSV, so both profiles get zero genre and zero mood credit and the ranking falls back entirely to energy-closeness and acoustic fit. It's a good sanity check that the system degrades predictably (not randomly) when it truly has nothing to match on — but it also means a blank/unset profile is treated identically to a profile with clearly-invalid preferences, which a real product probably shouldn't do silently.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

1. **Fix the case-sensitivity bug first.** Lowercase (or otherwise normalize) both the song data and the user's genre/mood before comparing them, so a typo like "Pop" instead of "pop" doesn't silently wreck someone's recommendations.
2. **Let genre and mood be "close" instead of exact-match-only.** Right now a song either matches your genre perfectly or gets nothing at all. I'd want something like a genre-similarity table (afrobeats and r&b are closer to each other than afrobeats and rock) so near-misses still get partial credit, the same way energy already works.
3. **Add a diversity rule to the top 5.** Since genre dominates the score so heavily, the top 5 for one user is often 3+ songs from the exact same genre. I'd want to cap how many songs from one genre can appear in a row, so users see more variety instead of one genre repeated with small score differences.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

My biggest learning moment was realizing how much a recommender's "personality" comes down to just a few numbers. Changing genre's weight from 2.0 to something else, or removing mood entirely, completely changed which song felt like the "best" pick — even though nothing about the songs themselves changed. That made it click that a recommender isn't really judging taste, it's just doing arithmetic on tags someone else decided on ahead of time.

Using my AI assistant to help run experiments and dig through the data was genuinely useful for speed — it could run a dozen test profiles and organize the output faster than I'd do it by hand, and it caught the case-sensitivity bug I hadn't thought to check for. But I had to double-check its claims against the real output every time, especially anything with specific numbers or song names, since it's easy for a written explanation to sound confident even when it's slightly wrong about which song scored what.

What surprised me most is how "alive" a simple weighted sum can feel from the outside. Watching Gym Hero sneak into a "happy pop" list because it shares a genre tag and lands near the right energy — it really does feel like the system is "confused," even though under the hood it's just addition. That's a little unsettling, honestly, because it means real recommendation apps probably feel way smarter than they actually are, and their biases (like the genre filter bubble I found here) can hide behind that same illusion.

If I kept building this, I'd want to try a bigger, messier dataset and see if these same biases get worse or actually smooth out with more songs to choose from.

# My Personal Project

A small personal tool I started on November 2, 2026.

## Tools

### 1. script_cleaner.py — Hindi narration script cleaner

Cleans Hindi narration scripts for voiceover use:

- Removes comma (,), hyphen (-), slash (/), and underscore (_) — these symbols make voiceover sound broken and robotic.
- Makes sure every sentence ends with a danda (।), the Devanagari full stop.

```bash
python script_cleaner.py example_input.txt cleaned_output.txt
```

If you don't give an output file, the cleaned text is printed on screen.

### 2. title_checker.py — YouTube title checker

Checks a video title against basic channel rules: 100 characters or fewer, no emojis, and ending with "| movie explanation".

```bash
python title_checker.py "Your Title Here"
```

### 3. hashtag_counter.py — description hashtag counter

Counts hashtags in a video description. YouTube ignores every hashtag beyond the first 15, so this warns when the count goes over 15.

```bash
python hashtag_counter.py example_description.txt
```

### 4. duration_estimator.py — narration duration estimator

Estimates narration time from a script file at 3.3 words per second, the rate used for Hindi movie-explanation narration planning.

```bash
python duration_estimator.py example_input.txt
```

### 5. script_symbols_checker.py — Hindi script symbols checker

Checks a Hindi narration script for banned symbols — comma (,), hyphen (-), slash (/) and underscore (_) — which make voiceover sound broken and robotic. Reports how many of each symbol were found and the line numbers where they appear.

```bash
python script_symbols_checker.py script.txt
```

Exit code is 0 when the script is clean and 1 when banned symbols are found.

### 6. script_splitter.py — Hindi narration script splitter

Splits a long Hindi script into sequential parts of about 2500 words each, at sentence boundaries, so no sentence is ever cut in half. Each part is saved as its own file and the word count and estimated narration time of every part is printed.

```bash
python script_splitter.py script.txt
python script_splitter.py script.txt --words 2000 --out-dir parts/
```

Estimated time uses 3.3 words per second, the same rate as duration_estimator.py.

### 7. description_checker.py — YouTube description checker

Checks a video description against the channel's locked description formula before it goes live:

- At most 15 hashtags — YouTube ignores everything beyond 15.
- Hindi keywords in the first two lines, so it ranks for Hindi search.
- A Movie Details / credits block (year, director, cast, rating).
- A Related line naming Flick Movies Explanation, Filmaya or Razzu Bolta Hai.
- A fair-use disclaimer.
- No email address — a personal Gmail must never appear in a public description.
- At most 5000 characters, the YouTube description limit.

```bash
python description_checker.py description.txt
```

Exit code is 0 when there are no failures (warnings are allowed), 1 when any check fails, and 2 on a usage or file error.

### 8. repetition_checker.py — Hindi script repetition checker

Finds repeated phrases and sentences in a Hindi narration script, for the no-repetition rule: never repeat the same beat or phrase back-to-back. A phrase counts only when it repeats in the same sentence or in two neighbouring sentences, so words that simply recur across a whole script are not flagged. Whole repeated sentences are reported separately.

```bash
python repetition_checker.py script.txt
python repetition_checker.py script.txt --min-words 5
```

Exit code is 0 when no repetition is found, 1 when repetition is found, and 2 on a usage or file error.

## Files

- `script_cleaner.py` — the cleaner tool
- `title_checker.py` — the title checker
- `hashtag_counter.py` — the hashtag counter
- `duration_estimator.py` — the duration estimator
- `script_symbols_checker.py` — the symbols checker
- `script_splitter.py` — the script splitter
- `description_checker.py` — the description checker
- `repetition_checker.py` — the repetition checker
- `example_input.txt` — a small sample script to try the tools on
- `example_description.txt` — a sample description for the hashtag counter
- `LICENSE` — MIT license

## Status

Active — small tools are added regularly, each one tested and working.

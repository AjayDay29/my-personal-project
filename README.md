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

## Files

- `script_cleaner.py` — the cleaner tool
- `title_checker.py` — the title checker
- `hashtag_counter.py` — the hashtag counter
- `duration_estimator.py` — the duration estimator
- `example_input.txt` — a small sample script to try the tools on
- `example_description.txt` — a sample description for the hashtag counter
- `LICENSE` — MIT license

## Status

Just started — one tool, working. More small tools may be added later.

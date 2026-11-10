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

### 9. upload_package_checker.py — YouTube upload package checker

Checks a whole video upload package folder before it goes live, against the channel's locked formula. The folder must hold title.txt, description.txt, tags.txt (comma-separated) and thumbnail.jpg or thumbnail.png:

- Title: 100 characters or fewer, no emojis, ends with "movie explanation".
- Description: 5000 characters or fewer, at most 15 hashtags, a Movie Details block, a Related line, a fair-use disclaimer, and no email address.
- Tags: 500 characters total or fewer (YouTube's documented limit); a tag over 30 characters is only a warning, because YouTube publishes no per-tag limit.
- Thumbnail: a JPG or PNG image, 16:9, at least 1280 pixels wide. Image size is read without extra libraries.

```bash
python upload_package_checker.py package-dir/
```

Exit code is 0 when the package passes (warnings are allowed), 1 when any check fails, and 2 on a usage or file error.

### 10. thumbnail_checker.py — YouTube thumbnail checker

Checks one thumbnail image before it goes live, against YouTube's thumbnail rules:

- Format: JPG, PNG, GIF or BMP — the formats YouTube accepts.
- Shape: 16:9, the YouTube thumbnail shape.
- Width: at least 640 pixels (YouTube's minimum); 1280x720 is the channel's upload size, anything bigger is only a warning.
- File size: 2 MB or less — YouTube's thumbnail limit. A 95 MB 8K file fails this check, so the mistake from 9 Nov 2026 (a 95 MB thumbnail made before anyone checked the size) gets caught before the file is sent anywhere.

```bash
python thumbnail_checker.py thumbnail.jpg
python thumbnail_checker.py thumbnail.png
```

Exit code is 0 when the thumbnail passes (warnings are allowed), 1 when any check fails, and 2 on a usage or file error.

### 11. thumbnail_sizer.py — YouTube thumbnail sizer

Shrinks a thumbnail to a file YouTube will accept, without changing what it looks like. YouTube only accepts a thumbnail up to 2 MB, and 1280x720 is the size it shows — anything bigger only makes the file heavier:

- A JPG already 1280 pixels wide or less and 2 MB or less is copied unchanged, so no quality is lost at all.
- Otherwise it resizes to 1280 pixels wide (keeping the shape) and saves as JPG, trying the highest quality first and stepping down only until the file fits under 2 MB.
- If even the lowest quality does not fit, it steps the width down to 960, then 640 (YouTube's minimum width).
- The output is always JPG, because YouTube does not accept WebP as a thumbnail. The input file is never changed.

Needs Pillow: `pip install Pillow`

```bash
python thumbnail_sizer.py thumbnail.png
python thumbnail_sizer.py thumbnail.png upload-ready.jpg
python thumbnail_sizer.py thumbnail.jpg --keep-size
```

Exit code is 0 when the output fits under the limit, 1 when it cannot be made to fit even at the smallest settings, and 2 on a usage or file error.

## Files

- `script_cleaner.py` — the cleaner tool
- `title_checker.py` — the title checker
- `hashtag_counter.py` — the hashtag counter
- `duration_estimator.py` — the duration estimator
- `script_symbols_checker.py` — the symbols checker
- `script_splitter.py` — the script splitter
- `description_checker.py` — the description checker
- `repetition_checker.py` — the repetition checker
- `upload_package_checker.py` — the upload package checker
- `thumbnail_checker.py` — the thumbnail checker
- `thumbnail_sizer.py` — the thumbnail sizer
- `example_input.txt` — a small sample script to try the tools on
- `example_description.txt` — a sample description for the hashtag counter
- `LICENSE` — MIT license

## Status

Active — small tools are added regularly, each one tested and working.

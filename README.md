# My Personal Project

A small personal tool I started on November 2, 2026.

## What it does

`script_cleaner.py` cleans Hindi narration scripts for voiceover use:

- Removes comma (,), hyphen (-), slash (/), and underscore (_) — these symbols make voiceover sound broken and robotic.
- Makes sure every sentence ends with a danda (।), the Devanagari full stop.

## How to use

```bash
python script_cleaner.py example_input.txt cleaned_output.txt
```

If you don't give an output file, the cleaned text is printed on screen.

## Files

- `script_cleaner.py` — the cleaner tool
- `example_input.txt` — a small sample script to try it on
- `LICENSE` — MIT license

## Status

Just started — one tool, working. More small tools may be added later.

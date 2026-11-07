#!/usr/bin/env python3
"""YouTube video description checker.

Checks a video description against the channel's locked description
formula before it goes live:

- At most 15 hashtags -- YouTube ignores every hashtag beyond the
  first 15, so more than 15 is a hard fail.
- Hindi keywords in the first two lines, so the description ranks
  for Hindi search from the very top.
- A Movie Details / credits block with the film's year, director,
  cast and rating.
- A Related line naming the reference channels (Flick Movies
  Explanation, Filmaya, Razzu Bolta Hai / Razzu The Explainer).
- A fair-use disclaimer.
- No email address anywhere -- a personal Gmail must never appear
  in a public description.
- At most 5000 characters, the YouTube description limit.

Usage:
    python description_checker.py description.txt

Prints one PASS / WARN / FAIL line per check and a short summary.
Exit code is 0 when there are no failures (warnings are allowed),
1 when any check fails, and 2 on a usage or file error.
"""

import argparse
import re
import sys

MAX_HASHTAGS = 15
MAX_CHARS = 5000
DEVANAGARI = re.compile(r"[\u0900-\u097F]")
HASHTAG = re.compile(r"#\w+")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RELATED_CHANNELS = (
    "Flick Movies Explanation",
    "Filmaya",
    "Razzu Bolta Hai",
    "Razzu The Explainer",
)


def first_lines(text, count=2):
    """First `count` non-empty lines of the description."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[:count]


def check_description(text):
    """Return (failures, warnings), each a list of message strings."""
    failures = []
    warnings = []

    hashtags = HASHTAG.findall(text)
    if len(hashtags) > MAX_HASHTAGS:
        failures.append(
            f"FAIL: {len(hashtags)} hashtags found, "
            f"but YouTube ignores everything beyond {MAX_HASHTAGS}."
        )
    else:
        print(f"PASS: {len(hashtags)} hashtag(s), within the "
              f"{MAX_HASHTAGS} limit.")

    if len(text) > MAX_CHARS:
        failures.append(
            f"FAIL: description is {len(text)} characters, over the "
            f"{MAX_CHARS} YouTube limit."
        )
    else:
        print(f"PASS: {len(text)} characters, within the "
              f"{MAX_CHARS} limit.")

    emails = EMAIL.findall(text)
    if emails:
        failures.append(
            "FAIL: email address found in the description "
            f"({', '.join(sorted(set(emails)))}). Remove it -- no "
            "personal email belongs in a public description."
        )
    else:
        print("PASS: no email address in the description.")

    top = "\n".join(first_lines(text))
    if DEVANAGARI.search(top):
        print("PASS: Hindi keywords present in the first two lines.")
    else:
        warnings.append(
            "WARN: no Hindi (Devanagari) keywords in the first two "
            "lines -- add them so the description ranks for Hindi search."
        )

    lowered = text.lower()
    if "movie details" in lowered or "movie credits" in lowered:
        print("PASS: Movie Details / credits block present.")
    else:
        warnings.append(
            "WARN: no Movie Details / credits block found -- add the "
            "film's year, director, cast and rating."
        )

    if any(name.lower() in lowered for name in RELATED_CHANNELS):
        print("PASS: Related line with a reference channel present.")
    else:
        warnings.append(
            "WARN: no Related line found -- add Flick Movies "
            "Explanation, Filmaya or Razzu Bolta Hai."
        )

    if "fair use" in lowered:
        print("PASS: fair-use disclaimer present.")
    else:
        warnings.append(
            "WARN: no fair-use disclaimer found -- add one before "
            "uploading."
        )

    return failures, warnings


def main(argv):
    parser = argparse.ArgumentParser(
        description="Check a YouTube video description against the "
        "channel's locked description formula."
    )
    parser.add_argument("description", help="description file to check")
    args = parser.parse_args(argv)

    try:
        with open(args.description, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.description}", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print(f"Error: not a UTF-8 text file: {args.description}",
              file=sys.stderr)
        return 2

    if not text.strip():
        print("Error: description file is empty.", file=sys.stderr)
        return 2

    failures, warnings = check_description(text)

    for message in warnings:
        print(message)
    for message in failures:
        print(message)

    if failures:
        print(f"Result: {len(failures)} failure(s), "
              f"{len(warnings)} warning(s) -- fix the failures first.")
        return 1
    if warnings:
        print(f"Result: all hard checks passed, "
              f"{len(warnings)} warning(s) to review.")
    else:
        print("Result: description passes every check.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

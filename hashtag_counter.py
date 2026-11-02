#!/usr/bin/env python3
"""Count hashtags in a YouTube description.

YouTube ignores every hashtag beyond the first 15, so a description
should carry at most 15 hashtags.

Usage:
    python hashtag_counter.py description.txt

If no file is given, the text is read from standard input.
"""

import re
import sys

MAX_HASHTAGS = 15
HASHTAG_PATTERN = re.compile(r"#\w+")


def count_hashtags(text):
    """Return the list of hashtags found in the text."""
    return HASHTAG_PATTERN.findall(text)


def main():
    if len(sys.argv) >= 2:
        with open(sys.argv[1], encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()
    tags = count_hashtags(text)
    print(f"Hashtags found: {len(tags)}")
    for tag in tags:
        print(f"  {tag}")
    if len(tags) > MAX_HASHTAGS:
        print(
            f"WARN: {len(tags) - MAX_HASHTAGS} hashtag(s) over the limit "
            f"of {MAX_HASHTAGS} will be ignored by YouTube."
        )
    else:
        print(f"OK: within the limit of {MAX_HASHTAGS} hashtags.")


if __name__ == "__main__":
    main()

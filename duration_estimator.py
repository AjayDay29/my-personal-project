#!/usr/bin/env python3
"""Estimate narration duration from a script file.

Uses a speaking rate of 3.3 words per second, the rate used for
Hindi movie-explanation narration planning.

Usage:
    python duration_estimator.py script.txt
"""

import sys

WORDS_PER_SECOND = 3.3


def estimate_duration(text):
    """Return (word_count, seconds) for the given text."""
    words = text.split()
    seconds = len(words) / WORDS_PER_SECOND
    return len(words), seconds


def format_time(seconds):
    """Format seconds as M:SS."""
    minutes = int(seconds // 60)
    remaining = int(round(seconds % 60))
    return f"{minutes}:{remaining:02d}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python duration_estimator.py script.txt")
        return
    with open(sys.argv[1], encoding="utf-8") as handle:
        text = handle.read()
    word_count, seconds = estimate_duration(text)
    print(f"Words: {word_count}")
    print(f"Estimated narration time: {format_time(seconds)} (MM:SS)")


if __name__ == "__main__":
    main()

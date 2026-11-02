#!/usr/bin/env python3
"""Clean a Hindi narration script for voiceover use.

Removes the symbols that make voiceover sound broken or robotic
(comma, hyphen, slash, underscore) and makes every sentence end
with a danda (Devanagari full stop).

Usage:
    python script_cleaner.py input.txt [output.txt]

If no output file is given, the cleaned text is printed.
"""

import re
import sys

BANNED = [",", "-", "/", "_"]


def clean_script(text):
    """Return the script with banned symbols removed and danda endings."""
    for symbol in BANNED:
        text = text.replace(symbol, " ")
    # Split on existing sentence endings (. ! ? and danda) and newlines.
    parts = re.split(r"[.!?।\n]+", text)
    sentences = []
    for part in parts:
        sentence = re.sub(r"\s+", " ", part).strip()
        if sentence:
            sentences.append(sentence)
    return "\n".join(sentence + "।" for sentence in sentences)


def main():
    if len(sys.argv) < 2:
        print("Usage: python script_cleaner.py input.txt [output.txt]")
        return
    with open(sys.argv[1], encoding="utf-8") as handle:
        text = handle.read()
    cleaned = clean_script(text)
    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as handle:
            handle.write(cleaned + "\n")
    else:
        print(cleaned)


if __name__ == "__main__":
    main()

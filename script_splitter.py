#!/usr/bin/env python3
"""Hindi narration script splitter.

Long narrations are recorded in sequential batches of about 2500 words
-- Part 1, Part 2, and so on. This tool splits a long Hindi script
into such parts at sentence boundaries, so no sentence is ever cut
in half. Each part is written to its own file next to the input file
(or into --out-dir) and the word count and estimated narration time
of every part is printed.

Usage:
    python script_splitter.py script.txt
    python script_splitter.py script.txt --words 2500
    python script_splitter.py script.txt --words 2000 --out-dir parts/

Sentences are split on the danda (Devanagari full stop). A single
sentence longer than the word limit gets a part of its own, and is
reported. Estimated time uses 3.3 words per second, the same rate as
duration_estimator.py.

Exit code is 0 on success and 2 on a usage or file error.
"""

import argparse
import os
import re
import sys

DEFAULT_WORDS = 2500
WORDS_PER_SECOND = 3.3
DANDA = "\u0964"


def split_sentences(text):
    """Split text into sentences on the danda, keeping it attached."""
    parts = re.split(f"(?<={DANDA})", text)
    sentences = [s.strip() for s in parts]
    return [s for s in sentences if s]


def word_count(sentence):
    return len(sentence.split())


def format_duration(words):
    total_seconds = round(words / WORDS_PER_SECOND)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def split_script(text, max_words):
    """Pack sentences into parts of at most max_words. Returns parts
    as a list of sentence lists, plus the long sentences that had to
    stand alone."""
    sentences = split_sentences(text)
    parts = []
    long_sentences = []
    current = []
    current_words = 0
    for sentence in sentences:
        words = word_count(sentence)
        if words > max_words:
            long_sentences.append(sentence)
            if current:
                parts.append(current)
                current = []
                current_words = 0
            parts.append([sentence])
            continue
        if current and current_words + words > max_words:
            parts.append(current)
            current = []
            current_words = 0
        current.append(sentence)
        current_words += words
    if current:
        parts.append(current)
    return parts, long_sentences


def main(argv):
    parser = argparse.ArgumentParser(
        description="Split a Hindi narration script into "
        f"~{DEFAULT_WORDS}-word parts at sentence boundaries."
    )
    parser.add_argument("script", help="Hindi script file to split")
    parser.add_argument(
        "--words",
        type=int,
        default=DEFAULT_WORDS,
        help=f"target words per part (default {DEFAULT_WORDS})",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="directory for the part files (default: same as the script)",
    )
    args = parser.parse_args(argv)

    if args.words < 1:
        print("Error: --words must be at least 1.", file=sys.stderr)
        return 2

    try:
        with open(args.script, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.script}", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print(f"Error: not a UTF-8 text file: {args.script}", file=sys.stderr)
        return 2

    parts, long_sentences = split_script(text, args.words)
    if not parts:
        print("Error: no sentences found in the script.", file=sys.stderr)
        return 2

    stem = os.path.splitext(os.path.basename(args.script))[0]
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.script))
    os.makedirs(out_dir, exist_ok=True)

    total_words = 0
    for number, sentences in enumerate(parts, start=1):
        filename = f"{stem}-part{number}.txt"
        path = os.path.join(out_dir, filename)
        words = sum(word_count(s) for s in sentences)
        total_words += words
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(sentences) + "\n")
        print(f"Part {number}: {filename} — {words} words, "
              f"about {format_duration(words)}")

    print(f"Total: {len(parts)} part(s), {total_words} words, "
          f"about {format_duration(total_words)}")
    if long_sentences:
        print(f"Note: {len(long_sentences)} sentence(s) alone exceed "
              f"{args.words} words and got a part of their own.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

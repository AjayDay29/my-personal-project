#!/usr/bin/env python3
"""Hindi narration voice chunk splitter.

Alex voiceovers are generated on teamsp.org, where one generation
takes at most 2500 characters. This tool splits a long Hindi script
into such voice chunks at sentence boundaries, so no sentence is ever
cut in half. Each chunk is written to its own file next to the input
file (or into --out-dir) and the character count, word count and
estimated narration time of every chunk is printed.

Usage:
    python voice_chunk_splitter.py script.txt
    python voice_chunk_splitter.py script.txt --chars 2500
    python voice_chunk_splitter.py script.txt --chars 2000 --out-dir chunks/

Sentences are split on the danda (Devanagari full stop) and on . ? !
for Roman Hindi or English lines. A single sentence longer than the
character limit gets a chunk of its own, and is reported, because
teamsp would cut it off -- split such a sentence by hand before
generating. Estimated time uses 3.3 words per second, the same rate
as duration_estimator.py.

Exit code is 0 on success and 2 on a usage or file error.
"""

import argparse
import os
import re
import sys

DEFAULT_CHARS = 2500
WORDS_PER_SECOND = 3.3
# Sentence ends: danda, full stop, question mark, exclamation mark.
SENTENCE_END = re.compile(r"(?<=[\u0964.?!])\s+")


def split_sentences(text):
    """Split text into sentences, keeping the end mark attached."""
    sentences = [s.strip() for s in SENTENCE_END.split(text)]
    return [s for s in sentences if s]


def word_count(sentence):
    return len(sentence.split())


def format_duration(words):
    total_seconds = round(words / WORDS_PER_SECOND)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def split_script(text, max_chars):
    """Pack sentences into chunks of at most max_chars. Returns chunks
    as a list of sentence lists, plus the long sentences that had to
    stand alone."""
    sentences = split_sentences(text)
    chunks = []
    long_sentences = []
    current = []
    current_chars = 0
    for sentence in sentences:
        size = len(sentence)
        if size > max_chars:
            long_sentences.append(sentence)
            if current:
                chunks.append(current)
                current = []
                current_chars = 0
            chunks.append([sentence])
            continue
        # Sentences are joined with one newline when written out.
        extra = size + (1 if current else 0)
        if current and current_chars + extra > max_chars:
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(sentence)
        current_chars += extra
    if current:
        chunks.append(current)
    return chunks, long_sentences


def main(argv):
    parser = argparse.ArgumentParser(
        description="Split a Hindi narration script into "
        f"~{DEFAULT_CHARS}-character voice chunks at sentence boundaries."
    )
    parser.add_argument("script", help="Hindi script file to split")
    parser.add_argument(
        "--chars",
        type=int,
        default=DEFAULT_CHARS,
        help=f"target characters per chunk (default {DEFAULT_CHARS}, "
        "the teamsp.org generation limit)",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="directory for the chunk files (default: same as the script)",
    )
    args = parser.parse_args(argv)

    if args.chars < 1:
        print("Error: --chars must be at least 1.", file=sys.stderr)
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

    chunks, long_sentences = split_script(text, args.chars)
    if not chunks:
        print("Error: no sentences found in the script.", file=sys.stderr)
        return 2

    stem = os.path.splitext(os.path.basename(args.script))[0]
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.script))
    os.makedirs(out_dir, exist_ok=True)

    total_chars = 0
    total_words = 0
    for number, sentences in enumerate(chunks, start=1):
        filename = f"{stem}-voice-chunk{number:02d}.txt"
        path = os.path.join(out_dir, filename)
        content = "\n".join(sentences) + "\n"
        chars = len(content.strip())
        words = sum(word_count(s) for s in sentences)
        total_chars += chars
        total_words += words
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Chunk {number}: {filename} — {chars} characters, "
              f"{words} words, about {format_duration(words)}")

    print(f"Total: {len(chunks)} chunk(s), {total_chars} characters, "
          f"{total_words} words, about {format_duration(total_words)}")
    if long_sentences:
        print(f"Note: {len(long_sentences)} sentence(s) alone exceed "
              f"{args.chars} characters and got a chunk of their own. "
              "Split them by hand before generating, or teamsp will "
              "cut them off.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

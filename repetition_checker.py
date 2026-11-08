#!/usr/bin/env python3
"""Hindi narration script repetition checker.

Ajay's no-repetition rule: never repeat the same beat or phrase
back-to-back in a script (for example "ek baar, phir dusri baar,
phir teesri baar"). A repeated action is described once, flowingly.
This tool finds repeated word phrases and repeated sentences in a
Hindi narration script and reports where they appear, so they can
be rewritten before recording.

Usage:
    python repetition_checker.py script.txt
    python repetition_checker.py script.txt --min-words 5
    cat script.txt | python repetition_checker.py

A phrase is a run of --min-words (default 4) or more words that
appears twice back-to-back -- in the same sentence or in two
neighbouring sentences. Whole repeated sentences are reported
separately, wherever they appear. Exit code is 0 when no repetition is found, 1 when
repetition is found, and 2 on a usage or file error.
"""

import argparse
import re
import sys
from collections import defaultdict

DEFAULT_MIN_WORDS = 4
MAX_SHOW_PER_PHRASE = 5


def split_sentences(text):
    """Split text into (line_no, sentence) pairs on danda or newline."""
    sentences = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"[।\n]+", line)
        for part in parts:
            part = part.strip()
            if part:
                sentences.append((line_no, part))
    return sentences


def words_of(sentence):
    """Words of a sentence, lowercased, punctuation stripped.

    Only punctuation is removed -- Devanagari vowel signs are kept,
    so a word like "राम" stays one word instead of splitting apart.
    """
    cleaned = re.sub(r"[।,.\-/_\"'()\[\]{}:;!?]", " ", sentence)
    return [w.lower() for w in cleaned.split() if w]


def find_repeated_phrases(sentences, min_words, repeated_sentence_keys):
    """Find word phrases that repeat back-to-back.

    Ajay's rule bans repeating the same beat or phrase right after
    itself, not words that recur across a whole script. So a phrase
    of min_words or more counts only when it appears twice in the
    same sentence or in two neighbouring sentences. A phrase that
    only repeats because its whole sentence repeats is left to the
    repeated-sentence report, and overlapping windows of one repeat
    are merged to a single report.

    Returns a dict: phrase -> (count, sorted list of line numbers).
    """
    occurrences = defaultdict(list)  # phrase -> [(sent_idx, line, start)]
    for sent_idx, (line_no, sentence) in enumerate(sentences):
        words = words_of(sentence)
        if len(words) < min_words:
            continue
        for start in range(len(words) - min_words + 1):
            phrase = " ".join(words[start:start + min_words])
            occurrences[phrase].append((sent_idx, line_no, start))

    repeated = {}
    for phrase, spots in occurrences.items():
        close = any(idx_b - idx_a <= 1
                    for (idx_a, _, _), (idx_b, _, _) in zip(spots, spots[1:]))
        if not close:
            continue
        # Skip phrases whose repeats come only from a repeated sentence.
        if all(" ".join(words_of(sentences[idx][1])) in repeated_sentence_keys
               for idx, _, _ in spots):
            continue
        repeated[phrase] = (len(spots), sorted({line for _, line, _ in spots}))

    # Merge overlapping windows of the same repeat: in one sentence,
    # keep only the earliest-starting window among overlapping ones.
    phrases = sorted(repeated, key=lambda p: (min(start for _, _, start in
                    occurrences[p]), p))
    kept = {}
    kept_spans = defaultdict(list)  # sent_idx -> [(start, end)]
    for phrase in phrases:
        overlap = False
        for sent_idx, _, start in occurrences[phrase]:
            for kept_start, kept_end in kept_spans[sent_idx]:
                if start < kept_end and kept_start < start + min_words:
                    overlap = True
                    break
            if overlap:
                break
        if overlap:
            continue
        kept[phrase] = repeated[phrase]
        for sent_idx, _, start in occurrences[phrase]:
            kept_spans[sent_idx].append((start, start + min_words))
    return kept


def find_repeated_sentences(sentences):
    """Find whole sentences that appear more than once.

    Returns a dict: sentence -> (count, sorted list of line numbers).
    Count is the number of occurrences, not distinct lines, so a
    sentence repeated twice on the same line is still caught.
    """
    occurrences = defaultdict(list)
    for line_no, sentence in sentences:
        key = " ".join(words_of(sentence))
        if key:
            occurrences[key].append(line_no)
    return {s: (len(lines), sorted(set(lines)))
            for s, lines in occurrences.items() if len(lines) > 1}


def check_text(text, min_words):
    sentences = split_sentences(text)
    repeated_sentences = find_repeated_sentences(sentences)
    # Keys of sentences that repeat, for the phrase check to skip.
    keys = set()
    seen = set()
    for _, sentence in sentences:
        key = " ".join(words_of(sentence))
        if key in seen:
            keys.add(key)
        seen.add(key)
    phrases = find_repeated_phrases(sentences, min_words, keys)
    return phrases, repeated_sentences


def report(label, phrases, repeated_sentences):
    print(f"--- {label} ---")
    if not phrases and not repeated_sentences:
        print("Clean: no repeated phrases or sentences found.")
        return 0
    total = len(phrases) + len(repeated_sentences)
    print(f"Found {total} repeated item(s):")
    if repeated_sentences:
        print("Repeated sentences:")
        for sentence, (count, lines) in sorted(
                repeated_sentences.items(), key=lambda kv: -kv[1][0]):
            shown = ", ".join(f"line {n}" for n in lines[:MAX_SHOW_PER_PHRASE])
            print(f"  x{count} [{shown}]: {sentence}")
    if phrases:
        print("Repeated phrases:")
        for phrase, (count, lines) in sorted(phrases.items(),
                                              key=lambda kv: -kv[1][0]):
            shown = ", ".join(f"line {n}" for n in lines[:MAX_SHOW_PER_PHRASE])
            print(f"  x{count} [{shown}]: ...{phrase}...")
    print("Fix: describe a repeated action once, flowingly, "
          "instead of repeating the same beat.")
    return 1


def check_file(path, min_words):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        return None
    except UnicodeDecodeError:
        print(f"Error: not a UTF-8 text file: {path}", file=sys.stderr)
        return None
    return check_text(text, min_words)


def main(argv):
    parser = argparse.ArgumentParser(
        description="Find repeated phrases and sentences in a Hindi "
                    "narration script.")
    parser.add_argument("paths", nargs="*", help="script file(s) to check")
    parser.add_argument("--min-words", type=int, default=DEFAULT_MIN_WORDS,
                        help="minimum words in a repeated phrase "
                             "(default: 4)")
    args = parser.parse_args(argv)
    if args.min_words < 2:
        print("Error: --min-words must be at least 2", file=sys.stderr)
        return 2

    if not args.paths:
        text = sys.stdin.read()
        phrases, repeated = check_text(text, args.min_words)
        return report("stdin", phrases, repeated)

    any_error = False
    found = False
    for path in args.paths:
        result = check_file(path, args.min_words)
        if result is None:
            any_error = True
            continue
        phrases, repeated = result
        if report(path, phrases, repeated):
            found = True

    if any_error:
        return 2
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

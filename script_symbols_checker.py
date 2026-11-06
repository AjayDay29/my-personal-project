#!/usr/bin/env python3
"""Hindi narration script symbols checker.

Narration scripts must not contain comma (,), hyphen (-), slash (/)
or underscore (_) -- these symbols make the voiceover sound broken
and robotic. This tool checks a script file for those symbols and
reports where they appear, so they can be fixed before recording.

Usage:
    python script_symbols_checker.py script.txt
    python script_symbols_checker.py script1.txt script2.txt
    cat script.txt | python script_symbols_checker.py

Exit code is 0 when the script is clean, 1 when banned symbols
are found, and 2 on a usage or file error.
"""

import sys

BANNED = {
    ",": "comma",
    "-": "hyphen",
    "/": "slash",
    "_": "underscore",
}

MAX_SHOW_PER_SYMBOL = 10


def check_text(text, label):
    """Check one text. Returns (total, per_symbol dict, examples list)."""
    per_symbol = {sym: 0 for sym in BANNED}
    examples = []  # (line_no, symbol, line_text)
    shown = {sym: 0 for sym in BANNED}
    for line_no, line in enumerate(text.splitlines(), start=1):
        for sym in BANNED:
            count = line.count(sym)
            if count:
                per_symbol[sym] += count
                if shown[sym] < MAX_SHOW_PER_SYMBOL:
                    examples.append((line_no, sym, line.strip()))
                    shown[sym] += 1
    total = sum(per_symbol.values())
    return total, per_symbol, examples


def check_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        return None
    except UnicodeDecodeError:
        print(f"Error: not a UTF-8 text file: {path}", file=sys.stderr)
        return None
    return check_text(text, path)


def report(label, total, per_symbol, examples):
    print(f"--- {label} ---")
    if total == 0:
        print("Clean: no banned symbols found.")
        return
    print(f"Found {total} banned symbol(s):")
    for sym, count in per_symbol.items():
        if count:
            print(f"  {BANNED[sym]} ({sym}): {count}")
    print("Examples (line number, symbol, line):")
    for line_no, sym, line in examples:
        print(f"  line {line_no} [{BANNED[sym]}]: {line}")
    print("Fix: remove these symbols, or run script_cleaner.py.")


def main(argv):
    paths = argv[1:]
    grand_total = 0

    if not paths:
        text = sys.stdin.read()
        total, per_symbol, examples = check_text(text, "stdin")
        report("stdin", total, per_symbol, examples)
        return 1 if total else 0

    any_error = False
    for path in paths:
        result = check_file(path)
        if result is None:
            any_error = True
            continue
        total, per_symbol, examples = result
        report(path, total, per_symbol, examples)
        grand_total += total

    if any_error:
        return 2
    return 1 if grand_total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

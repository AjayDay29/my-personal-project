#!/usr/bin/env python3
"""Check a YouTube title against a few basic channel rules.

Rules checked:
- Title must be 100 characters or fewer.
- Title should not contain emojis.
- Title should end with "| movie explanation" (warn only, not required).

Usage:
    python title_checker.py "Your Title Here"
"""

import re
import sys

MAX_LENGTH = 100
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U00002702-\U000027B0"
    "]+"
)


def check_title(title):
    """Return a list of (ok, message) results for the title."""
    results = []
    length = len(title)
    if length <= MAX_LENGTH:
        results.append((True, f"Length OK: {length}/{MAX_LENGTH} characters"))
    else:
        results.append((False, f"Too long: {length} characters (max {MAX_LENGTH})"))
    if EMOJI_PATTERN.search(title):
        results.append((False, "Contains emoji (titles should have none)"))
    else:
        results.append((True, "No emojis found"))
    if title.strip().endswith("| movie explanation"):
        results.append((True, 'Ends with "| movie explanation"'))
    else:
        results.append((False, 'Does not end with "| movie explanation"'))
    return results


def main():
    if len(sys.argv) < 2:
        print('Usage: python title_checker.py "Your Title Here"')
        return
    title = sys.argv[1]
    failed = False
    for ok, message in check_title(title):
        mark = "PASS" if ok else "WARN"
        if not ok:
            failed = True
        print(f"[{mark}] {message}")
    if failed:
        print("Result: title needs fixes.")
    else:
        print("Result: title looks good.")


if __name__ == "__main__":
    main()

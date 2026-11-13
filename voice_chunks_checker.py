#!/usr/bin/env python3
"""Hindi narration voice-chunks checker.

Long narrations are generated in numbered chunks (teamsp takes at
most 2500 characters at a time, so a 25-minute narration is 10-25
files like part01.mp3, part02.mp3 ...). Before joining them, this
checks the folder is complete: every chunk number in the sequence
is present, no number is duplicated, and no chunk is suspiciously
short (under 2 seconds usually means the generation failed).

Each chunk's duration is read with ffprobe, so the total narration
time is printed too -- useful for checking the joined file against
the script's estimated duration before the video edit starts.

Usage:
    python voice_chunks_checker.py chunks-dir/
    python voice_chunks_checker.py chunks-dir/ --min-seconds 5

Needs ffprobe on the PATH. MP3, WAV and M4A files are checked;
other files in the folder are ignored.

Exit code is 0 when the sequence is complete, 1 when a chunk is
missing, duplicated or too short, and 2 on a usage or file error.
"""

import argparse
import os
import re
import subprocess
import sys

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a"}
DEFAULT_MIN_SECONDS = 2.0
NUMBER_RE = re.compile(r"(\d+)\s*$")


def probe_duration(path):
    """Return the duration of an audio file in seconds, or None."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def format_duration(seconds):
    total = round(seconds)
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def chunk_number(filename):
    """Return the trailing number in a file's name, or None.

    part01.mp3 -> 1, chunk-12.wav -> 12, 07.m4a -> 7.
    A file with no trailing number is unnumbered.
    """
    stem = os.path.splitext(filename)[0]
    match = NUMBER_RE.search(stem)
    if match is None:
        return None
    return int(match.group(1))


def check(folder, min_seconds):
    """Check one folder of chunk files. Returns an exit code."""
    if not os.path.isdir(folder):
        print(f"error: no such folder: {folder}", file=sys.stderr)
        return 2

    names = sorted(os.listdir(folder))
    audio = [n for n in names
             if os.path.splitext(n)[1].lower() in SUPPORTED_EXTENSIONS]
    if not audio:
        print(f"error: no .mp3/.wav/.m4a files in {folder}",
              file=sys.stderr)
        return 2

    numbered = {}
    unnumbered = []
    for name in audio:
        number = chunk_number(name)
        if number is None:
            unnumbered.append(name)
        else:
            numbered.setdefault(number, []).append(name)

    problems = []
    durations = {}
    for number in sorted(numbered):
        files = numbered[number]
        if len(files) > 1:
            problems.append(
                f"duplicate chunk {number}: {', '.join(files)}")
        path = os.path.join(folder, files[0])
        duration = probe_duration(path)
        if duration is None:
            problems.append(f"could not read duration of {files[0]}")
            continue
        durations[number] = duration
        if duration < min_seconds:
            problems.append(
                f"chunk {number} is only {duration:.1f}s "
                f"({files[0]}) -- check if the generation failed")

    numbers = sorted(numbered)
    missing = [n for n in range(numbers[0], numbers[-1] + 1)
               if n not in numbered]
    if missing:
        problems.append(
            "missing chunks: " + ", ".join(str(n) for n in missing))

    total = sum(durations.values())
    print(f"Folder:   {folder}")
    print(f"Chunks:   {len(numbered)} numbered "
          f"({numbers[0]}-{numbers[-1]})")
    if unnumbered:
        print(f"Unnumbered files (ignored): {', '.join(unnumbered)}")
    for number in numbers:
        if number in durations:
            print(f"  chunk {number:>2}: {format_duration(durations[number])}"
                  f" ({durations[number]:.1f}s)  "
                  f"{numbered[number][0]}")
    print(f"Total:    {format_duration(total)} ({total:.1f}s)")
    if durations:
        average = total / len(durations)
        longest = max(durations.items(), key=lambda item: item[1])
        shortest = min(durations.items(), key=lambda item: item[1])
        print(f"Average:  {average:.1f}s per chunk")
        print(f"Longest:  chunk {longest[0]} "
              f"({format_duration(longest[1])})")
        print(f"Shortest: chunk {shortest[0]} "
              f"({format_duration(shortest[1])})")

    if problems:
        print("Problems:")
        for problem in problems:
            print(f"  ! {problem}")
        return 1
    print("OK: sequence complete, no chunk missing or too short.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check a folder of numbered narration chunks "
                    "is complete before joining.")
    parser.add_argument("folder", help="folder holding the chunk files")
    parser.add_argument("--min-seconds", type=float,
                        default=DEFAULT_MIN_SECONDS,
                        help="shortest acceptable chunk, in seconds "
                             "(default 2)")
    args = parser.parse_args(argv)

    if args.min_seconds <= 0:
        print("error: --min-seconds must be more than 0",
              file=sys.stderr)
        return 2
    return check(args.folder, args.min_seconds)


if __name__ == "__main__":
    sys.exit(main())

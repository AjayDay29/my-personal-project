#!/usr/bin/env python3
"""Hindi narration silence trimmer.

Strips pauses longer than 0.05 seconds from a narration audio file,
using the channel's locked silence-removal rule (ffmpeg silenceremove,
start_periods=1, stop_periods=-1, -45dB). How much shorter the audio
gets depends on how many pauses the narration has -- a 2-minute
excerpt of the Ritual narration came to 0.92x as long, while the
music-backed 47 Ronin clone barely changed (1.00x), because music
fills the gaps. Use the trimmed file for Shorts narration and keep
the RAW file for video-dub sync, since trimming changes the timing.

The input file is never changed. The trimmed audio is always written
to a NEW file next to the input (``<name>-trimmed.mp3`` by default),
and an existing output file is never overwritten unless --force is
given. Original and trimmed durations, the seconds removed and the
length ratio are printed.

Usage:
    python silence_trimmer.py narration.mp3
    python silence_trimmer.py narration.mp3 narration-trimmed.mp3
    python silence_trimmer.py narration.mp3 --silence 0.1
    python silence_trimmer.py narration.mp3 --force

Needs ffmpeg and ffprobe on the PATH. MP3, WAV and M4A inputs are
supported; MP3 output uses libmp3lame at 128k, the same bitrate as
the channel's narration exports.

Exit code is 0 on success, 1 when ffmpeg fails, and 2 on a usage
or file error.
"""

import argparse
import os
import subprocess
import sys

DEFAULT_SILENCE = 0.05
DEFAULT_THRESHOLD_DB = -45
SUPPORTED_EXTENSIONS = {".mp3": "libmp3lame", ".wav": "pcm_s16le",
                        ".m4a": "aac"}


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
    return f"{minutes}:{secs:02d}"


def silence_filter(silence, threshold_db):
    """The locked silence-removal filter: keep at most <silence>
    seconds of quiet at -45dB, at the start and between words."""
    return (
        f"silenceremove=start_periods=1:start_duration={silence}:"
        f"start_threshold={threshold_db}dB:"
        f"stop_periods=-1:stop_duration={silence}:"
        f"stop_threshold={threshold_db}dB"
    )


def trim(input_path, output_path, silence, threshold_db):
    """Run ffmpeg with the locked filter. Returns True on success."""
    _, ext = os.path.splitext(input_path)
    codec = SUPPORTED_EXTENSIONS[ext.lower()]
    command = ["ffmpeg", "-y", "-v", "error", "-i", input_path,
               "-af", silence_filter(silence, threshold_db),
               "-c:a", codec]
    if codec == "libmp3lame":
        command += ["-b:a", "128k"]
    command.append(output_path)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg failed: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Strip pauses longer than 0.05s from narration audio.")
    parser.add_argument("input", help="input audio file (.mp3, .wav, .m4a)")
    parser.add_argument("output", nargs="?",
                        help="output file (default: <name>-trimmed<ext>)")
    parser.add_argument("--silence", type=float, default=DEFAULT_SILENCE,
                        help="max silence to keep, in seconds (default 0.05)")
    parser.add_argument("--threshold", type=int,
                        default=DEFAULT_THRESHOLD_DB,
                        help="silence threshold in dB (default -45)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite the output file if it exists")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.input):
        print(f"error: no such file: {args.input}", file=sys.stderr)
        return 2
    _, ext = os.path.splitext(args.input)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        print(f"error: unsupported format '{ext}' "
              f"(use .mp3, .wav or .m4a)", file=sys.stderr)
        return 2
    if args.silence <= 0:
        print("error: --silence must be more than 0", file=sys.stderr)
        return 2

    output = args.output
    if output is None:
        stem, ext = os.path.splitext(args.input)
        output = f"{stem}-trimmed{ext}"
    if os.path.exists(output) and not args.force:
        print(f"error: {output} already exists "
              f"(use --force to overwrite)", file=sys.stderr)
        return 2

    original = probe_duration(args.input)
    if original is None:
        print(f"error: could not read duration of {args.input}",
              file=sys.stderr)
        return 2

    if not trim(args.input, output, args.silence, args.threshold):
        return 1

    trimmed = probe_duration(output)
    if trimmed is None:
        print(f"error: could not read duration of {output}",
              file=sys.stderr)
        return 1

    removed = original - trimmed
    ratio = trimmed / original if original > 0 else 0
    print(f"Input:    {args.input}")
    print(f"Output:   {output}")
    print(f"Original: {format_duration(original)} ({original:.1f}s)")
    print(f"Trimmed:  {format_duration(trimmed)} ({trimmed:.1f}s)")
    print(f"Removed:  {removed:.1f}s of pauses")
    print(f"Ratio:    {ratio:.2f}x as long")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Filmy Station-format Short package checker.

Checks one Shorts package folder before it goes live, against the
Filmy Station formula Ajay copied on 11 Nov 2026: one film, one
mystery, about 2 minutes, a Devanagari question title starting with
aakhir/kya plus an emoji, 3-5 Shorts a week.

The folder must hold script.txt and title.txt. A vertical thumbnail
file (thumbnail.jpg or thumbnail.png) is optional: Shorts can reuse
the long-form thumbnail or a video frame, so a missing thumbnail is
only a warning -- but if one is given it must be vertical 9:16.

Checks:
- script: at most 2500 characters, so the Marcus voice fits in a
  single teamsp.org generation; estimated narration 60-150 seconds
  at 3.3 words per second (warn only outside that range).
- title: starts with "aakhir" or "kya" (Devanagari question),
  100 characters or fewer, and contains an emoji (warn only --
  the three Not Without Hope titles delivered 11 Nov 2026 had
  none yet, and the emoji still needs adding).
- thumbnail (if present): JPG or PNG, vertical 9:16, at least
  720 pixels wide, 2 MB or less (YouTube's thumbnail limit).

Usage:
    python shorts_package_checker.py shorts-package-dir/

Exit code is 0 when the package passes (warnings are allowed),
1 when any check fails, and 2 on a usage or file error.
No extra libraries are needed -- image size is read from the
file headers.
"""

import argparse
import re
import struct
import sys
from pathlib import Path

MAX_SCRIPT_CHARS = 2500
WORDS_PER_SECOND = 3.3
MIN_DURATION_SECONDS = 60
MAX_DURATION_SECONDS = 150
MAX_TITLE_CHARS = 100
QUESTION_STARTERS = ("आखिर", "क्या")
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF"
    "\U00002702-\U000027B0"
    "]+"
)
MAX_THUMBNAIL_BYTES = 2_000_000
MIN_THUMBNAIL_WIDTH = 720


def png_size(path):
    """Return (width, height) of a PNG, or None if unreadable."""
    try:
        with open(path, "rb") as f:
            header = f.read(33)
    except OSError:
        return None
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def jpeg_size(path):
    """Return (width, height) of a JPEG, or None if unreadable."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 2 or data[:2] != b"\xff\xd8":
        return None
    pos = 2
    while pos + 9 < len(data):
        if data[pos] != 0xFF:
            return None
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        if pos + 4 > len(data):
            return None
        length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            if pos + 9 > len(data):
                return None
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + length
    return None


def image_size(path):
    suffix = path.suffix.lower()
    if suffix == ".png":
        return png_size(path)
    if suffix in (".jpg", ".jpeg"):
        return jpeg_size(path)
    return None


def check_script(path, problems, warnings):
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        problems.append(f"cannot read {path}")
        return
    if not text:
        problems.append("script.txt is empty")
        return
    chars = len(text)
    if chars > MAX_SCRIPT_CHARS:
        problems.append(
            f"script is {chars} characters, over the {MAX_SCRIPT_CHARS} "
            "teamsp single-chunk limit -- split it before generating "
            "the Marcus voice")
    else:
        print(f"  script: {chars}/{MAX_SCRIPT_CHARS} characters")
    words = len(text.split())
    seconds = words / WORDS_PER_SECOND
    minutes = int(seconds // 60)
    rest = int(seconds % 60)
    print(f"  estimated narration: {words} words, about "
          f"{minutes}:{rest:02d} at {WORDS_PER_SECOND} words/second")
    if seconds < MIN_DURATION_SECONDS or seconds > MAX_DURATION_SECONDS:
        warnings.append(
            f"estimated narration {minutes}:{rest:02d} is outside the "
            f"about-2-minute Shorts range "
            f"({MIN_DURATION_SECONDS}-{MAX_DURATION_SECONDS} seconds)")


def check_title(path, problems, warnings):
    try:
        title = path.read_text(encoding="utf-8").strip()
    except OSError:
        problems.append(f"cannot read {path}")
        return
    if not title:
        problems.append("title.txt is empty")
        return
    if not title.startswith(QUESTION_STARTERS):
        problems.append(
            'title does not start with "आखिर" or "क्या" '
            "(Filmy Station question-title format)")
    if len(title) > MAX_TITLE_CHARS:
        problems.append(
            f"title is {len(title)} characters (max {MAX_TITLE_CHARS})")
    if not EMOJI_PATTERN.search(title):
        warnings.append(
            "title has no emoji (Filmy Station titles carry one)")
    print(f'  title: "{title}" ({len(title)} characters)')


def check_thumbnail(path, problems, warnings):
    if path is None:
        warnings.append(
            "no vertical thumbnail in the package -- Shorts will use "
            "a video frame or the reused long-form thumbnail")
        return
    suffix = path.suffix.lower()
    if suffix not in (".jpg", ".jpeg", ".png"):
        problems.append(
            f"thumbnail format {suffix} is not JPG or PNG")
        return
    try:
        size_bytes = path.stat().st_size
    except OSError:
        problems.append(f"cannot read {path}")
        return
    size = image_size(path)
    if size is None:
        problems.append(f"cannot read image size from {path}")
        return
    width, height = size
    if height == 0:
        problems.append("thumbnail height is 0")
        return
    ratio = width / height
    if abs(ratio - 9 / 16) > 0.01:
        problems.append(
            f"thumbnail is {width}x{height}, not vertical 9:16")
    if width < MIN_THUMBNAIL_WIDTH:
        problems.append(
            f"thumbnail width is {width}px, under the 720px minimum")
    if size_bytes > MAX_THUMBNAIL_BYTES:
        problems.append(
            f"thumbnail is {size_bytes / 1_000_000:.1f} MB, over "
            "YouTube's 2 MB thumbnail limit")
    if (width, height) != (1080, 1920):
        warnings.append(
            f"thumbnail is {width}x{height}, not the 1080x1920 "
            "Shorts size")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check a Filmy Station-format Short package.")
    parser.add_argument(
        "package_dir", help="folder with script.txt and title.txt")
    args = parser.parse_args(argv)

    folder = Path(args.package_dir)
    if not folder.is_dir():
        print(f"error: folder not found: {folder}", file=sys.stderr)
        return 2

    problems = []
    warnings = []
    script_path = folder / "script.txt"
    title_path = folder / "title.txt"
    if not script_path.is_file():
        problems.append("script.txt is missing from the package")
    else:
        check_script(script_path, problems, warnings)
    if not title_path.is_file():
        problems.append("title.txt is missing from the package")
    else:
        check_title(title_path, problems, warnings)
    thumb = None
    for name in ("thumbnail.jpg", "thumbnail.jpeg", "thumbnail.png"):
        candidate = folder / name
        if candidate.is_file():
            thumb = candidate
            break
    check_thumbnail(thumb, problems, warnings)

    for problem in problems:
        print(f"FAIL: {problem}")
    for warning in warnings:
        print(f"WARN: {warning}")
    if not problems and not warnings:
        print(f"PASS: {folder} is ready to post")
    elif not problems:
        print(f"PASS with warnings: {folder} is ready to post")
    else:
        print(f"FAIL: {folder} is not ready to post")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

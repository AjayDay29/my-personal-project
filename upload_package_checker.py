#!/usr/bin/env python3
"""YouTube upload package checker.

Ajay's rule: nothing goes on a channel without his yes, and only
after the whole package is checked. Before an upload, a package
folder must hold everything -- title, description, tags and
thumbnail -- and each part must pass the channel's locked formula:

- title: 100 characters or fewer, no emojis, ends with
  "movie explanation" (his titles end "| movie explanation" or
  "| The Ritual movie explanation")
- description: 5000 characters or fewer, at most 15 hashtags
  (YouTube ignores everything beyond 15), a Movie Details block,
  a Related line, a fair-use disclaimer, and no email address
- tags: total 500 characters or fewer (YouTube's documented tags
  limit); a tag over 30 characters is only a warning, because
  YouTube publishes no per-tag limit and his own finalized tags
  run longer than 30 characters
- thumbnail: a JPG or PNG image, 16:9, at least 1280 pixels wide

Usage:
    python upload_package_checker.py package-dir/

The package folder is expected to hold title.txt, description.txt,
tags.txt (comma-separated) and thumbnail.jpg or thumbnail.png.
Exit code is 0 when the package passes (warnings are allowed),
1 when any check fails, and 2 on a usage or file error.
"""

import argparse
import re
import struct
import sys
from pathlib import Path

MAX_TITLE_CHARS = 100
MAX_DESCRIPTION_CHARS = 5000
MAX_HASHTAGS = 15
MAX_TAGS_CHARS = 500
MAX_TAG_CHARS = 30
MIN_THUMBNAIL_WIDTH = 1280

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HASHTAG_RE = re.compile(r"#\w+")
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF"
    "\U00002B00-\U00002BFF\U0000FE0F]")


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        return None


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
            height, width = struct.unpack(
                ">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + length
    return None


def image_size(path):
    if path.suffix.lower() == ".png":
        return png_size(path)
    return jpeg_size(path)


def check_title(text, problems, warnings):
    if text is None:
        problems.append("title.txt is missing")
        return
    title = text.strip()
    if not title:
        problems.append("title.txt is empty")
        return
    if len(title) > MAX_TITLE_CHARS:
        problems.append(
            f"title is {len(title)} characters, over the 100 limit")
    if EMOJI_RE.search(title):
        problems.append("title contains an emoji")
    if not title.lower().endswith("movie explanation"):
        problems.append(
            'title does not end with "movie explanation"')


def check_description(text, problems, warnings):
    if text is None:
        problems.append("description.txt is missing")
        return
    if not text.strip():
        problems.append("description.txt is empty")
        return
    if len(text) > MAX_DESCRIPTION_CHARS:
        problems.append(
            f"description is {len(text)} characters, over the 5000 limit")
    tags = HASHTAG_RE.findall(text)
    if len(tags) > MAX_HASHTAGS:
        problems.append(
            f"description has {len(tags)} hashtags, over the 15 limit "
            "(YouTube ignores everything beyond 15)")
    if "Movie Details" not in text:
        problems.append("description has no Movie Details block")
    if "Related:" not in text and "Related" not in text:
        problems.append("description has no Related line")
    if "Disclaimer" not in text and "disclaimer" not in text:
        problems.append("description has no fair-use disclaimer")
    if EMAIL_RE.search(text):
        problems.append("description contains an email address")


def check_tags(text, problems, warnings):
    if text is None:
        problems.append("tags.txt is missing")
        return
    tags = [t.strip() for t in text.split(",") if t.strip()]
    if not tags:
        problems.append("tags.txt has no tags")
        return
    if len(text.strip()) > MAX_TAGS_CHARS:
        problems.append(
            f"tags total {len(text.strip())} characters, "
            "over YouTube's 500 limit")
    for tag in tags:
        if len(tag) > MAX_TAG_CHARS:
            warnings.append(
                f'tag "{tag}" is {len(tag)} characters -- YouTube '
                "publishes no per-tag limit, but long tags rarely "
                "match real searches")


def check_thumbnail(folder, problems, warnings):
    for name in ("thumbnail.jpg", "thumbnail.jpeg", "thumbnail.png"):
        path = folder / name
        if path.exists():
            break
    else:
        problems.append(
            "thumbnail.jpg or thumbnail.png is missing")
        return
    size = image_size(path)
    if size is None:
        problems.append(f"cannot read image size of {path.name}")
        return
    width, height = size
    if height == 0:
        problems.append(f"{path.name} has zero height")
        return
    ratio = width / height
    if abs(ratio - 16 / 9) > 0.02:
        problems.append(
            f"thumbnail is {width}x{height}, not 16:9")
    if width < MIN_THUMBNAIL_WIDTH:
        problems.append(
            f"thumbnail is {width}px wide, under the 1280 minimum")


def check_package(folder):
    problems = []
    warnings = []
    check_title(read_text(folder / "title.txt"), problems, warnings)
    check_description(
        read_text(folder / "description.txt"), problems, warnings)
    check_tags(read_text(folder / "tags.txt"), problems, warnings)
    check_thumbnail(folder, problems, warnings)
    return problems, warnings


def main(argv):
    parser = argparse.ArgumentParser(
        description="Check a YouTube upload package folder against "
                    "the channel's locked formula.")
    parser.add_argument("folder", help="package folder to check")
    args = parser.parse_args(argv)
    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Error: not a folder: {folder}", file=sys.stderr)
        return 2
    problems, warnings = check_package(folder)
    print(f"--- {folder} ---")
    if warnings:
        print(f"{len(warnings)} warning(s):")
        for warning in warnings:
            print(f"  WARN: {warning}")
    if not problems:
        print("Pass: package is complete and follows the formula.")
        return 0
    print(f"Found {len(problems)} problem(s):")
    for problem in problems:
        print(f"  FAIL: {problem}")
    print("Fix the list above before uploading -- nothing goes live "
          "until the package passes and Ajay says yes.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

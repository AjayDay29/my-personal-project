#!/usr/bin/env python3
"""YouTube thumbnail checker.

Ajay's rule: a thumbnail must be right before it goes live, and
YouTube only accepts a thumbnail file up to 2 MB. On 9 Nov 2026 a
95 MB 8K version of the Not Without Hope thumbnail was made on his
order before anyone checked the size -- YouTube would never have
accepted it, and the 1.82 MB 4K version was the one to upload.
This tool catches that before the file is sent anywhere.

Checks a thumbnail image against the upload rules:

- format: JPG, PNG, GIF or BMP (the formats YouTube accepts)
- size: 16:9, the YouTube thumbnail shape
- width: at least 640 pixels (YouTube's minimum); 1280x720 is
  the channel's upload size, anything bigger is only a warning
- file size: 2 MB or less (YouTube's thumbnail limit)

Usage:
    python thumbnail_checker.py thumbnail.jpg
    python thumbnail_checker.py thumbnail.png

Exit code is 0 when the thumbnail passes (warnings are allowed),
1 when any check fails, and 2 on a usage or file error.
No extra libraries are needed -- image size is read from the
file headers, the same way upload_package_checker.py does it.
"""

import argparse
import struct
import sys
from pathlib import Path

ACCEPTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
MAX_FILE_BYTES = 2_000_000
MIN_WIDTH = 640
UPLOAD_WIDTH = 1280
UPLOAD_HEIGHT = 720


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


def gif_size(path):
    """Return (width, height) of a GIF, or None if unreadable."""
    try:
        with open(path, "rb") as f:
            header = f.read(10)
    except OSError:
        return None
    if len(header) < 10 or header[:6] not in (b"GIF87a", b"GIF89a"):
        return None
    width, height = struct.unpack("<HH", header[6:10])
    return width, height


def bmp_size(path):
    """Return (width, height) of a BMP, or None if unreadable."""
    try:
        with open(path, "rb") as f:
            header = f.read(26)
    except OSError:
        return None
    if len(header) < 26 or header[:2] != b"BM":
        return None
    width, height = struct.unpack("<ii", header[18:26])
    return width, abs(height)


def image_size(path):
    suffix = path.suffix.lower()
    if suffix == ".png":
        return png_size(path)
    if suffix in (".jpg", ".jpeg"):
        return jpeg_size(path)
    if suffix == ".gif":
        return gif_size(path)
    if suffix == ".bmp":
        return bmp_size(path)
    return None


def check_thumbnail(path, problems, warnings):
    suffix = path.suffix.lower()
    if suffix not in ACCEPTED_FORMATS:
        problems.append(
            f"format {suffix or '(none)'} is not a YouTube thumbnail "
            "format (JPG, PNG, GIF or BMP)")
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
        problems.append("image height is 0")
        return
    ratio = width / height
    if abs(ratio - 16 / 9) > 0.01:
        problems.append(
            f"image is {width}x{height}, not 16:9")
    if width < MIN_WIDTH:
        problems.append(
            f"width is {width}px, under YouTube's 640px minimum")
    if size_bytes > MAX_FILE_BYTES:
        problems.append(
            f"file is {size_bytes / 1_000_000:.1f} MB, over "
            "YouTube's 2 MB thumbnail limit")
    if (width, height) != (UPLOAD_WIDTH, UPLOAD_HEIGHT):
        warnings.append(
            f"image is {width}x{height}, not the 1280x720 upload "
            "size")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check a YouTube thumbnail before upload.")
    parser.add_argument("thumbnail", help="thumbnail image file")
    args = parser.parse_args(argv)

    path = Path(args.thumbnail)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    problems = []
    warnings = []
    check_thumbnail(path, problems, warnings)

    for problem in problems:
        print(f"FAIL: {problem}")
    for warning in warnings:
        print(f"WARN: {warning}")
    if not problems and not warnings:
        print(f"PASS: {path} is ready to upload")
    elif not problems:
        print(f"PASS with warnings: {path} is ready to upload")
    else:
        print(f"FAIL: {path} is not ready to upload")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

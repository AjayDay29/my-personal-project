#!/usr/bin/env python3
"""YouTube thumbnail sizer.

Shrinks a thumbnail to a file YouTube will accept, without changing
what it looks like. YouTube only accepts a thumbnail up to 2 MB, and
1280x720 is the size it shows -- anything bigger only makes the file
heavier. On 9 Nov 2026 a 95 MB 8K version of the Not Without Hope
thumbnail was made before anyone checked the size, and on 10 Nov 2026
a 174 KB thumbnail was asked to be made smaller without losing
quality, when it was already small enough. This tool answers both:
it only shrinks what needs shrinking, and leaves an already-ready
file untouched.

What it does, in order:

- If the image is already a JPG, no wider than 1280 pixels, and
  2 MB or less, it is copied unchanged. No recompression, so no
  quality is lost at all.
- Otherwise it resizes to 1280 pixels wide (keeping the shape) and
  saves as JPG, trying the highest quality first and stepping down
  only until the file fits under 2 MB.
- If even the lowest quality does not fit, it steps the width down
  (1280, then 960, then 640 -- YouTube's minimum width) and tries
  again, so it still returns a usable file instead of failing.
- The output is always JPG. WebP is not used, because YouTube does
  not accept WebP as a thumbnail.

Needs Pillow, the standard Python image library:

    pip install Pillow

Usage:
    python thumbnail_sizer.py thumbnail.png
    python thumbnail_sizer.py thumbnail.png upload-ready.jpg
    python thumbnail_sizer.py thumbnail.jpg --keep-size
    python thumbnail_sizer.py thumbnail.png --width 1280 --max-bytes 2000000

Without an output name, it writes <name>-upload-ready.jpg next to
the input. The input file is never changed.

Exit code is 0 when the output fits under the limit, 1 when it
cannot be made to fit even at the smallest settings, and 2 on a
usage or file error.
"""

import argparse
import io
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is needed for this tool. Install it with:")
    print("    pip install Pillow")
    sys.exit(2)

MAX_FILE_BYTES = 2_000_000
TARGET_WIDTH = 1280
MIN_WIDTH = 640
TOP_QUALITY = 95
LOW_QUALITY = 50
QUALITY_STEP = 5
WIDTH_STEPS = (1280, 960, 640)


def encode_jpeg(image, quality):
    """Encode an image as JPG bytes at the given quality."""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()


def best_jpeg_under_limit(image, limit):
    """Return (bytes, quality) for the best quality that fits, or None."""
    for quality in range(TOP_QUALITY, LOW_QUALITY - 1, -QUALITY_STEP):
        data = encode_jpeg(image, quality)
        if len(data) <= limit:
            return data, quality
    return None


def prepare(image):
    """Return an RGB copy of the image, flattening transparency."""
    if image.mode in ("RGBA", "LA", "PA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        alpha = image.convert("RGBA").split()[-1]
        background.paste(image.convert("RGBA"), mask=alpha)
        return background
    return image.convert("RGB")


def format_size(num_bytes):
    """Format a byte count the way a person reads it."""
    if num_bytes >= 1_000_000:
        return f"{num_bytes / 1_000_000:.2f} MB"
    return f"{num_bytes / 1_000:.1f} KB"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Shrink a thumbnail to a YouTube-ready JPG under 2 MB."
    )
    parser.add_argument("input", help="thumbnail image to shrink")
    parser.add_argument("output", nargs="?",
                        help="output JPG (default: <name>-upload-ready.jpg)")
    parser.add_argument("--width", type=int, default=TARGET_WIDTH,
                        help="resize width in pixels (default: 1280)")
    parser.add_argument("--max-bytes", type=int, default=MAX_FILE_BYTES,
                        help="largest output file in bytes (default: 2000000)")
    parser.add_argument("--keep-size", action="store_true",
                        help="do not resize, only lower the quality")
    args = parser.parse_args(argv)

    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"File not found: {in_path}")
        return 2
    if args.width < MIN_WIDTH:
        print(f"Width must be at least {MIN_WIDTH}, YouTube's minimum.")
        return 2

    out_path = Path(args.output) if args.output else in_path.with_name(
        f"{in_path.stem}-upload-ready.jpg")
    if out_path.resolve() == in_path.resolve():
        print("Output would overwrite the input. Give another output name.")
        return 2

    try:
        image = Image.open(in_path)
        image.load()
    except Exception as exc:
        print(f"Could not open image {in_path}: {exc}")
        return 2

    in_bytes = in_path.stat().st_size
    in_width, in_height = image.size
    print(f"Input:  {in_width}x{in_height}, {format_size(in_bytes)} "
          f"({in_bytes:,} bytes)")

    # Already ready: a JPG at or under the target width and the limit
    # is copied unchanged, so no quality is lost at all.
    if (in_path.suffix.lower() in (".jpg", ".jpeg")
            and in_width <= args.width and in_bytes <= args.max_bytes):
        shutil.copyfile(in_path, out_path)
        print(f"Already upload-ready: copied unchanged to {out_path}")
        print(f"Output: {in_width}x{in_height}, "
              f"{format_size(in_bytes)} ({in_bytes:,} bytes)")
        return 0

    rgb = prepare(image)

    widths = [rgb.size[0]] if args.keep_size else [
        w for w in WIDTH_STEPS if w <= args.width]
    if not widths:
        widths = [args.width]

    for width in widths:
        if rgb.size[0] > width:
            ratio = width / rgb.size[0]
            sized = rgb.resize(
                (width, round(rgb.size[1] * ratio)), Image.LANCZOS)
        else:
            sized = rgb
        result = best_jpeg_under_limit(sized, args.max_bytes)
        if result is not None:
            data, quality = result
            out_path.write_bytes(data)
            saved = in_bytes - len(data)
            print(f"Output: {sized.size[0]}x{sized.size[1]}, "
                  f"{format_size(len(data))} ({len(data):,} bytes), "
                  f"quality {quality}")
            print(f"Saved {format_size(saved)} "
                  f"({100 * saved / in_bytes:.0f}% smaller) -> {out_path}")
            return 0

    print(f"Could not fit under {format_size(args.max_bytes)} even at "
          f"quality {LOW_QUALITY} and {MIN_WIDTH}px wide. "
          "The file was not written.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""THE FIELD WIRE — news-image-20261124 entry program, Akun 15 (@sukmawatihss).

Stdlib-only carrier: copies the pre-rendered entry.png (original artwork
drawn in-session by compose.py, a PIL renderer written in the same build
session) into the grader output directory. No network, no randomness, no
environment input: the same bytes go out on every run.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
MAX_SIDE = 1024


def png_dimensions(path):
    """Read width/height from the PNG IHDR chunk by hand (no libraries)."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file: %s" % path)
    if head[12:16] != b"IHDR":
        raise ValueError("first chunk is not IHDR: %s" % path)
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def verify_gate(path):
    """Fail loudly instead of shipping a file the server gate would refuse."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError("entry.png is %d bytes, over the 1048576 limit" % size)
    width, height = png_dimensions(path)
    if width != MAX_SIDE or height != MAX_SIDE:
        raise ValueError("entry.png is %dx%d, must be exactly 1024x1024" % (width, height))
    return size, width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    size, width, height = verify_gate(dest)
    print("entry.png: %d bytes, %dx%d" % (size, width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""THE SOUTHERN CROSS POST - carrier for the NI24 entry image.

Standard library only. This program carries the finished front page:
it reads entry.png from its own directory, checks the bounty gate
(exactly 1024x1024 pixels, at most 1 MiB), and writes the identical
bytes to the output entry.png. Running it any number of times always
produces a byte-identical output, because the output is a pure copy
of the shipped entry.png and nothing else is generated.

Output directory: MAKEFUN_OUTPUT_DIR when set, otherwise the current
working directory. The file written is always named entry.png.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1024 * 1024  # 1 MiB gate
EXPECTED_W = 1024
EXPECTED_H = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_entry(path):
    with open(path, "rb") as fh:
        return fh.read()


def check_gate(data):
    """Return (width, height) or raise ValueError when the gate fails."""
    if len(data) > MAX_BYTES:
        raise ValueError("entry.png is %d bytes, over the 1 MiB gate" % len(data))
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("entry.png is not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if width != EXPECTED_W or height != EXPECTED_H:
        raise ValueError(
            "entry.png is %dx%d, gate requires %dx%d"
            % (width, height, EXPECTED_W, EXPECTED_H)
        )
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    data = read_entry(src)
    width, height = check_gate(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    if os.path.abspath(dst) != os.path.abspath(src):
        with open(dst, "wb") as fh:
            fh.write(data)

    digest = hashlib.sha256(data).hexdigest()
    print("entry.png: %d bytes, %dx%d, sha256 %s" % (len(data), width, height, digest))
    print("written to: %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())

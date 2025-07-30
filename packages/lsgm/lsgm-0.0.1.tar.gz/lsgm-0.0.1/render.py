#! /usr/bin/env python3
"""Dummy build."""

from pathlib import Path

from rwx.fs import make_directory, write

if __name__ == "__main__":
    out = Path(__file__).parent / "out" / "web"
    make_directory(out)
    write(out / "index.html", "lsgm.rwx.work")

#!/usr/bin/env python3
"""Convert basic SRT and WebVTT subtitles and shift their timestamps. Output is written to a new file."""

import argparse
import re
from pathlib import Path

STAMP = r"\d{2,}:\d{2}:\d{2}[,.]\d{3}|\d{2}:\d{2}[,.]\d{3}"


def milliseconds(stamp):
    parts = stamp.replace(",", ".").split(":")
    if len(parts) == 2:
        parts.insert(0, "0")
    h, m = map(int, parts[:2])
    s, ms = map(int, parts[2].split("."))
    if m > 59 or s > 59:
        raise ValueError("Invalid timestamp")
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def parse(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip().lstrip("\ufeff")):
        lines = block.splitlines()
        if not lines:
            continue
        if lines[0].startswith(("WEBVTT", "NOTE", "STYLE", "REGION")):
            continue
        index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if index is None:
            raise ValueError("Unrecognized subtitle block")
        match = re.fullmatch(rf"({STAMP})\s+-->\s+({STAMP})\s*", lines[index])
        if not match:
            raise ValueError("Unsupported timestamp line or cue settings")
        start, end = map(milliseconds, match.groups())
        if end <= start or index + 1 == len(lines):
            raise ValueError("Cue must have text and positive duration")
        cues.append((start, end, "\n".join(lines[index + 1:])))
    if not cues:
        raise ValueError("No subtitle cues found")
    return cues


def stamp(ms, separator):
    seconds, fraction = divmod(ms, 1000)
    minutes, second = divmod(seconds, 60)
    hour, minute = divmod(minutes, 60)
    return f"{hour:02}:{minute:02}:{second:02}{separator}{fraction:03}"


def convert(text, fmt, shift):
    cues = parse(text)
    blocks = []
    for i, (start, end, content) in enumerate(cues, 1):
        start, end = max(0, start + shift), max(0, end + shift)
        if end <= start:
            raise ValueError("Shift collapses a cue before time zero")
        sep = "," if fmt == "srt" else "."
        timing = f"{stamp(start, sep)} --> {stamp(end, sep)}\n{content}"
        blocks.append(f"{i}\n{timing}" if fmt == "srt" else timing)
    return ("WEBVTT\n\n" if fmt == "vtt" else "") + "\n\n".join(blocks) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--format", choices=["srt", "vtt"], required=True)
    p.add_argument("--shift-ms", type=int, default=0)
    a = p.parse_args()
    try:
        result = convert(a.file.read_text(encoding="utf-8"), a.format, a.shift_ms)
        with a.output.open("x", encoding="utf-8") as f:
            f.write(result)
    except (OSError, UnicodeError, ValueError) as exc:
        p.exit(2, f"Conversion error: {exc}\n")
    print(f"Wrote {a.output}")


if __name__ == "__main__":
    main()

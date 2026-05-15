#!/usr/bin/env python3
"""Scan inbox folders and list files waiting for ingest."""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INBOX_DIR = REPO_ROOT / "inbox"
INGEST_QUEUE_PATH = REPO_ROOT / "operations" / "librarian" / "INGEST_QUEUE.md"

IGNORE_FILES = {".DS_Store", ".gitkeep", "README.md", "Thumbs.db", ".gitignore"}
IGNORE_PREFIXES = (".", "__")

TYPE_MAP = {
    ".md": "markdown",
    ".txt": "text",
    ".rtf": "text",
    ".docx": "text",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".svg": "image",
    ".webp": "image",
    ".tiff": "image",
    ".tif": "image",
    ".bmp": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".flac": "audio",
    ".aiff": "audio",
    ".aif": "audio",
    ".ogg": "audio",
    ".m4a": "audio",
    ".mid": "audio",
    ".midi": "audio",
    ".mp4": "video",
    ".mov": "video",
    ".avi": "video",
    ".mkv": "video",
    ".webm": "video",
    ".m3u": "playlist",
    ".m3u8": "playlist",
    ".pls": "playlist",
    ".json": "data",
    ".csv": "data",
    ".html": "text",
    ".htm": "text",
    ".zip": "archive",
    ".gz": "archive",
    ".tar": "archive",
}

LANE_MAP = {
    "personal_writing": "personal_writing",
    "theory": "theory",
    "visual": "visual",
    "music": "music",
    "voice": "voice",
    "links": "links",
    "playlists": "playlists",
    "web_clips": "web_clips",
}

PRIVACY_DEFAULTS = {
    "personal_writing": "personal",
    "theory": "public",
    "visual": "personal",
    "music": "personal",
    "voice": "private",
    "links": "public",
    "playlists": "public",
    "web_clips": "public",
}


def source_id(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT)
    return hashlib.sha256(str(rel).encode()).hexdigest()[:12]


def detect_type(path: Path) -> str:
    ext = path.suffix.lower()
    return TYPE_MAP.get(ext, "unknown")


def detect_lane(path: Path) -> str:
    rel = path.relative_to(INBOX_DIR)
    parts = rel.parts
    if parts:
        return LANE_MAP.get(parts[0], "unknown")
    return "unknown"


def should_ignore(path: Path) -> bool:
    name = path.name
    if name in IGNORE_FILES:
        return True
    if any(name.startswith(p) for p in IGNORE_PREFIXES):
        return True
    return False


def scan_inbox():
    sources = []
    if not INBOX_DIR.exists():
        return sources

    for root, dirs, files in os.walk(INBOX_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in sorted(files):
            fpath = Path(root) / fname
            if should_ignore(fpath):
                continue
            rel_path = fpath.relative_to(REPO_ROOT)
            lane = detect_lane(fpath)
            sources.append({
                "source_id": source_id(fpath),
                "path": str(rel_path),
                "filename": fname,
                "type": detect_type(fpath),
                "lane": lane,
                "privacy_default": PRIVACY_DEFAULTS.get(lane, "personal"),
                "size_bytes": fpath.stat().st_size,
                "modified": datetime.fromtimestamp(fpath.stat().st_mtime).isoformat(),
            })
    return sources


def write_ingest_queue(sources):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# INGEST_QUEUE.md",
        "",
        f"Sources waiting for processing. Populated by `scripts/librarian/scan_inbox.py`.",
        "",
        f"Last scan: {now}",
        "",
    ]

    if not sources:
        lines.append("## Queue")
        lines.append("")
        lines.append("_No sources found in inbox._")
    else:
        lines.append(f"## Queue ({len(sources)} sources)")
        lines.append("")
        lines.append("| # | Source ID | File | Type | Lane | Privacy | Size | Modified |")
        lines.append("|---|----------|------|------|------|---------|------|----------|")
        for i, s in enumerate(sources, 1):
            size_kb = s["size_bytes"] / 1024
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"
            lines.append(
                f"| {i} | `{s['source_id']}` | `{s['filename']}` | {s['type']} "
                f"| {s['lane']} | {s['privacy_default']} | {size_str} | {s['modified'][:10]} |"
            )

    lines.append("")

    INGEST_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    INGEST_QUEUE_PATH.write_text("\n".join(lines), encoding="utf-8")
    return sources


def main():
    sources = scan_inbox()
    write_ingest_queue(sources)
    print(f"[scan_inbox] Scanned inbox: {len(sources)} sources found")
    for s in sources:
        print(f"  {s['source_id']} | {s['path']} | {s['type']} | {s['lane']}")
    return sources


if __name__ == "__main__":
    main()

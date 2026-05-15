#!/usr/bin/env python3
"""Build or update the SOURCE_MANIFEST.md from inbox and wiki state."""

import os
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INBOX_DIR = REPO_ROOT / "inbox"
WIKI_DIR = REPO_ROOT / "wiki"
STUBS_DIR = WIKI_DIR / "outputs" / "session_reports" / "metadata_stubs"
SUMMARIES_DIR = WIKI_DIR / "theory" / "source_summaries"
MANIFEST_PATH = REPO_ROOT / "operations" / "librarian" / "SOURCE_MANIFEST.md"

IDENTITY_LANES = {"personal_writing", "voice"}
STYLE_BIBLE_LANES = {"visual", "music", "voice"}
THEORY_LANES = {"theory", "links", "web_clips"}
SOCIAL_LANES = set()


def list_stubs():
    stubs = {}
    if not STUBS_DIR.exists():
        return stubs
    for f in STUBS_DIR.iterdir():
        if f.suffix == ".md" and f.name != "README.md":
            content = f.read_text(encoding="utf-8")
            sid = f.stem
            has_summary = False
            for line in content.split("\n"):
                if "summary_status:" in line and "complete" in line.lower():
                    has_summary = True
            stubs[sid] = {
                "stub_path": str(f.relative_to(REPO_ROOT)),
                "has_summary": has_summary,
            }
    return stubs


def list_summaries():
    summaries = set()
    if not SUMMARIES_DIR.exists():
        return summaries
    for f in SUMMARIES_DIR.iterdir():
        if f.suffix == ".md" and f.name != "README.md":
            summaries.add(f.stem)
    return summaries


def main():
    try:
        from scan_inbox import scan_inbox
    except ImportError:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from scan_inbox import scan_inbox

    sources = scan_inbox()
    stubs = list_stubs()
    summaries = list_summaries()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    missing_metadata = []
    missing_summaries = []
    needs_review = []
    identity_sources = []
    style_bible_sources = []
    theory_sources = []
    social_sources = []

    for s in sources:
        sid = s["source_id"]
        has_stub = sid in stubs
        has_summary = stubs.get(sid, {}).get("has_summary", False) or sid in summaries

        if not has_stub:
            missing_metadata.append(s)
        if not has_summary:
            missing_summaries.append(s)
        if s.get("privacy_default") in ("private", "personal"):
            needs_review.append(s)
        if s.get("lane") in IDENTITY_LANES:
            identity_sources.append(s)
        if s.get("lane") in STYLE_BIBLE_LANES:
            style_bible_sources.append(s)
        if s.get("lane") in THEORY_LANES:
            theory_sources.append(s)

    lines = [
        "# SOURCE_MANIFEST.md",
        "",
        f"Complete source inventory. Populated by `scripts/librarian/build_source_manifest.py`.",
        "",
        f"Last update: {now}",
        "",
        f"## Summary",
        "",
        f"- **Total sources in inbox:** {len(sources)}",
        f"- **Sources with metadata stubs:** {len(stubs)}",
        f"- **Missing metadata:** {len(missing_metadata)}",
        f"- **Missing summaries:** {len(missing_summaries)}",
        f"- **Requiring human review:** {len(needs_review)}",
        f"- **Identity-relevant sources:** {len(identity_sources)}",
        f"- **Style-bible-relevant sources:** {len(style_bible_sources)}",
        f"- **Theory-relevant sources:** {len(theory_sources)}",
        "",
    ]

    if sources:
        lines.extend([
            "## All Sources",
            "",
            "| Source ID | File | Type | Lane | Has Stub | Has Summary | Review |",
            "|----------|------|------|------|----------|-------------|--------|",
        ])
        for s in sources:
            sid = s["source_id"]
            has_stub = "yes" if sid in stubs else "**NO**"
            has_summary = "yes" if stubs.get(sid, {}).get("has_summary", False) else "**NO**"
            review = "required" if s in needs_review else "ok"
            lines.append(
                f"| `{sid}` | `{s['filename']}` | {s['type']} "
                f"| {s['lane']} | {has_stub} | {has_summary} | {review} |"
            )
        lines.append("")

    if missing_metadata:
        lines.extend([
            "## Missing Metadata",
            "",
            "These sources have no metadata stub yet:",
            "",
        ])
        for s in missing_metadata:
            lines.append(f"- `{s['path']}`")
        lines.append("")

    if missing_summaries:
        lines.extend([
            "## Missing Summaries",
            "",
            "These sources have not been summarized:",
            "",
        ])
        for s in missing_summaries:
            lines.append(f"- `{s['path']}`")
        lines.append("")

    if needs_review:
        lines.extend([
            "## Requiring Human Review",
            "",
        ])
        for s in needs_review:
            lines.append(f"- `{s['path']}` ({s['privacy_default']})")
        lines.append("")

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[build_source_manifest] Manifest updated: {len(sources)} sources, {len(missing_metadata)} missing metadata, {len(missing_summaries)} missing summaries")


if __name__ == "__main__":
    main()

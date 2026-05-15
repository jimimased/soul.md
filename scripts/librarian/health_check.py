#!/usr/bin/env python3
"""Run a wiki health check and report issues."""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
INBOX_DIR = REPO_ROOT / "inbox"
STUBS_DIR = WIKI_DIR / "outputs" / "session_reports" / "metadata_stubs"
HEALTH_CHECK_PATH = REPO_ROOT / "operations" / "librarian" / "HEALTH_CHECK.md"

STYLE_BIBLE_PATHS = [
    REPO_ROOT / "aesthetic_corpus" / "voice" / "VOICE_STYLE_CARD.md",
    REPO_ROOT / "aesthetic_corpus" / "visual" / "VISUAL_STYLE_BIBLE.md",
    REPO_ROOT / "aesthetic_corpus" / "music" / "MUSIC_STYLE_BIBLE.md",
]

IDENTITY_PATHS = [
    REPO_ROOT / "SOUL.md",
    REPO_ROOT / "STYLE.md",
    REPO_ROOT / "MEMORY.md",
    REPO_ROOT / "CANON.md",
]

PROPOSED_UPDATE_PATHS = [
    WIKI_DIR / "identity" / "proposed_soul_updates.md",
    WIKI_DIR / "identity" / "proposed_style_updates.md",
    WIKI_DIR / "aesthetics" / "voice" / "proposed_voice_style_card_updates.md",
    WIKI_DIR / "aesthetics" / "visual" / "proposed_visual_style_bible_updates.md",
    WIKI_DIR / "aesthetics" / "music" / "proposed_music_style_bible_updates.md",
    WIKI_DIR / "social" / "proposed_social_strategy_updates.md",
]

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aiff", ".aif", ".ogg", ".m4a"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".tiff", ".tif", ".bmp"}
IGNORE_FILES = {"README.md", ".DS_Store", ".gitkeep"}


def check_empty_readmes():
    issues = []
    for root, dirs, files in os.walk(WIKI_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if fname == "README.md":
                fpath = Path(root) / fname
                content = fpath.read_text(encoding="utf-8").strip()
                if len(content) < 10:
                    rel = fpath.relative_to(REPO_ROOT)
                    issues.append(f"Empty README: `{rel}`")
    return issues


def check_missing_metadata():
    issues = []
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from scan_inbox import scan_inbox
        sources = scan_inbox()
    except Exception:
        return ["Could not scan inbox for metadata check"]

    existing_stubs = set()
    if STUBS_DIR.exists():
        existing_stubs = {f.stem for f in STUBS_DIR.iterdir() if f.suffix == ".md"}

    for s in sources:
        if s["source_id"] not in existing_stubs:
            issues.append(f"Missing metadata stub for: `{s['path']}`")
    return issues


def check_style_bible_empty_fields():
    issues = []
    for bible_path in STYLE_BIBLE_PATHS:
        if not bible_path.exists():
            issues.append(f"Style bible missing: `{bible_path.relative_to(REPO_ROOT)}`")
            continue
        content = bible_path.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.startswith("*") and line.strip().endswith(":"):
                field = line.strip().lstrip("* ").rstrip(":")
                rel = bible_path.relative_to(REPO_ROOT)
                issues.append(f"Empty style bible field: `{rel}` → {field}")
    return issues


def check_unreviewed_proposals():
    issues = []
    for prop_path in PROPOSED_UPDATE_PATHS:
        if not prop_path.exists():
            continue
        content = prop_path.read_text(encoding="utf-8")
        if "status: pending" in content.lower() or "Status:** pending" in content:
            rel = prop_path.relative_to(REPO_ROOT)
            issues.append(f"Unreviewed proposal: `{rel}`")
    return issues


def check_old_inbox_files():
    issues = []
    seven_days_ago = datetime.now() - timedelta(days=7)

    for root, dirs, files in os.walk(INBOX_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if fname in IGNORE_FILES:
                continue
            fpath = Path(root) / fname
            mtime = datetime.fromtimestamp(fpath.stat().st_mtime)
            if mtime < seven_days_ago:
                rel = fpath.relative_to(REPO_ROOT)
                age_days = (datetime.now() - mtime).days
                issues.append(f"Inbox file older than 7 days ({age_days}d): `{rel}`")
    return issues


def check_media_without_notes():
    issues = []
    for root, dirs, files in os.walk(INBOX_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if fname in IGNORE_FILES:
                continue
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()
            if ext in AUDIO_EXTS or ext in IMAGE_EXTS:
                from scan_inbox import source_id
                sid = source_id(fpath)
                stub_path = STUBS_DIR / f"{sid}.md"
                if stub_path.exists():
                    content = stub_path.read_text(encoding="utf-8")
                    if "_Add notes here._" in content:
                        rel = fpath.relative_to(REPO_ROOT)
                        issues.append(f"Media file without descriptive notes: `{rel}`")
    return issues


def check_broken_links():
    issues = []
    link_pattern = re.compile(r'\[\[([^\]|]+?)(?:\|[^\]]*?)?\]\]')

    for root, dirs, files in os.walk(WIKI_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = Path(root) / fname
            content = fpath.read_text(encoding="utf-8")
            for match in link_pattern.finditer(content):
                link_target = match.group(1)
                if link_target.startswith("http"):
                    continue
                target_path = (Path(root) / link_target).resolve()
                if not target_path.suffix:
                    target_path = target_path.with_suffix(".md")
                if not target_path.exists():
                    parent_dir = Path(root)
                    found = False
                    for wiki_root, _, wiki_files in os.walk(WIKI_DIR):
                        base = link_target.split("/")[-1]
                        if f"{base}.md" in wiki_files or base in wiki_files:
                            found = True
                            break
                    if not found:
                        rel = fpath.relative_to(REPO_ROOT)
                        issues.append(f"Possible broken link in `{rel}`: [[{link_target}]]")
    return issues


def check_duplicate_source_ids():
    issues = []
    if not STUBS_DIR.exists():
        return issues
    seen = {}
    for f in STUBS_DIR.iterdir():
        if f.suffix == ".md" and f.name != "README.md":
            content = f.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("source_id:"):
                    sid = line.split(":", 1)[1].strip().strip('"')
                    if sid in seen:
                        issues.append(f"Duplicate source ID `{sid}`: `{f.name}` and `{seen[sid]}`")
                    else:
                        seen[sid] = f.name
    return issues


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    all_checks = {
        "Empty README files": check_empty_readmes,
        "Missing metadata stubs": check_missing_metadata,
        "Style bible empty fields": check_style_bible_empty_fields,
        "Unreviewed proposals": check_unreviewed_proposals,
        "Inbox files older than 7 days": check_old_inbox_files,
        "Media without descriptive notes": check_media_without_notes,
        "Broken wiki links": check_broken_links,
        "Duplicate source IDs": check_duplicate_source_ids,
    }

    critical = []
    warnings = []

    for check_name, check_fn in all_checks.items():
        try:
            issues = check_fn()
        except Exception as e:
            warnings.append(f"Check failed ({check_name}): {e}")
            continue

        if check_name in ("Missing metadata stubs", "Style bible empty fields"):
            critical.extend(issues)
        else:
            warnings.extend(issues)

    total = len(critical) + len(warnings)

    lines = [
        "# HEALTH_CHECK.md",
        "",
        f"Wiki health report. Populated by `scripts/librarian/health_check.py`.",
        "",
        f"Last check: {now}",
        "",
        f"## Summary",
        "",
        f"- **Total issues:** {total}",
        f"- **Critical:** {len(critical)}",
        f"- **Warnings:** {len(warnings)}",
        "",
    ]

    lines.append("## Critical Issues")
    lines.append("")
    if critical:
        for issue in critical:
            lines.append(f"- {issue}")
    else:
        lines.append("_None._")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    if warnings:
        for issue in warnings:
            lines.append(f"- {issue}")
    else:
        lines.append("_None._")
    lines.append("")

    lines.extend([
        "## Checks Performed",
        "",
    ])
    for check_name in all_checks:
        lines.append(f"- [x] {check_name}")

    HEALTH_CHECK_PATH.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_CHECK_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[health_check] {total} issues found ({len(critical)} critical, {len(warnings)} warnings)")


if __name__ == "__main__":
    main()

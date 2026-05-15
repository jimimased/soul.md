#!/usr/bin/env python3
"""Create proposed update files for identity, style, theory, and social files."""

import os
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
STUBS_DIR = WIKI_DIR / "outputs" / "session_reports" / "metadata_stubs"
REVIEW_QUEUE_PATH = REPO_ROOT / "operations" / "librarian" / "REVIEW_QUEUE.md"

TARGET_FILES = {
    "SOUL.md": REPO_ROOT / "SOUL.md",
    "STYLE.md": REPO_ROOT / "STYLE.md",
    "MEMORY.md": REPO_ROOT / "MEMORY.md",
    "CANON.md": REPO_ROOT / "CANON.md",
    "VOICE_STYLE_CARD.md": REPO_ROOT / "aesthetic_corpus" / "voice" / "VOICE_STYLE_CARD.md",
    "VISUAL_STYLE_BIBLE.md": REPO_ROOT / "aesthetic_corpus" / "visual" / "VISUAL_STYLE_BIBLE.md",
    "MUSIC_STYLE_BIBLE.md": REPO_ROOT / "aesthetic_corpus" / "music" / "MUSIC_STYLE_BIBLE.md",
    "MEDIUM_ADAPTERS.md": REPO_ROOT / "media" / "MEDIUM_ADAPTERS.md",
    "POST_REGISTER.md": REPO_ROOT / "media" / "POST_REGISTER.md",
    "VIDEO_REGISTER.md": REPO_ROOT / "media" / "VIDEO_REGISTER.md",
}

PROPOSAL_OUTPUTS = {
    "SOUL.md": WIKI_DIR / "identity" / "proposed_soul_updates.md",
    "STYLE.md": WIKI_DIR / "identity" / "proposed_style_updates.md",
    "VOICE_STYLE_CARD.md": WIKI_DIR / "aesthetics" / "voice" / "proposed_voice_style_card_updates.md",
    "VISUAL_STYLE_BIBLE.md": WIKI_DIR / "aesthetics" / "visual" / "proposed_visual_style_bible_updates.md",
    "MUSIC_STYLE_BIBLE.md": WIKI_DIR / "aesthetics" / "music" / "proposed_music_style_bible_updates.md",
    "social_strategy": WIKI_DIR / "social" / "proposed_social_strategy_updates.md",
}

RELEVANCE_MAP = {
    "identity_relevance": ["SOUL.md", "STYLE.md"],
    "aesthetic_relevance": ["VOICE_STYLE_CARD.md", "VISUAL_STYLE_BIBLE.md", "MUSIC_STYLE_BIBLE.md"],
    "theory_relevance": [],
    "social_relevance": ["social_strategy"],
}


def load_stubs():
    stubs = []
    if not STUBS_DIR.exists():
        return stubs
    for f in sorted(STUBS_DIR.iterdir()):
        if f.suffix == ".md" and f.name != "README.md":
            content = f.read_text(encoding="utf-8")
            stub = {"path": str(f), "content": content, "filename": f.name}
            for line in content.split("\n"):
                for field in ("source_id", "original_path", "source_type", "title",
                              "ingest_lane", "privacy_level", "identity_relevance",
                              "aesthetic_relevance", "theory_relevance", "social_relevance",
                              "requires_human_review"):
                    if line.startswith(f"{field}:"):
                        val = line.split(":", 1)[1].strip().strip('"').strip("'")
                        stub[field] = val
            stubs.append(stub)
    return stubs


def stubs_relevant_to(stubs, relevance_field, threshold=("likely", "high", "confirmed")):
    return [s for s in stubs if s.get(relevance_field, "unknown") in threshold]


def update_review_queue(stubs):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    identity_stubs = stubs_relevant_to(stubs, "identity_relevance")
    aesthetic_stubs = stubs_relevant_to(stubs, "aesthetic_relevance")
    theory_stubs = stubs_relevant_to(stubs, "theory_relevance")
    social_stubs = stubs_relevant_to(stubs, "social_relevance")
    review_required = [s for s in stubs if s.get("requires_human_review") == "true"]

    lines = [
        "# REVIEW_QUEUE.md",
        "",
        f"Proposed updates waiting for human review. Populated by `scripts/librarian/propose_updates.py`.",
        "",
        f"Last update: {now}",
        "",
        "## Pending Reviews",
        "",
    ]

    proposals = []

    if identity_stubs:
        proposals.append({
            "file": "wiki/identity/proposed_soul_updates.md",
            "reason": f"{len(identity_stubs)} identity-relevant source(s)",
            "confidence": "low",
            "status": "needs analysis",
        })
        proposals.append({
            "file": "wiki/identity/proposed_style_updates.md",
            "reason": f"{len(identity_stubs)} identity-relevant source(s)",
            "confidence": "low",
            "status": "needs analysis",
        })

    if aesthetic_stubs:
        for bible in ["voice", "visual", "music"]:
            proposals.append({
                "file": f"wiki/aesthetics/{bible}/proposed_{bible}_style_{'card' if bible == 'voice' else 'bible'}_updates.md",
                "reason": f"{len(aesthetic_stubs)} aesthetic-relevant source(s)",
                "confidence": "low",
                "status": "needs analysis",
            })

    if social_stubs:
        proposals.append({
            "file": "wiki/social/proposed_social_strategy_updates.md",
            "reason": f"{len(social_stubs)} social-relevant source(s)",
            "confidence": "low",
            "status": "needs analysis",
        })

    if proposals:
        lines.append("| # | Proposal File | Reason | Confidence | Status |")
        lines.append("|---|---------------|--------|------------|--------|")
        for i, p in enumerate(proposals, 1):
            lines.append(f"| {i} | `{p['file']}` | {p['reason']} | {p['confidence']} | {p['status']} |")
    else:
        lines.append("_No proposals generated. Ingest sources with relevant tags to trigger proposals._")

    lines.append("")

    if review_required:
        lines.extend([
            "## Sources Requiring Human Review",
            "",
        ])
        for s in review_required:
            lines.append(f"- `{s.get('original_path', s['filename'])}` — {s.get('privacy_level', 'unknown')} privacy")
        lines.append("")

    REVIEW_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_QUEUE_PATH.write_text("\n".join(lines), encoding="utf-8")
    return proposals


def main():
    stubs = load_stubs()
    proposals = update_review_queue(stubs)
    print(f"[propose_updates] {len(proposals)} proposals generated from {len(stubs)} stubs")


if __name__ == "__main__":
    main()

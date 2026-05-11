#!/usr/bin/env python3
"""Create metadata stubs for each source in the ingest queue."""

import json
import os
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INBOX_DIR = REPO_ROOT / "inbox"
STUBS_DIR = REPO_ROOT / "wiki" / "outputs" / "session_reports" / "metadata_stubs"
TEMPLATE_PATH = REPO_ROOT / "templates" / "librarian" / "source_metadata.template.json"

SENSITIVE_KEYWORDS = [
    "health", "medical", "diagnosis", "treatment", "therapy",
    "financial", "investment", "portfolio", "tax", "salary",
    "indigenous", "aboriginal", "first nations", "traditional",
    "private", "confidential", "secret", "personal",
    "political", "election", "vote",
]

REVIEW_REQUIRED_TYPES = {"audio", "video", "image"}


def load_template():
    if TEMPLATE_PATH.exists():
        return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return {}


def needs_human_review(source):
    if source.get("privacy_default") in ("private", "personal"):
        return True
    if source.get("type") in REVIEW_REQUIRED_TYPES:
        return True
    filename_lower = source.get("filename", "").lower()
    if any(kw in filename_lower for kw in SENSITIVE_KEYWORDS):
        return True
    return False


def infer_relevance(source):
    lane = source.get("lane", "")
    relevance = {
        "identity_relevance": "unknown",
        "aesthetic_relevance": "unknown",
        "theory_relevance": "unknown",
        "social_relevance": "unknown",
    }
    if lane == "personal_writing":
        relevance["identity_relevance"] = "likely"
    elif lane == "theory":
        relevance["theory_relevance"] = "likely"
    elif lane == "visual":
        relevance["aesthetic_relevance"] = "likely"
    elif lane == "music":
        relevance["aesthetic_relevance"] = "likely"
    elif lane == "voice":
        relevance["identity_relevance"] = "likely"
        relevance["aesthetic_relevance"] = "likely"
    elif lane == "links":
        relevance["theory_relevance"] = "possible"
    elif lane == "playlists":
        relevance["aesthetic_relevance"] = "likely"
    return relevance


def destination_for_lane(lane):
    destinations = {
        "personal_writing": "wiki/identity/",
        "theory": "wiki/theory/source_summaries/",
        "visual": "wiki/aesthetics/visual/",
        "music": "wiki/aesthetics/music/",
        "voice": "wiki/aesthetics/voice/",
        "links": "wiki/theory/source_summaries/",
        "playlists": "wiki/aesthetics/music/",
        "web_clips": "wiki/theory/source_summaries/",
    }
    return destinations.get(lane, "wiki/outputs/")


def create_stub(source, template):
    stub = dict(template)
    stub["source_id"] = source["source_id"]
    stub["original_path"] = source["path"]
    stub["source_type"] = source["type"]
    stub["title"] = Path(source["filename"]).stem
    stub["date_added"] = datetime.now().strftime("%Y-%m-%d")
    stub["privacy_level"] = source["privacy_default"]
    stub["ingest_lane"] = source["lane"]
    stub["proposed_destination"] = destination_for_lane(source["lane"])
    stub["summary_status"] = "pending"
    stub["requires_human_review"] = needs_human_review(source)

    relevance = infer_relevance(source)
    stub.update(relevance)

    return stub


def write_stub_markdown(stub, stubs_dir):
    sid = stub["source_id"]
    stub_path = stubs_dir / f"{sid}.md"

    if stub_path.exists():
        return False

    lines = [
        "---",
        f'source_id: "{sid}"',
        f'original_path: "{stub["original_path"]}"',
        f'source_type: "{stub["source_type"]}"',
        f'title: "{stub["title"]}"',
        f'creator_or_author: ""',
        f'date_added: "{stub["date_added"]}"',
        f'date_created_if_known: ""',
        f'rights_status: ""',
        f'privacy_level: "{stub["privacy_level"]}"',
        f'ingest_lane: "{stub["ingest_lane"]}"',
        f'proposed_destination: "{stub["proposed_destination"]}"',
        f'summary_status: "{stub["summary_status"]}"',
        f'identity_relevance: "{stub["identity_relevance"]}"',
        f'aesthetic_relevance: "{stub["aesthetic_relevance"]}"',
        f'theory_relevance: "{stub["theory_relevance"]}"',
        f'social_relevance: "{stub["social_relevance"]}"',
        f'requires_human_review: {str(stub["requires_human_review"]).lower()}',
        f'notes: ""',
        "---",
        "",
        f'# Metadata: {stub["title"]}',
        "",
        f'**Source:** `{stub["original_path"]}`',
        f'**Type:** {stub["source_type"]}',
        f'**Lane:** {stub["ingest_lane"]}',
        f'**Privacy:** {stub["privacy_level"]}',
        f'**Review required:** {"yes" if stub["requires_human_review"] else "no"}',
        "",
        "## Notes",
        "",
        "_Add notes here._",
    ]

    stub_path.write_text("\n".join(lines), encoding="utf-8")
    return True


def main():
    try:
        from scan_inbox import scan_inbox
    except ImportError:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from scan_inbox import scan_inbox

    sources = scan_inbox()
    template = load_template()
    STUBS_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    for source in sources:
        stub = create_stub(source, template)
        if write_stub_markdown(stub, STUBS_DIR):
            created += 1
        else:
            skipped += 1

    print(f"[create_metadata_stubs] Created {created} stubs, skipped {skipped} existing")
    return created


if __name__ == "__main__":
    main()

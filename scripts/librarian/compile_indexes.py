#!/usr/bin/env python3
"""Compile markdown indexes for the wiki."""

import os
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
STUBS_DIR = WIKI_DIR / "outputs" / "session_reports" / "metadata_stubs"
CONCEPT_CARDS_DIR = WIKI_DIR / "theory" / "concept_cards"
SOURCE_SUMMARIES_DIR = WIKI_DIR / "theory" / "source_summaries"
ALGO_DEPS_DIR = WIKI_DIR / "theory" / "algorithm_dependencies"


def count_md_files(directory):
    if not directory.exists():
        return 0
    return sum(1 for f in directory.iterdir() if f.suffix == ".md" and f.name != "README.md")


def list_md_files(directory):
    if not directory.exists():
        return []
    files = []
    for f in sorted(directory.iterdir()):
        if f.suffix == ".md" and f.name != "README.md":
            files.append(f)
    return files


def extract_frontmatter_field(path, field):
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None
    in_frontmatter = False
    for line in content.split("\n"):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter and line.startswith(f"{field}:"):
            val = line.split(":", 1)[1].strip().strip('"').strip("'")
            return val
    return None


def update_wiki_index():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    stubs_count = count_md_files(STUBS_DIR)
    concept_count = count_md_files(CONCEPT_CARDS_DIR)
    summary_count = count_md_files(SOURCE_SUMMARIES_DIR)

    concept_cards = list_md_files(CONCEPT_CARDS_DIR)
    source_summaries = list_md_files(SOURCE_SUMMARIES_DIR)

    lines = [
        "# Wiki Index",
        "",
        f"Master index for the Rupture System knowledge base. Updated by `scripts/librarian/compile_indexes.py`.",
        "",
        f"Last compiled: {now}",
        "",
        "## Identity",
        "",
        "- [[YUWAS_MAWAY_IDENTITY_INDEX]] — identity observations and proposed updates",
        "- [[identity_observations]] — raw identity notes",
        "- [[proposed_soul_updates]] — proposed changes to SOUL.md",
        "- [[proposed_style_updates]] — proposed changes to STYLE.md",
        "",
        "## Aesthetics",
        "",
        "- [[AESTHETIC_INDEX]] — aesthetic observations across voice, visual, music",
        "- Voice: [[voice_observations]] | [[proposed_voice_style_card_updates]]",
        "- Visual: [[visual_observations]] | [[proposed_visual_style_bible_updates]]",
        "- Music: [[music_observations]] | [[proposed_music_style_bible_updates]]",
        "",
        "## Theory",
        "",
        "- [[THEORY_INDEX]] — concept cards, source summaries, algorithm dependencies",
        "",
    ]

    if concept_cards:
        lines.append("### Concept Cards")
        lines.append("")
        for card in concept_cards:
            title = extract_frontmatter_field(card, "concept") or card.stem
            lines.append(f"- [[{card.stem}|{title}]]")
        lines.append("")

    if source_summaries:
        lines.append("### Source Summaries")
        lines.append("")
        for summary in source_summaries:
            title = extract_frontmatter_field(summary, "title") or summary.stem
            lines.append(f"- [[{summary.stem}|{title}]]")
        lines.append("")

    lines.extend([
        "## Social",
        "",
        "- [[SOCIAL_IDENTITY_INDEX]] — social media identity preparation",
        "- [[platform_register_observations]] — platform/register mapping notes",
        "- [[proposed_social_strategy_updates]] — proposed social media strategy",
        "",
        "## Outputs",
        "",
        "- Session reports: `wiki/outputs/session_reports/`",
        "- Generated drafts: `wiki/outputs/generated_drafts/`",
        "- Filed outputs: `wiki/outputs/filed_outputs/`",
        "",
        "## Source Statistics",
        "",
        f"- Metadata stubs: {stubs_count}",
        f"- Concept cards: {concept_count}",
        f"- Source summaries: {summary_count}",
    ])

    index_path = WIKI_DIR / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")


def update_theory_index():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    concept_cards = list_md_files(CONCEPT_CARDS_DIR)
    source_summaries = list_md_files(SOURCE_SUMMARIES_DIR)
    algo_deps = list_md_files(ALGO_DEPS_DIR)

    lines = [
        "---",
        "type: index",
        "subject: theory",
        f"status: {'populated' if concept_cards or source_summaries else 'initial'}",
        "created: 2026-05-11",
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Theory Index",
        "",
        f"Last compiled: {now}",
        "",
        "## Concept Cards",
        "",
    ]

    if concept_cards:
        for card in concept_cards:
            title = extract_frontmatter_field(card, "concept") or card.stem
            lines.append(f"- [[concept_cards/{card.stem}|{title}]]")
    else:
        lines.append("_No concept cards yet. Ingest theory sources to populate._")

    lines.extend(["", "## Source Summaries", ""])

    if source_summaries:
        for summary in source_summaries:
            title = extract_frontmatter_field(summary, "title") or summary.stem
            lines.append(f"- [[source_summaries/{summary.stem}|{title}]]")
    else:
        lines.append("_No source summaries yet._")

    lines.extend(["", "## Algorithm Dependencies", ""])

    if algo_deps:
        for dep in algo_deps:
            lines.append(f"- [[algorithm_dependencies/{dep.stem}]]")
    else:
        lines.append("_No algorithm dependency maps yet._")

    lines.extend([
        "",
        "## Statistics",
        "",
        f"- Concept cards: {len(concept_cards)}",
        f"- Source summaries: {len(source_summaries)}",
        f"- Algorithm dependency maps: {len(algo_deps)}",
    ])

    theory_index_path = WIKI_DIR / "theory" / "THEORY_INDEX.md"
    theory_index_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    update_wiki_index()
    update_theory_index()
    print("[compile_indexes] Wiki indexes updated")


if __name__ == "__main__":
    main()

# Manual Ingest Guide

Where to place different types of source material for the librarian to process.

## Personal writing

**Location:** `inbox/personal_writing/`
**Formats:** .md, .txt, .rtf, .docx
**Examples:** journal entries, autobiographical text, essays, reflections, letters
**Privacy:** Defaults to `personal`. Requires human review before influencing public identity.

## Theory PDFs and papers

**Location:** `inbox/theory/`
**Formats:** .pdf, .md, .txt
**Examples:** academic papers, book chapters, theory excerpts
**Privacy:** Defaults to `public`.

## Theory links and web articles

**Location:** `inbox/links/`
**Format:** One .md file per link, using the link entry template:

```markdown
---
url: https://example.com/article
title: Article Title
author: Author Name
date_found: 2026-05-11
tags: [theory, platform-colonialism]
notes: Why this matters
---
```

**Privacy:** Defaults to `public`.

## Web clips and saved articles

**Location:** `inbox/web_clips/`
**Formats:** .md, .html, .txt, .pdf
**Examples:** saved web pages, article archives, clippings
**Privacy:** Defaults to `public`.

## Images and visual references

**Location:** `inbox/visual/`
**Formats:** .png, .jpg, .jpeg, .gif, .svg, .webp, .tiff
**Examples:** mood boards, reference images, screenshots, design files
**Privacy:** Defaults to `personal`. Images of real people require human review.

## Music files

**Location:** `inbox/music/`
**Formats:** .mp3, .wav, .flac, .aiff, .ogg, .m4a, .mid, .midi
**Examples:** tracks, stems, mixes, samples, generated outputs
**Privacy:** Defaults to `personal`. Collaborative material needs attribution.

## Playlists

**Location:** `inbox/playlists/`
**Format:** .md files listing tracks/URLs:

```markdown
---
title: Footwork References
platform: spotify
date_created: 2026-05-11
mood: kinetic, fractured, polyrhythmic
notes: Reference material for rhythmic identity
---

1. DJ Rashad - Let U No [URL]
2. RP Boo - Legacy [URL]
```

**Privacy:** Defaults to `public`.

## Voice files

**Location:** `inbox/voice/`
**Formats:** .mp3, .wav, .flac, .aiff, .ogg, .m4a
**Examples:** voice recordings, vocal samples, narration drafts
**Privacy:** Defaults to `private`. Requires human review before any training or publication.

## Generated outputs (for filing back)

**Location:** `wiki/outputs/generated_drafts/` (if pending review) or `wiki/outputs/filed_outputs/` (if approved)
**Note:** Don't put generated outputs in inbox — they go directly into the wiki output layer.

## Public research

**Location:** `data/public_research/` (existing directory)
**Note:** Already in the repo structure. The librarian can reference but won't move files.

## Private material that should NOT be ingested

**Location:** `data/do_not_ingest_private/`
**Rule:** The librarian will NEVER scan this directory. Place anything here that should be excluded from all processing.

## After adding sources

Run the librarian:

```bash
./scripts/librarian/run_librarian.sh
```

Then review:
- `operations/librarian/INGEST_QUEUE.md` — what was found
- `operations/librarian/SOURCE_MANIFEST.md` — full inventory
- `operations/librarian/REVIEW_QUEUE.md` — proposed changes
- `operations/librarian/HEALTH_CHECK.md` — system health

# inbox/

Drop raw sources here for the librarian to scan. Subdirectories organize by type.

## Subdirectories

- `personal_writing/` — autobiographical text, essays, journal entries, reflections
- `theory/` — PDFs, academic papers, book chapters, theory links
- `visual/` — images, visual references, screenshots, design files
- `music/` — audio files, stems, mixes, tracks
- `voice/` — voice recordings, vocal samples, narration drafts
- `links/` — URLs as .md files (one link per file with notes)
- `playlists/` — playlist files or .md files listing tracks/URLs
- `web_clips/` — saved web articles, clippings, archived pages

## How it works

1. Drop files into the appropriate subdirectory.
2. Run `./scripts/librarian/run_librarian.sh` from the repo root.
3. The librarian scans, creates metadata stubs, and proposes updates.
4. Review proposals in `wiki/` and `operations/librarian/REVIEW_QUEUE.md`.
5. Approve or reject.

## Rules

- Files are never moved or deleted by the librarian.
- Private material goes in `data/do_not_ingest_private/`, not here.
- If unsure about privacy level, the librarian will flag it for human review.

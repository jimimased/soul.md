# LIBRARIAN_PROTOCOL.md

The Obsidian Librarian is a controlled, manual-ingest system for maintaining the Rupture System's knowledge base.

## Principles

1. **Human in the loop.** The librarian proposes; the human decides.
2. **No automatic mutation.** Identity files (SOUL.md, STYLE.md, MEMORY.md, CANON.md) and style bibles are never written directly. All changes go through proposed update files and the review queue.
3. **Provenance first.** Every claim must be traceable to a source.
4. **Privacy by default.** Personal, voice, and culturally sensitive material defaults to private and requires human review.
5. **Compounding knowledge.** Every session's outputs are filed back into the wiki so the system accumulates over time.

## Workflow

1. User drops sources into `inbox/` subdirectories.
2. User runs `./scripts/librarian/run_librarian.sh`.
3. The librarian:
   - Scans inbox for new sources
   - Creates metadata stubs for unprocessed sources
   - Builds/updates the source manifest
   - Compiles wiki indexes
   - Creates proposed update files for identity, style, theory, and social files
   - Runs a health check
4. User reviews proposals in `wiki/` and `operations/librarian/REVIEW_QUEUE.md`.
5. User approves or rejects proposals.
6. Approved material is manually copied into target files or via future approval script.
7. Approvals and rejections are logged in `APPROVAL_LEDGER.md`.

## What the librarian does NOT do

- Move or delete inbox files
- Directly edit SOUL.md, STYLE.md, MEMORY.md, CANON.md, or style bibles
- Access `data/do_not_ingest_private/`
- Make API calls or require network access
- Train models
- Publish anything
- Create social media accounts
- Fabricate metadata or invent sources

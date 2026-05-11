# Obsidian Librarian Workflow

This repo uses an Obsidian-compatible markdown librarian system adapted from the Karpathy-style markdown wiki model to the Rupture System's identity substrate.

## How it works

1. **You manually drop sources** into `inbox/` subdirectories (text, PDFs, images, audio, links, playlists).
2. **You run the librarian** with `./scripts/librarian/run_librarian.sh`.
3. **The librarian scans** inbox, creates metadata stubs, builds the source manifest, compiles wiki indexes, proposes updates to identity/style/theory/social files, and runs a health check.
4. **You review proposals** in `wiki/` and `operations/librarian/REVIEW_QUEUE.md`.
5. **You approve or reject.** Approved changes are manually applied to target files. Rejections are logged.
6. **Outputs compound.** Every session's outputs are filed back into the wiki, so the knowledge base grows over time.

## What the librarian does NOT do

- Automatically publish, train, or mutate identity files
- Access `data/do_not_ingest_private/`
- Require network access, API keys, or external dependencies
- Create social media accounts or post content
- Fabricate metadata or invent sources

## Layer model

```
inbox/                    ← raw source layer (you add files here)
  ↓
wiki/                     ← compiled wiki layer (librarian writes here)
  ├── identity/           ← identity observations + proposed updates
  ├── aesthetics/         ← voice/visual/music observations + proposals
  ├── theory/             ← concept cards + source summaries
  ├── social/             ← social media preparation
  └── outputs/            ← session reports + generated drafts
  ↓
operations/librarian/     ← operational layer (queues, ledgers, health)
  ↓
SOUL.md, STYLE.md, etc.  ← identity layer (protected, human-approved only)
```

## Obsidian compatibility

All wiki files use:
- YAML frontmatter for metadata
- Relative links for file references
- `[[wiki links]]` for cross-references
- Backlinks sections for discoverability

Open the repo root in Obsidian to browse the wiki with full graph view and backlink support.

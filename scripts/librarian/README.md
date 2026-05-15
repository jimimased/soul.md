# scripts/librarian/

Python scripts for the Obsidian Librarian system. All scripts use Python standard library only — no external dependencies.

## Scripts

1. **scan_inbox.py** — Scan `inbox/` folders, detect file types, write `INGEST_QUEUE.md`
2. **create_metadata_stubs.py** — Create YAML-frontmatter metadata stubs for unprocessed sources
3. **build_source_manifest.py** — Compile `SOURCE_MANIFEST.md` from inbox and wiki state
4. **compile_indexes.py** — Update wiki index files with Obsidian-style links
5. **health_check.py** — Detect gaps, stale files, empty fields, broken links, privacy issues
6. **propose_updates.py** — Create structured proposals for identity/style/theory/social updates
7. **run_librarian.sh** — Orchestrator that runs all scripts in order

## Usage

```bash
chmod +x scripts/librarian/run_librarian.sh
./scripts/librarian/run_librarian.sh
```

## Requirements

- Python 3.6+
- No pip packages needed

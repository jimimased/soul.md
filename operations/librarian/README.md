# operations/librarian/

Operational ledgers for the Obsidian Librarian system.

These files are maintained by the librarian scripts and track the state of source ingestion, review queues, approvals, provenance, and system health.

## Files

- `LIBRARIAN_PROTOCOL.md` — how the librarian works
- `INGEST_QUEUE.md` — sources waiting for processing (populated by `scan_inbox.py`)
- `REVIEW_QUEUE.md` — proposed updates waiting for human review (populated by `propose_updates.py`)
- `APPROVAL_LEDGER.md` — log of approved and rejected proposals
- `PROVENANCE_LEDGER.md` — source tracing for all claims
- `HEALTH_CHECK.md` — system health report (populated by `health_check.py`)
- `SOURCE_MANIFEST.md` — complete source inventory (populated by `build_source_manifest.py`)
- `BACKLINK_AUDIT.md` — link integrity check
- `IDENTITY_CHANGELOG.md` — changes to identity files
- `STYLE_BIBLE_CHANGELOG.md` — changes to style bible files
- `SOCIAL_DEPLOYMENT_READINESS.md` — pre-launch checklist for social media

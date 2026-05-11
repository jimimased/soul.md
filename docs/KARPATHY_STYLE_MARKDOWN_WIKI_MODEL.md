# Karpathy-Style Markdown Wiki Model

This system adapts Andrej Karpathy's Obsidian-based knowledge management workflow to the Rupture System's multi-layered identity substrate.

## Layer Architecture

### 1. Raw Source Layer (`inbox/`)
- Manually added by the human
- Unprocessed files: PDFs, text, images, audio, links, playlists
- The librarian reads but never modifies these files

### 2. Compiled Wiki Layer (`wiki/`)
- Summaries, concept cards, observations, and proposed updates
- Written and maintained by the librarian
- Obsidian-compatible with YAML frontmatter and wiki links
- Organized by domain: identity, aesthetics, theory, social

### 3. Index Layer (`wiki/INDEX.md` + domain indexes)
- Master index and per-domain indexes
- Compiled automatically by the librarian
- Obsidian-style internal links for graph view navigation
- Source statistics and gap tracking

### 4. Output Layer (`wiki/outputs/`)
- Session reports from each librarian run
- Generated drafts (content, bios, posts) awaiting review
- Filed outputs (approved and published/archived)

### 5. Health Check Layer (`operations/librarian/HEALTH_CHECK.md`)
- Detects gaps, stale files, inconsistent claims
- Missing metadata, broken links, orphan cards
- Empty style bible fields
- Unreviewed proposals
- Privacy status issues

### 6. Obsidian Frontend Layer
- Open the repo root in Obsidian
- Browse the wiki with graph view, backlinks, and search
- YAML frontmatter renders as properties in Obsidian
- Wiki links create navigable connections

## Future optional extensions

### Search tool
A local search tool (e.g., ripgrep-based) that queries the wiki by concept, source, or relevance tag. Not implemented yet — the index files and Obsidian search serve this role for now.

### Model fine-tuning
The compiled wiki could serve as training data for fine-tuning a model on the Rupture System's knowledge and voice. This is explicitly out of scope for now. The librarian only produces markdown — it does not train models.

### Automated approval
A future script could apply approved patches automatically. For now, approval is manual to protect identity integrity.

## Differences from Karpathy's model

Karpathy's system is a general knowledge wiki. This system adds:
- **Identity protection:** Core identity files are never written directly
- **Privacy layers:** Source material has privacy levels; sensitive content is gated
- **Multi-domain structure:** Identity, aesthetics, theory, and social are separate domains
- **Provenance tracking:** Every claim traces to a source with confidence levels
- **Mask-aware outputs:** Proposals can note which argumentative mask (per MASKS.md) is relevant
- **Ethics integration:** The librarian respects ETHICS.md and CONSTITUTION.md boundaries

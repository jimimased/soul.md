# Approval Workflow

How proposed updates move from draft to approved (or rejected).

## Process

1. The librarian writes proposed updates into `wiki/` subdirectories:
   - `wiki/identity/proposed_soul_updates.md`
   - `wiki/identity/proposed_style_updates.md`
   - `wiki/aesthetics/voice/proposed_voice_style_card_updates.md`
   - `wiki/aesthetics/visual/proposed_visual_style_bible_updates.md`
   - `wiki/aesthetics/music/proposed_music_style_bible_updates.md`
   - `wiki/social/proposed_social_strategy_updates.md`

2. The librarian lists all pending proposals in `operations/librarian/REVIEW_QUEUE.md`.

3. **Human reviews each proposal.** Each proposal includes:
   - Proposed change (exact text)
   - Source evidence
   - Confidence level
   - Risk assessment
   - Affected file
   - Rationale

4. **Human decides:** approve or reject.

5. **If approved:**
   - Manually copy the proposed text into the target file
   - Update the proposal status to `approved`
   - Log the approval in `operations/librarian/APPROVAL_LEDGER.md`
   - Log the change in `operations/librarian/IDENTITY_CHANGELOG.md` or `STYLE_BIBLE_CHANGELOG.md`

6. **If rejected:**
   - Update the proposal status to `rejected`
   - Log the rejection with a reason in `operations/librarian/APPROVAL_LEDGER.md`
   - The proposal remains in the wiki for reference

## Protected files

These files are NEVER written directly by the librarian:
- `SOUL.md`
- `STYLE.md`
- `MEMORY.md`
- `CANON.md`
- `aesthetic_corpus/voice/VOICE_STYLE_CARD.md`
- `aesthetic_corpus/visual/VISUAL_STYLE_BIBLE.md`
- `aesthetic_corpus/music/MUSIC_STYLE_BIBLE.md`

All changes go through the proposal → review → approval pipeline.

## Special review requirements

The following types of changes always require human review, regardless of confidence level:
- Identity claims (who Yuwas Maway is)
- Public biography statements
- Voice identity parameters
- Cultural identity or Indigenous references
- Health or medical information
- Financial or investment information
- Political positions
- Any content that would be published publicly

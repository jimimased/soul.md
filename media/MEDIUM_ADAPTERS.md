# MEDIUM_ADAPTERS.md

The agent expresses through different registers. Each register is a distinct medium with its own voice rules, ideal masks, and output constraints.

## Register Index

| Register | File | Primary Platform | Voice Density |
|---|---|---|---|
| Essay | `ESSAY_REGISTER.md` | Long-form / Substack | Full accrete-then-rupture |
| Post | `POST_REGISTER.md` | Instagram / Threads | Compressed witness |
| Video | `VIDEO_REGISTER.md` | YouTube | Temporal continuity |
| Music | `MUSIC_REGISTER.md` | SoundCloud / Bandcamp | Sonic motifs |
| Game | `GAME_REGISTER.md` | Interactive | Cultural mechanics |
| Platform Spec | — | Internal / Pacific Commons | Technical architecture |
| Grant Brief | — | Institutional | Diplomatic legibility |
| Spoken Voice | — | Podcast / Live | Oral storytelling register |
| Visual | — | ComfyUI pipeline | Image grammar |
| Theory-to-Output | — | Internal | Concept → applied logic |

## Register Selection Logic

1. **What is the output?** Determines primary register.
2. **Who encounters it?** Determines voice compression level.
3. **Which masks should argue?** Each register has ideal masks.
4. **Where does it land?** Platform determines format constraints.

## Cross-Register Rules

- A post can be a compressed essay. A video can contain a post-density caption.
- Cross-posting from Instagram to Threads: expand the caption. The Threads voice is longer, more discursive.
- Cross-posting from Threads to Instagram: compress to 1–3 lines. The image carries the weight.
- Never cross-post without register adaptation.

## Voice Density Scale

| Level | Register | Lines | Pattern |
|---|---|---|---|
| Manifesto | Post (compressed) | 1 line | Statement |
| Fragment | Post | 1–3 lines | Observe, turn |
| Compressed essay | Threads text post | 3–8 lines | Accrete, accrete, rupture |
| Full essay | Essay register | 500–5000 words | Full scene-building |
| Process note | Stories / YouTube | 1–2 lines | Technical fragment |

## Platform → Register Mapping

| Platform | Primary Register | Secondary Register |
|---|---|---|
| Instagram feed | Post (visual) | Process |
| Instagram Stories | Process | Post |
| Threads | Post (text) | Compressed essay |
| YouTube | Video | Essay (spoken) |
| SoundCloud | Music | — |
| Bandcamp | Music | — |

## Auto-Poster Pipeline

The auto-poster system (`scripts/auto_poster/`) generates captions by:
1. Scanning the image corpus (`scan_images.py`)
2. Classifying by folder taxonomy (ART22 outputs, SUBJECT/*, FACE, VIDEO)
3. Generating voice-appropriate captions per POST_REGISTER rules (`generate_captions.py`)
4. Writing to a review queue (`POST_QUEUE.md`)
5. Human review → approve/reject/edit
6. Publishing approved posts via platform APIs or manual posting

Two caption modes:
- **Template mode:** Pattern-based captions from image metadata (no API key needed)
- **API mode:** Claude vision generates captions from the actual image + VOICE_STYLE_CARD context

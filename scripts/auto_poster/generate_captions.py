#!/usr/bin/env python3
"""
Generate voice-appropriate captions for images in the manifest.

Uses the VOICE_STYLE_CARD.md voice architecture and CANON.md principles
to produce captions in the POST_REGISTER format. Captions are generated
via Claude API (Anthropic) with the image and voice context as input.

Caption rules (from VOICE_STYLE_CARD + POST_REGISTER + CANON):
  - Compressed phrase, memorable line (1-3 lines max)
  - POST_REGISTER voice: accrete-then-rupture in miniature
  - No hashtags in caption body
  - No startup language, no rage bait
  - No explaining the image — let the image carry the weight
  - Bilingual (Chinese/English) permitted
  - Lowercase by default except proper nouns
  - Fragment, not explanation
  - The Slow Clock: meaning accumulates, no urgency

Output: operations/POST_QUEUE.md + operations/post_queue.json
"""

import os
import sys
import json
import base64
import subprocess
from datetime import datetime
from pathlib import Path

VOICE_SYSTEM_PROMPT = """You are the caption voice for Yuwas Maway (@yuwasmaway), an artist, researcher, and musician working between Australia, the UK, and Taiwan.

## Voice Rules (from VOICE_STYLE_CARD.md)

Your voice is:
- Direct — states before it argues
- The accrete-then-rupture pattern in miniature: one or two lines of scene/observation, then a single blunt sentence that reframes
- Bilingual: Chinese for intimacy and witness, English for theory and systems. Code-switching is natural, not performed
- Lowercase by default except proper nouns
- Material specificity over abstraction: name the place, the colour, the texture
- Never explains the image — the image carries the weight
- Dark humour and grief can coexist with tenderness
- The witness position: "I was there. I noticed this."
- Anti-generic: every claim traces to a specific thing

## Caption Format Rules (from POST_REGISTER)

- 1 to 3 lines maximum
- No hashtags
- No "first post" energy, no announcements
- No startup language ("disrupting", "empowering", "content creator")
- No rescue narratives, no pity, no voyeurism
- Fragment, not explanation
- Can be a single word, a phrase, a line of Chinese, or a compressed observation

## Canon Principles (from CANON.md)

- The Slow Clock: meaning accumulates over months, not days
- The agent is a synthetic cultural medium, not a chatbot
- Structural analysis + personal empathy, never exploitation
- The algorithm is the sediment of successful curation

## Image Type Contexts

For face grids / halftone art: "face grid [number]. [one-word or short observation]." — the face is a dataset, not a portrait
For wall textures / street art: "[location], [year]. [one compressed observation about accumulation or erasure]."
For silhouettes / void pieces: minimal — 2-4 words. signal / void / signal rhythm.
For documentary photography: witness position — what was seen, where, when. one turn at the end.
For processed/AI art: the process is the subject. name the filter, the grid, the colour treatment.

## Examples of Good Captions

- "face grid 058."
- "shoreditch, 2021. the wall doesn't forget. it just gets painted over."
- "signal / void / signal"
- "先是一個人。"
- "the algorithm is the sediment."
- "face grid 054. the face is a dataset."
- "twenty filters. twenty hypotheses about who this person is."

## Examples of Bad Captions (NEVER write these)

- "Check out my latest AI art! 🎨"
- "This piece explores the intersection of identity and technology"
- "New work dropping soon! Stay tuned"
- "The beauty of imperfection ✨"
- Any caption with emojis
- Any caption that explains what the viewer can already see"""


def read_voice_files(repo_root):
    """Read the actual voice and canon files for full context."""
    voice_card = ''
    canon = ''
    visual_bible = ''

    voice_path = os.path.join(repo_root, 'aesthetic_corpus', 'voice', 'VOICE_STYLE_CARD.md')
    if os.path.exists(voice_path):
        with open(voice_path) as f:
            voice_card = f.read()

    canon_path = os.path.join(repo_root, 'CANON.md')
    if os.path.exists(canon_path):
        with open(canon_path) as f:
            canon = f.read()

    visual_path = os.path.join(repo_root, 'aesthetic_corpus', 'visual', 'VISUAL_STYLE_BIBLE.md')
    if os.path.exists(visual_path):
        with open(visual_path) as f:
            visual_bible = f.read()

    return voice_card, canon, visual_bible


def encode_image(filepath):
    """Base64-encode an image for the API."""
    ext = os.path.splitext(filepath)[1].lower()
    media_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.avif': 'image/avif',
    }
    media_type = media_types.get(ext, 'image/jpeg')

    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')

    return media_type, data


def generate_caption_via_claude(image_path, image_meta, system_prompt):
    """
    Call Claude API via the `claude` CLI or Anthropic API to generate a caption.
    Falls back to a template-based caption if API is unavailable.
    """
    tags_str = ', '.join(image_meta.get('tags', []))
    register = image_meta.get('register', 'unknown')
    post_type = image_meta.get('post_type', 'unknown')

    user_prompt = f"""Generate a caption for this image.

Image metadata:
- Register: {register}
- Post type: {post_type}
- Tags: {tags_str}
- Filename: {image_meta.get('filename', 'unknown')}

Write ONLY the caption text. Nothing else. No quotes around it. No explanation.
1-3 lines maximum. Follow the voice rules exactly."""

    try:
        media_type, image_data = encode_image(image_path)

        api_payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 150,
            "system": system_prompt,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        }
                    },
                    {
                        "type": "text",
                        "text": user_prompt,
                    }
                ]
            }]
        }

        payload_json = json.dumps(api_payload)
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST',
             'https://api.anthropic.com/v1/messages',
             '-H', 'Content-Type: application/json',
             '-H', f'x-api-key: {os.environ.get("ANTHROPIC_API_KEY", "")}',
             '-H', 'anthropic-version: 2023-06-01',
             '-d', payload_json],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'content' in response and len(response['content']) > 0:
                return response['content'][0].get('text', '').strip(), 'claude_api'

    except Exception as e:
        print(f'  API call failed: {e}', file=sys.stderr)

    return generate_template_caption(image_meta), 'template'


def generate_template_caption(meta):
    """Fallback: generate a template caption based on metadata when API is unavailable."""
    register = meta.get('register', '')
    tags = meta.get('tags', [])
    fname = meta.get('filename', '')

    if register == 'processed_art':
        if 'comfyui_output' in tags:
            num = ''.join(c for c in fname if c.isdigit())[:5]
            if 'face_grid' in tags or 'grid' in fname.lower():
                return f'face grid {num}.'
            if 'silhouette' in tags:
                return 'signal / void / signal'
            if 'inverted' in tags:
                return f'inversion {num}. the negative holds the face.'
            if 'mirror' in tags:
                return f'mirror {num}. the reflection is the dataset.'
            return f'process {num}.'
        if 'hyperrealism' in tags:
            return 'the render doesn\'t care about your comfort.'
        return '[CAPTION NEEDED — processed art, review image]'

    if register == 'documentary':
        if 'street_art' in tags or 'wall_texture' in tags:
            return 'the wall accumulates. the wall doesn\'t forget.'
        if 'taiwan' in tags:
            return '台北。the night market doesn\'t close.'
        if 'nauru' in tags:
            return '[ETHICAL REVIEW REQUIRED — Nauru documentary]'
        if 'portrait' in tags or 'self' in tags:
            return '[CAPTION NEEDED — portrait, review image]'
        if 'nature' in tags or 'plantation' in tags:
            return 'the trees remember what the maps erased.'
        return '[CAPTION NEEDED — documentary, review image]'

    if register == 'face_reference':
        return '[NOT FOR POSTING — face reference material]'

    if register == 'video':
        return '[DEFERRED — video register]'

    return '[CAPTION NEEDED — unclassified, review image]'


def generate_alt_text_template(meta):
    """Generate alt text based on image metadata."""
    register = meta.get('register', '')
    tags = meta.get('tags', [])

    if register == 'processed_art':
        if 'face_grid' in tags:
            return 'Grid of processed portrait fragments in halftone with colour variations on dark background.'
        if 'silhouette' in tags:
            return 'Dark silhouette figure against textured black background with halftone artifacts.'
        return 'Processed digital artwork with halftone texture and colour treatment.'

    if register == 'documentary':
        if 'street_art' in tags or 'wall_texture' in tags:
            return 'Layered street art, graffiti tags, and torn posters on urban wall surface.'
        if 'taiwan' in tags:
            return 'Street scene from Taiwan with urban texture and signage.'
        return 'Documentary photograph.'

    return 'Image from the Rupture System visual corpus.'


def process_manifest(manifest_path, base_image_dir, repo_root, use_api=False, limit=None):
    """Process the image manifest and generate captions."""
    with open(manifest_path) as f:
        images = json.load(f)

    if limit:
        images = images[:limit]

    system_prompt = VOICE_SYSTEM_PROMPT
    queue = []

    for i, meta in enumerate(images):
        rel_path = meta.get('relative_path', '')
        image_path = os.path.join(base_image_dir, rel_path)

        if not os.path.exists(image_path):
            print(f'  [{i+1}/{len(images)}] SKIP (missing): {rel_path}')
            continue

        if meta.get('register') == 'video':
            continue
        if meta.get('register') == 'face_reference':
            continue

        print(f'  [{i+1}/{len(images)}] Processing: {rel_path[:60]}...')

        if use_api and os.environ.get('ANTHROPIC_API_KEY'):
            caption, source = generate_caption_via_claude(image_path, meta, system_prompt)
        else:
            caption, source = generate_template_caption(meta), 'template'

        alt_text = generate_alt_text_template(meta)

        platform = meta.get('platform', 'review_required')
        if platform == 'instagram_primary':
            aspect = '4:5'
        elif platform == 'instagram_secondary':
            aspect = '4:5 or 1:1'
        else:
            aspect = 'native'

        entry = {
            'id': f'post_{i+1:04d}',
            'image_path': rel_path,
            'filename': meta.get('filename', ''),
            'register': meta.get('register', ''),
            'post_type': meta.get('post_type', ''),
            'tags': meta.get('tags', []),
            'platform': platform,
            'aspect_ratio': aspect,
            'caption': caption,
            'alt_text': alt_text,
            'caption_source': source,
            'status': 'pending_review',
            'generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        }

        if '[ETHICAL REVIEW' in caption:
            entry['status'] = 'ethical_review_required'
        elif '[NOT FOR POSTING' in caption:
            entry['status'] = 'excluded'
        elif '[CAPTION NEEDED' in caption:
            entry['status'] = 'needs_caption'
        elif '[DEFERRED' in caption:
            entry['status'] = 'deferred'

        queue.append(entry)

    return queue


def write_post_queue_md(queue, output_path):
    """Write the post queue as a markdown review document."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    status_counts = {}
    for entry in queue:
        s = entry['status']
        status_counts[s] = status_counts.get(s, 0) + 1

    lines = [
        '---',
        'type: post_queue',
        'subject: auto_generated_posts',
        f'generated: {now}',
        f'total_posts: {len(queue)}',
        'requires_human_review: true',
        '---',
        '',
        '# Post Queue — Auto-Generated',
        '',
        f'Generated: {now}',
        '',
        '## Status Summary',
        '',
        '| Status | Count |',
        '|---|---|',
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f'| {status} | {count} |')
    lines.append(f'| **Total** | **{len(queue)}** |')
    lines.append('')

    lines.append('## Review Instructions')
    lines.append('')
    lines.append('- [ ] Review each caption for voice fidelity')
    lines.append('- [ ] Approve, edit, or reject each post')
    lines.append('- [ ] Set posting order and dates')
    lines.append('- [ ] Mark `approved` to move to posting pipeline')
    lines.append('- [ ] Posts marked `ethical_review_required` need extra scrutiny')
    lines.append('- [ ] Posts marked `needs_caption` require manual caption writing or API generation')
    lines.append('')
    lines.append('---')
    lines.append('')

    for entry in queue:
        if entry['status'] == 'excluded':
            continue

        lines.append(f'## {entry["id"]} — {entry["register"]}')
        lines.append('')
        lines.append(f'**Status:** `{entry["status"]}`')
        lines.append(f'**Image:** `{entry["image_path"][:80]}`')
        lines.append(f'**Platform:** {entry["platform"]}')
        lines.append(f'**Aspect:** {entry["aspect_ratio"]}')
        lines.append(f'**Tags:** {", ".join(entry["tags"]) if entry["tags"] else "—"}')
        lines.append(f'**Caption source:** {entry["caption_source"]}')
        lines.append('')
        lines.append('**Caption:**')
        lines.append('```')
        lines.append(entry['caption'])
        lines.append('```')
        lines.append('')
        lines.append(f'**Alt text:** {entry["alt_text"]}')
        lines.append('')
        lines.append('**Review:** [ ] approve  [ ] edit  [ ] reject')
        lines.append('')
        lines.append('---')
        lines.append('')

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def write_post_queue_json(queue, output_path):
    with open(output_path, 'w') as f:
        json.dump(queue, f, indent=2)


def main():
    base_image_dir = os.environ.get(
        'EXAMPLEIMAGE26_DIR',
        '/Users/jamessherringham/.gemini/antigravity/scratch/soul.md-main/aesthetic_corpus/visual/examples/EXAMPLEIMAGE26'
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    ops_dir = os.path.join(repo_root, 'operations')

    manifest_path = os.path.join(ops_dir, 'image_manifest.json')
    if not os.path.exists(manifest_path):
        print('ERROR: Run scan_images.py first to generate the manifest.')
        sys.exit(1)

    use_api = '--api' in sys.argv
    limit = None
    for arg in sys.argv[1:]:
        if arg.startswith('--limit='):
            limit = int(arg.split('=')[1])

    print(f'Mode: {"Claude API" if use_api else "template-based"}')
    if limit:
        print(f'Limit: {limit} images')

    queue = process_manifest(manifest_path, base_image_dir, repo_root, use_api=use_api, limit=limit)

    md_output = os.path.join(ops_dir, 'POST_QUEUE.md')
    json_output = os.path.join(ops_dir, 'post_queue.json')

    write_post_queue_md(queue, md_output)
    print(f'Post queue written: {md_output}')

    write_post_queue_json(queue, json_output)
    print(f'JSON queue written: {json_output}')

    status_counts = {}
    for entry in queue:
        s = entry['status']
        status_counts[s] = status_counts.get(s, 0) + 1
    print(f'\nQueue summary:')
    for status, count in sorted(status_counts.items()):
        print(f'  {status}: {count}')


if __name__ == '__main__':
    main()

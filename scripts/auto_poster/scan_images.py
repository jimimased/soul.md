#!/usr/bin/env python3
"""
Scan EXAMPLEIMAGE26 directory tree, classify images by folder structure,
and write an image manifest for the caption generator.

Folder taxonomy (from the user's own directory naming):
  ART22 outputs/  → processed ComfyUI art (face grids, halftone, silhouettes)
  FACE/           → face reference images
  SUBJECT/        → documentary/personal photography by subject
  VIDEO/          → video source material (skipped for image posts)

Output: operations/IMAGE_MANIFEST.md
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.tiff', '.tif', '.bmp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

FOLDER_TAXONOMY = {
    'ART22 outputs': {
        'register': 'processed_art',
        'post_type': 'face_grid_or_halftone',
        'platform': 'instagram_primary',
        'description': 'ComfyUI processed outputs — face grids, halftone compositions, silhouettes',
    },
    'FACE': {
        'register': 'face_reference',
        'post_type': 'portrait',
        'platform': 'instagram_secondary',
        'description': 'Face reference images for processing pipeline',
    },
    'SUBJECT': {
        'register': 'documentary',
        'post_type': 'documentary_texture',
        'platform': 'instagram_secondary',
        'description': 'Documentary and personal photography organized by subject',
    },
    'VIDEO': {
        'register': 'video',
        'post_type': 'video_register',
        'platform': 'youtube',
        'description': 'Video source material — deferred to VIDEO_REGISTER',
    },
}

SUBJECT_SUBFOLDER_TAGS = {
    'eastlondontexture': ['street_art', 'wall_texture', 'shoreditch', 'london', 'urban_palimpsest'],
    'Taiwan': ['taiwan', 'taipei', 'street', 'night_market', 'documentary'],
    'Nauru': ['nauru', 'pacific', 'detention', 'documentary'],
    'nauruallfoldersin1': ['nauru', 'pacific', 'documentary'],
    'nauruallfoldersin2': ['nauru', 'pacific', 'documentary'],
    'Fashion': ['fashion', 'body', 'texture'],
    'TOUCHEDBYGOD': ['sacred', 'religious', 'intensity'],
    'WANKER': ['provocative', 'confrontation', 'body'],
    'rubbertrees': ['nature', 'plantation', 'colonial', 'texture'],
    'tunisia-images': ['tunisia', 'north_africa', 'documentary'],
    'JIMI-POWERHOUSE': ['portrait', 'self', 'performance'],
    'PHOTOS': ['mixed', 'documentary'],
    'pictures': ['mixed', 'personal'],
    'Archive': ['archive', 'historical'],
    'allimagesAI': ['ai_generated', 'processed'],
    'JIM IMAGES': ['portrait', 'self'],
    '8058girl': ['portrait', 'figure'],
    'inputframes': ['source', 'pipeline_input'],
    'good times': ['personal', 'documentary', 'memory'],
}


def file_hash(filepath, block_size=65536):
    h = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read(block_size)
            while buf:
                h.update(buf)
                buf = f.read(block_size)
    except (OSError, PermissionError):
        return 'unreadable'
    return h.hexdigest()[:12]


def classify_image(filepath, base_dir):
    rel = os.path.relpath(filepath, base_dir)
    parts = Path(rel).parts

    top_folder = parts[0] if parts else 'unknown'
    taxonomy = FOLDER_TAXONOMY.get(top_folder, {
        'register': 'uncategorized',
        'post_type': 'unknown',
        'platform': 'review_required',
        'description': f'Uncategorized file in {top_folder}/',
    })

    tags = []
    if top_folder == 'SUBJECT' and len(parts) > 1:
        subfolder = parts[1]
        tags = SUBJECT_SUBFOLDER_TAGS.get(subfolder, [subfolder.lower().replace(' ', '_')])

    fname = os.path.basename(filepath)
    fname_lower = fname.lower()
    if 'comfyui' in fname_lower:
        tags.append('comfyui_output')
    if 'face' in fname_lower or 'grid' in fname_lower:
        tags.append('face_grid')
    if 'invert' in fname_lower:
        tags.append('inverted')
    if 'hyperrealism' in fname_lower or 'vray' in fname_lower:
        tags.append('hyperrealism')
    if 'mirror' in fname_lower:
        tags.append('mirror')
    if 'silhouette' in fname_lower or 'shadow' in fname_lower:
        tags.append('silhouette')

    ext = os.path.splitext(filepath)[1].lower()

    return {
        'filename': fname,
        'relative_path': rel,
        'top_folder': top_folder,
        'register': taxonomy['register'],
        'post_type': taxonomy['post_type'],
        'platform': taxonomy['platform'],
        'tags': sorted(set(tags)),
        'extension': ext,
        'size_bytes': os.path.getsize(filepath),
    }


def scan_directory(base_dir):
    images = []
    videos = []
    skipped = []

    for root, dirs, files in os.walk(base_dir):
        dirs.sort()
        for fname in sorted(files):
            if fname.startswith('.'):
                continue
            filepath = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()

            if ext in IMAGE_EXTENSIONS:
                entry = classify_image(filepath, base_dir)
                images.append(entry)
            elif ext in VIDEO_EXTENSIONS:
                videos.append({
                    'filename': fname,
                    'relative_path': os.path.relpath(filepath, base_dir),
                    'type': 'video',
                })
            else:
                skipped.append(os.path.relpath(filepath, base_dir))

    return images, videos, skipped


def write_manifest(images, videos, skipped, output_path):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    by_register = {}
    for img in images:
        r = img['register']
        if r not in by_register:
            by_register[r] = []
        by_register[r].append(img)

    lines = [
        '---',
        'type: manifest',
        'subject: image_corpus',
        f'generated: {now}',
        f'total_images: {len(images)}',
        f'total_videos: {len(videos)}',
        f'total_skipped: {len(skipped)}',
        'status: ready_for_caption_generation',
        '---',
        '',
        '# Image Manifest — EXAMPLEIMAGE26',
        '',
        f'Generated: {now}',
        '',
        '## Summary',
        '',
        f'| Register | Count |',
        f'|---|---|',
    ]

    for register, imgs in sorted(by_register.items()):
        lines.append(f'| {register} | {len(imgs)} |')

    lines.append(f'| **Total images** | **{len(images)}** |')
    lines.append(f'| Videos (deferred) | {len(videos)} |')
    lines.append(f'| Skipped (non-media) | {len(skipped)} |')
    lines.append('')

    for register, imgs in sorted(by_register.items()):
        lines.append(f'## {register.replace("_", " ").title()} ({len(imgs)} images)')
        lines.append('')

        by_subfolder = {}
        for img in imgs:
            parts = Path(img['relative_path']).parts
            subfolder = parts[1] if len(parts) > 2 else '(root)'
            if subfolder not in by_subfolder:
                by_subfolder[subfolder] = []
            by_subfolder[subfolder].append(img)

        for subfolder, sub_imgs in sorted(by_subfolder.items()):
            if subfolder != '(root)':
                lines.append(f'### {subfolder} ({len(sub_imgs)} files)')
            lines.append('')
            lines.append('| File | Tags | Size | Post Type |')
            lines.append('|---|---|---|---|')
            for img in sub_imgs[:50]:
                tags_str = ', '.join(img['tags']) if img['tags'] else '—'
                size_kb = img['size_bytes'] // 1024
                lines.append(f'| `{img["filename"][:60]}` | {tags_str} | {size_kb}KB | {img["post_type"]} |')
            if len(sub_imgs) > 50:
                lines.append(f'| ... | *{len(sub_imgs) - 50} more files* | | |')
            lines.append('')

    lines.append('## Queue Priority')
    lines.append('')
    lines.append('1. **ART22 outputs** (processed_art) → Instagram primary feed')
    lines.append('2. **SUBJECT/eastlondontexture** → Instagram wall texture posts')
    lines.append('3. **SUBJECT/Taiwan** → Instagram documentary posts')
    lines.append('4. **SUBJECT/Nauru** → Instagram documentary posts (ethical review required)')
    lines.append('5. **FACE** → Pipeline input, not direct posting')
    lines.append('6. **VIDEO** → Deferred to VIDEO_REGISTER')
    lines.append('')

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    return len(images)


def write_json_manifest(images, output_path):
    with open(output_path, 'w') as f:
        json.dump(images, f, indent=2)


def main():
    base_dir = os.environ.get(
        'EXAMPLEIMAGE26_DIR',
        '/Users/jamessherringham/.gemini/antigravity/scratch/soul.md-main/aesthetic_corpus/visual/examples/EXAMPLEIMAGE26'
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    ops_dir = os.path.join(repo_root, 'operations')
    os.makedirs(ops_dir, exist_ok=True)

    md_output = os.path.join(ops_dir, 'IMAGE_MANIFEST.md')
    json_output = os.path.join(ops_dir, 'image_manifest.json')

    print(f'Scanning: {base_dir}')
    images, videos, skipped = scan_directory(base_dir)
    print(f'Found: {len(images)} images, {len(videos)} videos, {len(skipped)} skipped')

    count = write_manifest(images, videos, skipped, md_output)
    print(f'Manifest written: {md_output} ({count} images)')

    write_json_manifest(images, json_output)
    print(f'JSON manifest written: {json_output}')


if __name__ == '__main__':
    main()

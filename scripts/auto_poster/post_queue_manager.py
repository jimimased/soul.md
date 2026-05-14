#!/usr/bin/env python3
"""
Post queue manager — approve, schedule, and track posts.

Commands:
  list              Show all posts and their status
  approve <id>      Mark a post as approved
  reject <id>       Mark a post as rejected
  schedule <id> <date>  Schedule a post for a specific date (YYYY-MM-DD)
  next              Show the next approved post ready to publish
  publish <id>      Mark a post as published (after manual posting)
  stats             Show queue statistics
  export-approved   Export approved posts as a batch for posting
"""

import os
import sys
import json
from datetime import datetime


def load_queue(queue_path):
    with open(queue_path) as f:
        return json.load(f)


def save_queue(queue, queue_path):
    with open(queue_path, 'w') as f:
        json.dump(queue, f, indent=2)


def find_post(queue, post_id):
    for entry in queue:
        if entry['id'] == post_id:
            return entry
    return None


def cmd_list(queue, status_filter=None):
    for entry in queue:
        if status_filter and entry['status'] != status_filter:
            continue
        tags = ', '.join(entry.get('tags', [])[:3])
        caption_preview = entry['caption'][:50].replace('\n', ' ')
        scheduled = entry.get('scheduled_date', '')
        print(f"  {entry['id']}  [{entry['status']:20s}]  {entry['register']:15s}  {caption_preview}{'...' if len(entry['caption']) > 50 else ''}")
        if scheduled:
            print(f"           scheduled: {scheduled}")


def cmd_approve(queue, post_id):
    entry = find_post(queue, post_id)
    if not entry:
        print(f'Post {post_id} not found.')
        return
    entry['status'] = 'approved'
    entry['approved_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    print(f'Approved: {post_id}')


def cmd_reject(queue, post_id):
    entry = find_post(queue, post_id)
    if not entry:
        print(f'Post {post_id} not found.')
        return
    entry['status'] = 'rejected'
    print(f'Rejected: {post_id}')


def cmd_schedule(queue, post_id, date_str):
    entry = find_post(queue, post_id)
    if not entry:
        print(f'Post {post_id} not found.')
        return
    entry['scheduled_date'] = date_str
    if entry['status'] == 'pending_review':
        entry['status'] = 'approved'
    print(f'Scheduled {post_id} for {date_str}')


def cmd_publish(queue, post_id):
    entry = find_post(queue, post_id)
    if not entry:
        print(f'Post {post_id} not found.')
        return
    entry['status'] = 'published'
    entry['published_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    print(f'Published: {post_id}')


def cmd_next(queue):
    approved = [e for e in queue if e['status'] == 'approved']
    scheduled = [e for e in approved if 'scheduled_date' in e]
    scheduled.sort(key=lambda e: e['scheduled_date'])

    if scheduled:
        entry = scheduled[0]
    elif approved:
        entry = approved[0]
    else:
        print('No approved posts in queue.')
        return

    print(f"\nNext post: {entry['id']}")
    print(f"Platform: {entry['platform']}")
    print(f"Image: {entry['image_path']}")
    print(f"Aspect: {entry['aspect_ratio']}")
    if entry.get('scheduled_date'):
        print(f"Scheduled: {entry['scheduled_date']}")
    print(f"\nCaption:\n{entry['caption']}")
    print(f"\nAlt text: {entry['alt_text']}")


def cmd_stats(queue):
    status_counts = {}
    register_counts = {}
    for entry in queue:
        s = entry['status']
        r = entry['register']
        status_counts[s] = status_counts.get(s, 0) + 1
        register_counts[r] = register_counts.get(r, 0) + 1

    print('\nBy status:')
    for s, c in sorted(status_counts.items()):
        print(f'  {s}: {c}')

    print('\nBy register:')
    for r, c in sorted(register_counts.items()):
        print(f'  {r}: {c}')

    print(f'\nTotal: {len(queue)}')


def cmd_export_approved(queue, output_dir):
    approved = [e for e in queue if e['status'] == 'approved']
    if not approved:
        print('No approved posts to export.')
        return

    export = []
    for entry in approved:
        export.append({
            'id': entry['id'],
            'image_path': entry['image_path'],
            'caption': entry['caption'],
            'alt_text': entry['alt_text'],
            'platform': entry['platform'],
            'aspect_ratio': entry['aspect_ratio'],
            'scheduled_date': entry.get('scheduled_date', ''),
        })

    output_path = os.path.join(output_dir, 'approved_posts.json')
    with open(output_path, 'w') as f:
        json.dump(export, f, indent=2)

    print(f'Exported {len(export)} approved posts to {output_path}')


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    ops_dir = os.path.join(repo_root, 'operations')
    queue_path = os.path.join(ops_dir, 'post_queue.json')

    if not os.path.exists(queue_path):
        print('ERROR: No post queue found. Run generate_captions.py first.')
        sys.exit(1)

    queue = load_queue(queue_path)

    if len(sys.argv) < 2:
        print('Usage: post_queue_manager.py <command> [args]')
        print('Commands: list, approve, reject, schedule, next, publish, stats, export-approved')
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'list':
        status_filter = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_list(queue, status_filter)
    elif cmd == 'approve':
        if len(sys.argv) < 3:
            print('Usage: approve <post_id>')
            sys.exit(1)
        cmd_approve(queue, sys.argv[2])
        save_queue(queue, queue_path)
    elif cmd == 'reject':
        if len(sys.argv) < 3:
            print('Usage: reject <post_id>')
            sys.exit(1)
        cmd_reject(queue, sys.argv[2])
        save_queue(queue, queue_path)
    elif cmd == 'schedule':
        if len(sys.argv) < 4:
            print('Usage: schedule <post_id> <YYYY-MM-DD>')
            sys.exit(1)
        cmd_schedule(queue, sys.argv[2], sys.argv[3])
        save_queue(queue, queue_path)
    elif cmd == 'publish':
        if len(sys.argv) < 3:
            print('Usage: publish <post_id>')
            sys.exit(1)
        cmd_publish(queue, sys.argv[2])
        save_queue(queue, queue_path)
    elif cmd == 'next':
        cmd_next(queue)
    elif cmd == 'stats':
        cmd_stats(queue)
    elif cmd == 'export-approved':
        cmd_export_approved(queue, ops_dir)
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)


if __name__ == '__main__':
    main()

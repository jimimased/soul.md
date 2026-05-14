#!/usr/bin/env python3
"""
Push commits to GitHub via the Git Data API.
Bypasses git push size limits for repos with large binary data.

Usage:
  python3 push_via_api.py                    # Push current branch
  python3 push_via_api.py --branch=my-branch # Push specific branch
  python3 push_via_api.py --force            # Force update ref
"""

import subprocess
import json
import sys
import os
import base64

REPO = "jimimased/soul.md"


def gh_api(endpoint, method="GET", data=None):
    cmd = ["gh", "api", f"repos/{REPO}/{endpoint}"]
    if method != "GET":
        cmd.extend(["--method", method])
    if data:
        cmd.extend(["--input", "-"])

    result = subprocess.run(
        cmd,
        input=json.dumps(data) if data else None,
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"API error: {result.stderr}", file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout


def get_current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_commit_sha(ref="HEAD"):
    result = subprocess.run(
        ["git", "rev-parse", ref],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_changed_files(base_sha, head_sha):
    result = subprocess.run(
        ["git", "diff", "--name-status", base_sha, head_sha],
        capture_output=True, text=True
    )
    files = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('\t')
        status = parts[0]
        filepath = parts[-1]
        files.append((status, filepath))
    return files


def get_file_content(filepath, ref="HEAD"):
    result = subprocess.run(
        ["git", "show", f"{ref}:{filepath}"],
        capture_output=True
    )
    if result.returncode != 0:
        return None
    return result.stdout


def create_blob(content_bytes):
    encoded = base64.b64encode(content_bytes).decode('utf-8')
    data = {
        "content": encoded,
        "encoding": "base64"
    }
    result = gh_api("git/blobs", method="POST", data=data)
    if result and 'sha' in result:
        return result['sha']
    return None


def get_tree_sha(commit_sha):
    result = gh_api(f"git/commits/{commit_sha}")
    if result and 'tree' in result:
        return result['tree']['sha']
    return None


def create_tree(base_tree_sha, tree_entries):
    data = {
        "base_tree": base_tree_sha,
        "tree": tree_entries
    }
    result = gh_api("git/trees", method="POST", data=data)
    if result and 'sha' in result:
        return result['sha']
    return None


def create_commit(message, tree_sha, parent_shas):
    data = {
        "message": message,
        "tree": tree_sha,
        "parents": parent_shas
    }
    result = gh_api("git/commits", method="POST", data=data)
    if result and 'sha' in result:
        return result['sha']
    return None


def get_commit_message(sha):
    result = subprocess.run(
        ["git", "log", "--format=%B", "-1", sha],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_commit_parents(sha):
    result = subprocess.run(
        ["git", "log", "--format=%P", "-1", sha],
        capture_output=True, text=True
    )
    return result.stdout.strip().split()


def ref_exists(branch):
    result = gh_api(f"git/refs/heads/{branch}")
    if result and isinstance(result, dict) and 'ref' in result:
        return result['object']['sha']
    return None


def create_ref(branch, sha):
    data = {
        "ref": f"refs/heads/{branch}",
        "sha": sha
    }
    result = gh_api("git/refs", method="POST", data=data)
    return result


def update_ref(branch, sha, force=False):
    data = {
        "sha": sha,
        "force": force
    }
    result = gh_api(f"git/refs/heads/{branch}", method="PATCH", data=data)
    return result


def push_commits(branch, commits_to_push, force=False):
    """Push a series of local commits to remote via API."""

    remote_sha = ref_exists(branch)

    for i, local_sha in enumerate(commits_to_push):
        message = get_commit_message(local_sha)
        parent_local_shas = get_commit_parents(local_sha)

        print(f"\n--- Commit {i+1}/{len(commits_to_push)}: {local_sha[:8]} ---")
        print(f"Message: {message[:80]}...")

        if i == 0 and remote_sha:
            parent_remote_sha = remote_sha
        elif i == 0:
            parent_remote_sha = None
        else:
            parent_remote_sha = prev_remote_sha

        if parent_remote_sha:
            changed = get_changed_files(parent_local_shas[0] if parent_local_shas else local_sha + "~1", local_sha)
        else:
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "-r", "--name-status", local_sha],
                capture_output=True, text=True
            )
            changed = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('\t')
                changed.append((parts[0], parts[-1]))

        print(f"Files changed: {len(changed)}")

        tree_entries = []
        for status, filepath in changed:
            if status.startswith('D'):
                tree_entries.append({
                    "path": filepath,
                    "mode": "100644",
                    "type": "blob",
                    "sha": None
                })
                print(f"  D {filepath}")
            else:
                content = get_file_content(filepath, local_sha)
                if content is None:
                    print(f"  SKIP {filepath} (not found)")
                    continue

                blob_sha = create_blob(content)
                if not blob_sha:
                    print(f"  FAIL {filepath} (blob creation failed)")
                    continue

                is_executable = filepath.endswith('.sh')
                mode = "100755" if is_executable else "100644"

                tree_entries.append({
                    "path": filepath,
                    "mode": mode,
                    "type": "blob",
                    "sha": blob_sha
                })
                print(f"  {status} {filepath} → {blob_sha[:8]}")

        if parent_remote_sha:
            base_tree = get_tree_sha(parent_remote_sha)
        else:
            main_sha = ref_exists("main")
            base_tree = get_tree_sha(main_sha) if main_sha else None

        if not base_tree:
            print("ERROR: Could not get base tree SHA")
            return False

        new_tree = create_tree(base_tree, tree_entries)
        if not new_tree:
            print("ERROR: Could not create tree")
            return False

        parents = [parent_remote_sha] if parent_remote_sha else [ref_exists("main")]
        parents = [p for p in parents if p]

        new_commit = create_commit(message, new_tree, parents)
        if not new_commit:
            print("ERROR: Could not create commit")
            return False

        print(f"Created remote commit: {new_commit[:8]}")
        prev_remote_sha = new_commit

    if remote_sha:
        result = update_ref(branch, prev_remote_sha, force=force)
    else:
        result = create_ref(branch, prev_remote_sha)

    if result:
        print(f"\nBranch {branch} updated to {prev_remote_sha[:8]}")
        return True
    else:
        print("\nERROR: Failed to update ref")
        return False


def main():
    force = '--force' in sys.argv

    branch = get_current_branch()
    for arg in sys.argv[1:]:
        if arg.startswith('--branch='):
            branch = arg.split('=')[1]

    print(f"Pushing branch: {branch}")

    remote_sha = ref_exists(branch)
    if remote_sha:
        print(f"Remote HEAD: {remote_sha[:8]}")
    else:
        print("Branch does not exist on remote — will create")

    head_sha = get_commit_sha("HEAD")
    print(f"Local HEAD: {head_sha[:8]}")

    if remote_sha:
        result = subprocess.run(
            ["git", "log", "--oneline", f"{remote_sha}..HEAD"],
            capture_output=True, text=True
        )
        commits = [line.split()[0] for line in result.stdout.strip().split('\n') if line]
        commits.reverse()
    else:
        main_sha = ref_exists("main")
        if main_sha:
            result = subprocess.run(
                ["git", "log", "--oneline", f"{main_sha}..HEAD"],
                capture_output=True, text=True
            )
            commits = [line.split()[0] for line in result.stdout.strip().split('\n') if line]
            commits.reverse()
        else:
            commits = [head_sha]

    if not commits:
        print("Nothing to push — remote is up to date")
        return

    print(f"Commits to push: {len(commits)}")
    for c in commits:
        msg = get_commit_message(c)
        print(f"  {c[:8]} {msg[:60]}")

    success = push_commits(branch, commits, force=force)
    if success:
        print("\nPush complete!")
    else:
        print("\nPush failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env bash
# Run the full local librarian pass.
# Usage: ./scripts/librarian/run_librarian.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Obsidian Librarian ==="
echo "Repo: $REPO_ROOT"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

cd "$REPO_ROOT"

echo "--- Step 1: Scanning inbox ---"
python3 "$SCRIPT_DIR/scan_inbox.py"
echo ""

echo "--- Step 2: Creating metadata stubs ---"
python3 "$SCRIPT_DIR/create_metadata_stubs.py"
echo ""

echo "--- Step 3: Building source manifest ---"
python3 "$SCRIPT_DIR/build_source_manifest.py"
echo ""

echo "--- Step 4: Compiling indexes ---"
python3 "$SCRIPT_DIR/compile_indexes.py"
echo ""

echo "--- Step 5: Proposing updates ---"
python3 "$SCRIPT_DIR/propose_updates.py"
echo ""

echo "--- Step 6: Running health check ---"
python3 "$SCRIPT_DIR/health_check.py"
echo ""

echo "=== Librarian pass complete ==="
echo ""
echo "Review these files:"
echo "  operations/librarian/INGEST_QUEUE.md"
echo "  operations/librarian/SOURCE_MANIFEST.md"
echo "  operations/librarian/REVIEW_QUEUE.md"
echo "  operations/librarian/HEALTH_CHECK.md"
echo "  wiki/INDEX.md"

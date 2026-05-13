#!/usr/bin/env bash
#
# Run the full auto-poster pipeline:
#   1. Scan images → IMAGE_MANIFEST.md + image_manifest.json
#   2. Generate captions → POST_QUEUE.md + post_queue.json
#   3. (Optional) Open queue for review
#
# Usage:
#   ./run_auto_poster.sh                    # Template captions (no API key needed)
#   ./run_auto_poster.sh --api              # Claude API captions (requires ANTHROPIC_API_KEY)
#   ./run_auto_poster.sh --api --limit=20   # API captions for first 20 images only
#   ./run_auto_poster.sh --stats            # Just show queue stats

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OPS_DIR="${REPO_ROOT}/operations"

export EXAMPLEIMAGE26_DIR="${EXAMPLEIMAGE26_DIR:-/Users/jamessherringham/.gemini/antigravity/scratch/soul.md-main/aesthetic_corpus/visual/examples/EXAMPLEIMAGE26}"

echo "=== Rupture System Auto-Poster ==="
echo "Image source: ${EXAMPLEIMAGE26_DIR}"
echo "Output: ${OPS_DIR}/"
echo ""

if [[ "${1:-}" == "--stats" ]]; then
    python3 "${SCRIPT_DIR}/post_queue_manager.py" stats
    exit 0
fi

echo "--- Step 1: Scanning images ---"
python3 "${SCRIPT_DIR}/scan_images.py"
echo ""

echo "--- Step 2: Generating captions ---"
CAPTION_ARGS=""
for arg in "$@"; do
    CAPTION_ARGS="${CAPTION_ARGS} ${arg}"
done
python3 "${SCRIPT_DIR}/generate_captions.py" ${CAPTION_ARGS}
echo ""

echo "--- Step 3: Queue summary ---"
python3 "${SCRIPT_DIR}/post_queue_manager.py" stats
echo ""

echo "=== Pipeline complete ==="
echo ""
echo "Review the queue:"
echo "  cat ${OPS_DIR}/POST_QUEUE.md"
echo ""
echo "Manage posts:"
echo "  python3 ${SCRIPT_DIR}/post_queue_manager.py list"
echo "  python3 ${SCRIPT_DIR}/post_queue_manager.py approve post_0001"
echo "  python3 ${SCRIPT_DIR}/post_queue_manager.py schedule post_0001 2026-05-15"
echo "  python3 ${SCRIPT_DIR}/post_queue_manager.py next"
echo "  python3 ${SCRIPT_DIR}/post_queue_manager.py export-approved"
echo ""
echo "To generate captions with Claude API:"
echo "  ANTHROPIC_API_KEY=sk-... ./run_auto_poster.sh --api --limit=10"

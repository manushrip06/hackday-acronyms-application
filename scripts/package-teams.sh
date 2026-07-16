#!/usr/bin/env bash
# Build sideload zip after updating HTTPS URLs in manifest.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/teams"
zip -r "$ROOT/acronym-atlas-teams.zip" manifest.json color.png outline.png
echo "Wrote $ROOT/acronym-atlas-teams.zip"

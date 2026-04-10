#!/usr/bin/env bash
# doc-staleness-hook.sh — PreToolUse on Read
# Checks if a documentation file is stale by comparing last-verified date against source file mtimes.

set -euo pipefail

# Read stdin (hook input JSON) and extract file_path
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
[ -z "$FILE_PATH" ] && exit 0

BASENAME=$(basename "$FILE_PATH")
DIRNAME=$(dirname "$FILE_PATH")
FOLDERNAME=$(basename "$DIRNAME")

IS_DOC=false
if [ "$BASENAME" = "start-here.md" ]; then IS_DOC=true
elif [[ "$BASENAME" == *.ctx ]]; then IS_DOC=true
elif [ "$BASENAME" = "${FOLDERNAME}.md" ]; then IS_DOC=true
fi
[ "$IS_DOC" = false ] && exit 0
[ ! -f "$FILE_PATH" ] && exit 0

# Extract last-verified date
VERIFIED_DATE=$(grep -oP '(?<=last-verified: )\d{4}-\d{2}-\d{2}' "$FILE_PATH" 2>/dev/null | head -1)
[ -z "$VERIFIED_DATE" ] && exit 0

TOUCH_FILE=$(mktemp)
touch -d "$VERIFIED_DATE" "$TOUCH_FILE" 2>/dev/null || { rm -f "$TOUCH_FILE"; exit 0; }

# Find source files newer than last-verified date
NEWER_FILES=$(find "$DIRNAME" -maxdepth 1 -type f \
  -newer "$TOUCH_FILE" \
  ! -name '*.md' \
  ! -name '*.ctx' \
  2>/dev/null | head -5)

rm -f "$TOUCH_FILE"
[ -z "$NEWER_FILES" ] && exit 0

STALE_COUNT=$(echo "$NEWER_FILES" | wc -l)
RELATIVE_DIR=$(echo "$DIRNAME" | sed "s|^$(pwd)/||")

cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"STALENESS WARNING: ${BASENAME} last verified ${VERIFIED_DATE}, but ${STALE_COUNT} source file(s) modified since. Path: ${RELATIVE_DIR}"}}
EOF

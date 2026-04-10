#!/usr/bin/env bash
# install-ctx-git-hook.sh

HOOK_FILE=".git/hooks/pre-commit"

if [ ! -d ".git" ]; then
    echo "❌ Not a git repository."
    exit 1
fi

echo "🔧 Installing CTX-Audit Git Hook..."

# Ensure the scripts directory exists
mkdir -p scripts

cat <<'EOF' > "$HOOK_FILE"
#!/usr/bin/env bash

# Run the Shadow Auditor
if [ -f "scripts/ctx-auditor.py" ]; then
    python3 scripts/ctx-auditor.py
else
    echo "❌ scripts/ctx-auditor.py not found. Skipping audit."
    exit 0
fi

# If the auditor fails (exit code 1), warn the user
if [ $? -ne 0 ]; then
    echo -e "\n\033[1;33m⚠ ARCHITECTURE DRIFT DETECTED\033[0m"
    echo "Your .ctx files do not match the files on disk."
    echo "Please update your documentation before committing."
    echo -e "Use 'git commit --no-verify' to skip this check.\n"
    exit 1
fi
EOF

chmod +x "$HOOK_FILE"
echo "✅ Hook installed to $HOOK_FILE"

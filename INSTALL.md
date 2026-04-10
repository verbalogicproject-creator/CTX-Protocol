# Installing CTX Protocol

Follow these steps to integrate the CTX Protocol into your project.

## 1. Copy the Scripts
Copy the contents of the `scripts/` folder into your project's `scripts/` directory.

## 2. Initialize your Project
Run the heuristic generator to bootstrap your initial `.ctx` files:
```bash
python3 scripts/generate_basic_ctx.py --root .
```

## 3. Install the Git Hook (Optional but Recommended)
To prevent documentation drift, install the pre-commit hook:
```bash
chmod +x scripts/install-ctx-git-hook.sh
./scripts/install-ctx-git-hook.sh
```

## 4. Set up the Staleness Hook (Claude Code only)
If you use Claude Code, add the staleness hook to your `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "scripts/doc-staleness-hook.sh",
            "timeout": 5,
            "statusMessage": "Checking doc staleness..."
          }
        ]
      }
    ]
  }
}
```

## 5. Start Documenting
Now, when you work with an AI assistant, tell it to follow the `.ctx` format described in `docs/CTX-FORMAT-SPEC.md`.

As you build, the AI will use the `.ctx` files to understand your architecture, and the Git hook will ensure you never forget to update them.

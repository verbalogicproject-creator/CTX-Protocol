#!/usr/bin/env python3
"""
CTX Auditor — Objective architecture drift detector.
===================================================
Compares files on disk vs nodes defined in .ctx files.
Returns 0 if synced, 1 if drift detected.
"""
import os
import re
import sys
from pathlib import Path

# --- Configuration ---
SOURCE_EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs', '.json', '.md', '.sh', '.d.ts', '.css', '.html'}
EXCLUDE_DIRS = {'node_modules', '.git', '.next', '__pycache__', 'dist', 'build'}

def get_documented_folders(root):
    """Finds all folders containing a .ctx file."""
    doc_hubs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        ctx_files = [f for f in filenames if f.endswith('.ctx')]
        if ctx_files:
            doc_hubs.append(Path(dirpath))
    return doc_hubs

def parse_ctx_nodes(ctx_path):
    """Extracts node names from a .ctx file."""
    nodes = set()
    if not ctx_path.exists():
        return nodes
    with open(ctx_path, 'r') as f:
        for line in f:
            # Match "  NodeName : description [type]"
            match = re.match(r'^\s\s([\w\-\.]+)\s*:', line)
            if match:
                nodes.add(match.group(1).strip())
    return nodes

def audit_folder(folder_path):
    """Compares files on disk vs nodes in .ctx."""
    folder_path = Path(folder_path)
    ctx_file = next(folder_path.glob('*.ctx'), None)
    
    if not ctx_file:
        return None

    # 1. Get actual source files (stems)
    actual_files = {f.stem for f in folder_path.iterdir() 
                    if f.suffix in SOURCE_EXTENSIONS and f.is_file()}
    
    # 2. Get documented nodes
    documented_nodes = parse_ctx_nodes(ctx_file)

    # 3. Find gaps
    missing_in_ctx = actual_files - documented_nodes
    ghost_nodes = documented_nodes - actual_files # Nodes in ctx but file deleted

    return {
        "folder": str(folder_path),
        "missing": list(missing_in_ctx),
        "ghosts": list(ghost_nodes)
    }

def main():
    root = Path('.').absolute()
    hubs = get_documented_folders(root)
    
    issues_found = False
    print(f"🔍 Auditing {len(hubs)} context hubs...")

    for hub in hubs:
        report = audit_folder(hub)
        if report and (report['missing'] or report['ghosts']):
            issues_found = True
            print(f"\n📂 {os.path.relpath(report['folder'], root)}")
            if report['missing']:
                print(f"  ❌ Missing Nodes (Files exist but not in .ctx):")
                for m in report['missing']: print(f"     - {m}")
            if report['ghosts']:
                print(f"  👻 Ghost Nodes (In .ctx but file deleted):")
                for g in report['ghosts']: print(f"     - {g}")

    if issues_found:
        print("\n⚠️  Architecture drift detected! Run your upkeep process to resync.")
        sys.exit(1)
    else:
        print("\n✅ All context hubs are synchronized with source files.")
        sys.exit(0)

if __name__ == "__main__":
    main()

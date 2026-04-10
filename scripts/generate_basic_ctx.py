#!/usr/bin/env python3
"""
Heuristic .ctx Generator — Mechanical .ctx files from imports, no AI.
====================================================================
Scans a project directory, parses imports (Python, TypeScript, Go, Rust, Java),
and generates minimal .ctx files with nodes = source files and edges = imports.

This produces lower-quality .ctx files than AI-generated ones (no semantic
descriptions, just filenames and import edges), but it's fully automated,
reproducible, and fast — suitable for benchmarking and bootstrapping.

Usage:
  python3 scripts/generate_basic_ctx.py --root /path/to/project
  python3 scripts/generate_basic_ctx.py --root /path/to/project --dry-run
"""

import os
import re
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from datetime import date

# ============================================================================
# EXCLUSIONS
# ============================================================================

EXCLUDE_DIRS = {
    'node_modules', '.git', '.next', '__pycache__', 'dist', 'build',
    'venv', '.venv', 'target', 'vendor', '.cache', '.tox', 'egg-info',
    '.mypy_cache', '.pytest_cache', 'coverage', '.nyc_output', 'out',
    '.turbo', '.vercel', '.svelte-kit',
}

SOURCE_EXTENSIONS = {
    '.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs', '.java',
    '.kt', '.swift', '.rb', '.php', '.vue', '.svelte',
}

# ============================================================================
# IMPORT PARSERS
# ============================================================================

def parse_python_imports(content: str, file_path: str) -> List[str]:
    """Extract import targets from Python files."""
    imports = []
    for match in re.finditer(r'^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))', content, re.MULTILINE):
        module = match.group(1) or match.group(2)
        imports.append(module)
    return imports


def parse_ts_imports(content: str, file_path: str) -> List[str]:
    """Extract import targets from TypeScript/JavaScript files."""
    imports = []
    for match in re.finditer(r'''(?:import\s+.*?from\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\s*\))''', content):
        target = match.group(1) or match.group(2)
        imports.append(target)
    return imports


def parse_go_imports(content: str, file_path: str) -> List[str]:
    """Extract import targets from Go files."""
    imports = []
    # Single import
    for match in re.finditer(r'import\s+"([^"]+)"', content):
        imports.append(match.group(1))
    # Block import
    block = re.search(r'import\s*\((.*?)\)', content, re.DOTALL)
    if block:
        for match in re.finditer(r'"([^"]+)"', block.group(1)):
            imports.append(match.group(1))
    return imports


def parse_rust_imports(content: str, file_path: str) -> List[str]:
    """Extract use targets from Rust files."""
    imports = []
    for match in re.finditer(r'use\s+([\w:]+)', content):
        imports.append(match.group(1))
    return imports


def parse_java_imports(content: str, file_path: str) -> List[str]:
    """Extract import targets from Java/Kotlin files."""
    imports = []
    for match in re.finditer(r'import\s+([\w.]+)', content):
        imports.append(match.group(1))
    return imports


PARSERS = {
    '.py': parse_python_imports,
    '.ts': parse_ts_imports,
    '.tsx': parse_ts_imports,
    '.js': parse_ts_imports,
    '.jsx': parse_ts_imports,
    '.vue': parse_ts_imports,
    '.svelte': parse_ts_imports,
    '.go': parse_go_imports,
    '.rs': parse_rust_imports,
    '.java': parse_java_imports,
    '.kt': parse_java_imports,
}

# ============================================================================
# FILE SCANNER
# ============================================================================

def scan_project(root: str) -> Dict[str, List[str]]:
    """Scan project and return {dir_path: [source_files]}."""
    folders = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == '.':
            rel_dir = ''
        for f in filenames:
            ext = os.path.splitext(f)[1]
            if ext in SOURCE_EXTENSIONS:
                folders[rel_dir].append(f)
    return dict(folders)


def resolve_import(imp: str, source_dir: str, all_files: Dict[str, Set[str]], root: str) -> str:
    """Try to resolve an import string to a file in the project. Returns node name or None."""
    # Relative imports: ./foo, ../bar
    if imp.startswith('.'):
        # Convert ./foo to actual path
        parts = imp.split('/')
        resolved_dir = os.path.normpath(os.path.join(source_dir, *parts[:-1])) if len(parts) > 1 else source_dir
        target_name = parts[-1] if parts[-1] != '.' else ''
        if resolved_dir in all_files:
            for f in all_files[resolved_dir]:
                stem = os.path.splitext(f)[0]
                if stem == target_name or f == target_name:
                    return stem
        return None

    # Absolute imports: @/lib/foo, src/lib/foo
    cleaned = imp.lstrip('@/').replace('/', os.sep)
    # Try matching against all known files
    for dir_path, files in all_files.items():
        for f in files:
            stem = os.path.splitext(f)[0]
            full_stem = os.path.join(dir_path, stem) if dir_path else stem
            if full_stem == cleaned or full_stem.endswith(cleaned):
                return stem

    # Python dotted imports: services.game_runtime
    dotted = imp.replace('.', os.sep)
    for dir_path, files in all_files.items():
        for f in files:
            stem = os.path.splitext(f)[0]
            full_stem = os.path.join(dir_path, stem) if dir_path else stem
            if full_stem == dotted or full_stem.endswith(dotted):
                return stem

    return None


# ============================================================================
# .ctx GENERATOR
# ============================================================================

def infer_type(filename: str, dir_name: str) -> str:
    """Infer node type from filename and directory conventions."""
    name_lower = filename.lower()
    dir_lower = dir_name.lower()

    if 'test' in name_lower or 'spec' in name_lower or dir_lower.startswith('test'):
        return 'test'
    if 'store' in name_lower or 'store' in dir_lower:
        return 'store'
    if 'route' in name_lower or 'router' in name_lower or dir_lower == 'routes' or dir_lower == 'routers':
        return 'router'
    if 'service' in name_lower or dir_lower == 'services':
        return 'service'
    if 'config' in name_lower:
        return 'config'
    if 'type' in name_lower or dir_lower == 'types':
        return 'type'
    if 'util' in name_lower or 'helper' in name_lower or dir_lower in ('lib', 'utils', 'helpers'):
        return 'lib'
    if 'page' in name_lower or dir_lower in ('pages', 'app', 'views'):
        return 'screen'
    if 'model' in name_lower or dir_lower == 'models':
        return 'data'
    if name_lower in ('index.ts', 'index.js', 'index.tsx', 'main.py', 'app.py', 'main.go', 'main.rs'):
        return 'root'
    return 'component'


def generate_ctx_for_folder(folder_path: str, files: List[str], edges: Dict[str, List[str]],
                             root: str, today: str) -> str:
    """Generate a .ctx file content for a folder."""
    folder_name = os.path.basename(folder_path) if folder_path else os.path.basename(os.path.abspath(root))
    rel_path = folder_path or folder_name

    lines = [
        f"# {rel_path}/ — Auto-generated",
        f"# format: ctx/1.0",
        f"# last-verified: {today}",
        f"# edges: -> call/render",
        f"",
        f"## Files",
    ]

    for f in sorted(files):
        stem = os.path.splitext(f)[0]
        ntype = infer_type(f, os.path.basename(folder_path) if folder_path else '')
        ext = os.path.splitext(f)[1]
        lines.append(f"  {stem} : {f} [{ntype}]")

        # Add edges for this file
        file_edges = edges.get(stem, [])
        if file_edges:
            targets = ', '.join(sorted(set(file_edges)))
            lines.append(f"    -> {targets}")

    return '\n'.join(lines) + '\n'


def generate_start_here(folder_path: str, files: List[str], root: str, today: str) -> str:
    """Generate a start-here.md for a folder."""
    folder_name = os.path.basename(folder_path) if folder_path else os.path.basename(os.path.abspath(root))
    rel_path = folder_path or folder_name

    lines = [
        f"<!-- last-verified: {today} -->",
    ]
    if folder_path:
        lines.append(f"> Parent: [../start-here.md](../start-here.md)")
    lines += [
        f"",
        f"# {rel_path}/ — Start Here",
        f"",
        f"> Auto-generated by generate_basic_ctx.py",
        f"",
        f"| File | Type |",
        f"|------|------|",
    ]

    for f in sorted(files):
        ntype = infer_type(f, os.path.basename(folder_path) if folder_path else '')
        lines.append(f"| **{os.path.splitext(f)[0]}** | {ntype} |")

    return '\n'.join(lines) + '\n'


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Heuristic .ctx generator — no AI required")
    parser.add_argument('--root', required=True, help='Project root to scan')
    parser.add_argument('--min-files', type=int, default=2, help='Min source files per folder to generate .ctx (default: 2)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without writing')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    today = date.today().isoformat()

    print(f"Scanning {root}...")
    folders = scan_project(root)

    # Build file index for import resolution
    all_files = {k: set(v) for k, v in folders.items()}

    # Parse imports for all files
    print("Parsing imports...")
    all_edges = defaultdict(lambda: defaultdict(list))  # folder → {file_stem: [target_stems]}
    total_imports = 0
    resolved_imports = 0

    for folder_path, files in folders.items():
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext not in PARSERS:
                continue

            full_path = os.path.join(root, folder_path, f) if folder_path else os.path.join(root, f)
            try:
                with open(full_path, 'r', errors='ignore') as fh:
                    content = fh.read()
            except Exception:
                continue

            imports = PARSERS[ext](content, full_path)
            stem = os.path.splitext(f)[0]

            for imp in imports:
                total_imports += 1
                resolved = resolve_import(imp, folder_path, all_files, root)
                if resolved and resolved != stem:
                    all_edges[folder_path][stem].append(resolved)
                    resolved_imports += 1

    print(f"  Total imports: {total_imports}, resolved to project files: {resolved_imports}")

    # Generate .ctx files for qualifying folders
    generated = 0
    skipped = 0

    for folder_path, files in sorted(folders.items()):
        if len(files) < args.min_files:
            skipped += 1
            continue

        folder_name = os.path.basename(folder_path) if folder_path else os.path.basename(root)
        ctx_path = os.path.join(root, folder_path, f"{folder_name}.ctx") if folder_path else os.path.join(root, f"{folder_name}.ctx")
        sh_path = os.path.join(root, folder_path, "start-here.md") if folder_path else os.path.join(root, "start-here.md")

        # Skip if .ctx already exists (don't overwrite AI-generated files)
        if os.path.exists(ctx_path):
            print(f"  SKIP {folder_path or '(root)'} — .ctx already exists")
            skipped += 1
            continue

        edges = dict(all_edges.get(folder_path, {}))
        ctx_content = generate_ctx_for_folder(folder_path, files, edges, root, today)
        sh_content = generate_start_here(folder_path, files, root, today)

        if args.dry_run:
            print(f"\n  WOULD GENERATE: {ctx_path}")
            print(f"    {len(files)} files, {sum(len(v) for v in edges.values())} edges")
        else:
            os.makedirs(os.path.dirname(ctx_path) or '.', exist_ok=True)
            with open(ctx_path, 'w') as fh:
                fh.write(ctx_content)
            if not os.path.exists(sh_path):
                with open(sh_path, 'w') as fh:
                    fh.write(sh_content)
            print(f"  GENERATED: {folder_path or '(root)'} — {len(files)} files, {sum(len(v) for v in edges.values())} edges")

        generated += 1

    print(f"\nDone: {generated} folders documented, {skipped} skipped")
    return generated


if __name__ == "__main__":
    main()

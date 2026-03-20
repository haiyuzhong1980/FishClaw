#!/usr/bin/env python3
"""
Generate update manifest for FishClaw auto-release workflow.

Creates update_files.json containing all files needed for self-updating.
This manifest is used by the update checker to download new versions.
"""

import json
import os
import sys
from pathlib import Path


def generate_manifest(repo_root: str) -> dict:
    """Generate update manifest from repository files."""
    root = Path(repo_root)

    # Files to include in update package
    # Exclude: .git, __pycache__, data, logs, configs with secrets
    include_patterns = [
        "*.py",
        "requirements.txt",
        "static/**/*",
    ]

    exclude_dirs = {
        ".git",
        "__pycache__",
        "data",
        "logs",
        "backups",
        ".github",
        "node_modules",
        "venv",
        ".venv",
    }

    exclude_files = {
        "config.py",  # May contain user-specific paths
        ".env",
        ".env.local",
        "cookies.json",
        "database.db",
        "database.db-wal",
        "database.db-shm",
    }

    files = []

    for pattern in include_patterns:
        if "*" in pattern and "/" not in pattern:
            # Simple glob pattern
            for f in root.glob(pattern):
                if f.is_file() and f.name not in exclude_files:
                    files.append(str(f.relative_to(root)))
        elif pattern.endswith("/**/*"):
            # Recursive pattern
            dir_name = pattern.replace("/**/*", "")
            dir_path = root / dir_name
            if dir_path.exists():
                for f in dir_path.rglob("*"):
                    if f.is_file():
                        files.append(str(f.relative_to(root)))
        else:
            # Specific file
            f = root / pattern
            if f.exists() and f.is_file():
                files.append(pattern)

    # Add specific Python files at root level
    for f in root.glob("*.py"):
        if f.name not in exclude_files and f.name != "generate_update_manifest.py":
            rel_path = str(f.relative_to(root))
            if rel_path not in files:
                files.append(rel_path)

    # Add requirements.txt if exists
    req_file = root / "requirements.txt"
    if req_file.exists() and "requirements.txt" not in files:
        files.append("requirements.txt")

    # Sort for consistent output
    files.sort()

    manifest = {
        "version": "",
        "files": files,
        "timestamp": "",
    }

    # Read version from static/version.txt
    version_file = root / "static" / "version.txt"
    if version_file.exists():
        manifest["version"] = version_file.read_text().strip()

    # Add timestamp
    from datetime import datetime, timezone
    manifest["timestamp"] = datetime.now(timezone.utc).isoformat()

    return manifest


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_update_manifest.py <repo_root>", file=sys.stderr)
        sys.exit(1)

    repo_root = sys.argv[1]
    manifest = generate_manifest(repo_root)

    output_path = Path(repo_root) / "update_files.json"
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated {output_path} with {len(manifest['files'])} files")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
organizer.py - Automated File Organizer & Cleanup Utility

Scans a directory (default: ~/Downloads), sorts every file into category
subfolders based on its extension, and safely handles permission errors
and filename collisions. Prints a formatted summary when finished.

Usage:
    python organizer.py                    # organize ~/Downloads
    python organizer.py /path/to/folder    # organize a specific folder
    python organizer.py --dry-run          # preview without moving anything
"""

import argparse
import logging
import os
import shutil
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Extension -> category mapping
# ---------------------------------------------------------------------------
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".csv": "Documents",
    ".ppt": "Documents", ".pptx": "Documents", ".md": "Documents",
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".bmp": "Images", ".svg": "Images", ".webp": "Images", ".ico": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos", ".mov": "Videos",
    ".wmv": "Videos", ".flv": "Videos", ".webm": "Videos",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives", ".bz2": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".ts": "Code", ".java": "Code",
    ".c": "Code", ".cpp": "Code", ".h": "Code", ".html": "Code",
    ".css": "Code", ".json": "Code", ".sql": "Code", ".sh": "Code",
}

DEFAULT_CATEGORY = "Others"
CATEGORY_FOLDERS = set(EXTENSION_MAP.values()) | {DEFAULT_CATEGORY}
LOG_FILE = "organizer.log"

logger = logging.getLogger("organizer")


def setup_logging(log_path: Path) -> None:
    """Log to both the console and a log file."""
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)
    try:
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning("Could not create log file %s: %s", log_path, exc)


def get_category(filename: str) -> str:
    """Return the category folder for a file based on its extension."""
    return EXTENSION_MAP.get(Path(filename).suffix.lower(), DEFAULT_CATEGORY)


def unique_destination(dest: Path) -> Path:
    """If dest already exists, append _1, _2, ... until the name is free."""
    if not dest.exists():
        return dest
    counter = 1
    while True:
        candidate = dest.with_name(f"{dest.stem}_{counter}{dest.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize(target: Path, dry_run: bool = False) -> dict:
    """Organize files directly inside `target`. Returns stats."""
    stats = {"moved": Counter(), "skipped": 0, "errors": 0, "renamed": 0}

    with os.scandir(target) as entries:
        files = [e for e in entries if e.is_file(follow_symlinks=False)]

    for entry in files:
        # Don't move the script itself or its log file
        if entry.name in {Path(__file__).name, LOG_FILE}:
            stats["skipped"] += 1
            continue

        category = get_category(entry.name)
        dest_dir = target / category
        src = Path(entry.path)

        try:
            if not dry_run:
                dest_dir.mkdir(exist_ok=True)
            dest = unique_destination(dest_dir / entry.name)
            if dest.name != entry.name:
                stats["renamed"] += 1

            if dry_run:
                logger.info("[DRY RUN] %s -> %s/%s", entry.name, category, dest.name)
            else:
                shutil.move(str(src), str(dest))
                logger.info("Moved %s -> %s/%s", entry.name, category, dest.name)
            stats["moved"][category] += 1

        except PermissionError:
            logger.error("Permission denied: %s (file may be open or protected)", entry.name)
            stats["errors"] += 1
        except FileExistsError:
            logger.error("File already exists, skipped: %s", entry.name)
            stats["errors"] += 1
        except OSError as exc:
            logger.error("Failed to move %s: %s", entry.name, exc)
            stats["errors"] += 1

    return stats


def print_summary(target: Path, stats: dict, dry_run: bool) -> None:
    total = sum(stats["moved"].values())
    line = "=" * 46
    print(f"\n{line}")
    print(f"  EXECUTION SUMMARY{' (DRY RUN)' if dry_run else ''}")
    print(line)
    print(f"  Directory : {target}")
    for category in sorted(stats["moved"]):
        print(f"  {category:<12}: {stats['moved'][category]:>4} file(s)")
    print("-" * 46)
    print(f"  Total {'to relocate' if dry_run else 'relocated'} : {total}")
    print(f"  Renamed (collisions) : {stats['renamed']}")
    print(f"  Skipped              : {stats['skipped']}")
    print(f"  Errors               : {stats['errors']}")
    print(f"{line}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize files into category folders.")
    parser.add_argument("directory", nargs="?", default=str(Path.home() / "Downloads"),
                        help="Directory to organize (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would happen without moving files")
    args = parser.parse_args()

    target = Path(args.directory).expanduser().resolve()
    if not target.is_dir():
        raise SystemExit(f"Error: '{target}' is not a valid directory.")

    setup_logging(Path(__file__).resolve().parent / LOG_FILE)
    logger.info("Starting organizer on %s", target)

    try:
        stats = organize(target, dry_run=args.dry_run)
    except PermissionError:
        raise SystemExit(f"Error: no permission to read '{target}'.")

    print_summary(target, stats, args.dry_run)


if __name__ == "__main__":
    main()

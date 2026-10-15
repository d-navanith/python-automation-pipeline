"""
01_downloads_cleaner.py - Production-Ready Folder Organizer

Features:
1. Safe Dry-Run Mode: Preview all moves before actually touching any files.
2. Collision Safe: Never overwrites files with identical names (auto appends _1, _2).
3. Temporary File Filter: Skips in-progress downloads (.crdownload, .tmp, .part).
4. Comprehensive Categories: Documents, Media, Archives, Installers, Code, etc.
"""

import shutil
import sys
from pathlib import Path
from datetime import datetime

# Comprehensive extension to folder mapping
EXTENSION_MAPPINGS = {
    # Documents
    ".pdf": "Documents/PDFs",
    ".docx": "Documents/Word",
    ".doc": "Documents/Word",
    ".pptx": "Documents/PowerPoint",
    ".ppt": "Documents/PowerPoint",
    ".txt": "Documents/Text",
    ".md": "Documents/Markdown",
    
    # Spreadsheets & Data
    ".xlsx": "Spreadsheets/Excel",
    ".xls": "Spreadsheets/Excel",
    ".csv": "Spreadsheets/CSV",
    ".json": "Data/JSON",
    ".xml": "Data/XML",
    
    # Images
    ".png": "Media/Images",
    ".jpg": "Media/Images",
    ".jpeg": "Media/Images",
    ".webp": "Media/Images",
    ".gif": "Media/Images",
    ".svg": "Media/Images",
    
    # Audio & Video
    ".mp3": "Media/Audio",
    ".wav": "Media/Audio",
    ".m4a": "Media/Audio",
    ".flac": "Media/Audio",
    ".mp4": "Media/Videos",
    ".mkv": "Media/Videos",
    ".mov": "Media/Videos",
    ".avi": "Media/Videos",
    
    # Archives & Compressed Files
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    
    # Installers & Executables
    ".exe": "Installers",
    ".msi": "Installers",
    ".iso": "Installers",
    
    # Code & Scripts
    ".py": "Code/Python",
    ".js": "Code/JavaScript",
    ".html": "Code/Web",
    ".css": "Code/Web",
    ".sql": "Code/SQL",
}

# Temporary or system files that should NEVER be moved
IGNORE_EXTENSIONS = {
    ".tmp",
    ".crdownload",  # Chrome in-progress download
    ".part",        # Firefox in-progress download
    ".ini",         # Windows desktop.ini
}


def get_unique_destination(destination_dir: Path, filename: str) -> Path:
    """
    Prevents accidental overwrites. If 'report.pdf' already exists in target,
    it returns 'report_1.pdf', 'report_2.pdf', etc.
    """
    target = destination_dir / filename
    if not target.exists():
        return target
        
    stem = target.stem
    suffix = target.suffix
    counter = 1
    
    while target.exists():
        target = destination_dir / f"{stem}_{counter}{suffix}"
        counter += 1
        
    return target


def organize_downloads(folder_path: Path, dry_run: bool = True) -> dict:
    """
    Organizes all loose files in folder_path.
    If dry_run is True, prints what would happen without moving files.
    If dry_run is False, actually executes the moves safely.
    """
    if not folder_path.exists():
        print(f"[ERROR] Target directory does not exist: {folder_path}")
        return {"error": "Directory not found"}

    print("=" * 65)
    print(f" TARGET FOLDER: {folder_path}")
    print(f" MODE:          {'[PREVIEW / DRY-RUN] (No files will be moved)' if dry_run else '[LIVE EXECUTION] (Files will be moved)'}")
    print("=" * 65)

    stats = {"processed": 0, "ignored": 0, "skipped_dirs": 0}
    moves_planned = []

    for item in folder_path.iterdir():
        # Do not organize existing folders or subdirectories
        if item.is_dir():
            stats["skipped_dirs"] += 1
            continue

        file_ext = item.suffix.lower()

        # Skip temporary files
        if file_ext in IGNORE_EXTENSIONS or item.name.startswith("."):
            print(f"  [SKIPPED - Temp/System] {item.name}")
            stats["ignored"] += 1
            continue

        # Look up category subfolder
        subfolder = EXTENSION_MAPPINGS.get(file_ext, "Miscellaneous")
        target_dir = folder_path / subfolder
        target_path = get_unique_destination(target_dir, item.name)

        moves_planned.append((item, target_path, subfolder))

    if not moves_planned:
        print("[INFO] No loose files found to organize. Everything is already clean!")
        return stats

    for source, destination, subfolder in moves_planned:
        stats["processed"] += 1
        action_prefix = "  [WOULD MOVE]" if dry_run else "  --> [MOVED]"
        print(f"{action_prefix} {source.name:<32} to [{subfolder}]")

        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))

    print("-" * 65)
    print(f"[SUMMARY] Total files: {stats['processed']} | Skipped: {stats['ignored']}")
    if dry_run:
        print("[TIP] To perform the actual cleanup, run with dry_run=False.")
    else:
        print("[SUCCESS] Cleanup finished safely!")
    print("=" * 65)

    return stats


if __name__ == "__main__":
    # Automatically locate user's real Windows Downloads folder
    user_downloads = Path.home() / "Downloads"
    
    # By default, run in SAFE PREVIEW mode (dry_run=True)
    # Check if user passed '--live' as a command-line argument
    is_live = "--live" in sys.argv
    
    organize_downloads(user_downloads, dry_run=not is_live)

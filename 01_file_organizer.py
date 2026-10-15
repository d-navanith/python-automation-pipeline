"""
01_file_organizer.py - Beginner Automation Script 01
Concept: Turn 15-30 minutes of manual file sorting into 1 second.
Uses Python's built-in libraries (pathlib, shutil) - no extra install required!
"""

import shutil
from pathlib import Path
from datetime import datetime

# 1. Define folder rules (File extension -> Target folder name)
EXTENSION_MAPPINGS = {
    # Documents
    ".pdf": "Documents/PDFs",
    ".docx": "Documents/Word",
    ".txt": "Documents/Notes",
    
    # Spreadsheets / Data
    ".xlsx": "Data/Excel",
    ".csv": "Data/CSV",
    
    # Images / Media
    ".png": "Media/Images",
    ".jpg": "Media/Images",
    ".jpeg": "Media/Images",
    
    # Code & Archives
    ".zip": "Archives",
    ".py": "Code",
}


def create_demo_files(target_dir: Path):
    """Creates a sample messy folder to test our automation safely."""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    sample_files = [
        "october_sales_report.xlsx",
        "customer_list.csv",
        "project_specification.pdf",
        "invoice_1042.pdf",
        "meeting_notes.txt",
        "profile_picture.png",
        "backup_archive.zip",
        "quick_test.py",
        "readme_first.docx"
    ]
    
    for filename in sample_files:
        file_path = target_dir / filename
        if not file_path.exists():
            file_path.write_text(f"Sample content for {filename}\nCreated at: {datetime.now()}", encoding="utf-8")
    
    print(f"[OK] Created {len(sample_files)} messy sample files in: {target_dir}\n")


def organize_folder(source_dir: Path) -> dict:
    """
    Scans source_dir, sorts each file based on EXTENSION_MAPPINGS,
    and moves it into its appropriate subfolder.
    """
    stats = {"moved": 0, "skipped": 0}
    
    print(f"[CLEANUP] Starting cleanup in: {source_dir}")
    print("-" * 55)
    
    for item in source_dir.iterdir():
        # Only process files, skip directories we created
        if not item.is_file():
            continue
            
        file_ext = item.suffix.lower()
        destination_subfolder = EXTENSION_MAPPINGS.get(file_ext, "Miscellaneous")
        
        target_folder = source_dir / destination_subfolder
        target_folder.mkdir(parents=True, exist_ok=True)
        
        target_path = target_folder / item.name
        
        # Move the file
        shutil.move(str(item), str(target_path))
        print(f"  --> Moved: {item.name:<30} to [{destination_subfolder}]")
        stats["moved"] += 1
        
    print("-" * 55)
    print(f"[SUCCESS] Done! {stats['moved']} file(s) organized in milliseconds.\n")
    return stats


if __name__ == "__main__":
    # Safe practice folder located right inside this workspace
    workspace_inbox = Path(__file__).parent / "demo_workspace" / "messy_inbox"
    
    # Step 1: Create sample messy files
    create_demo_files(workspace_inbox)
    
    # Step 2: Run the automation to sort them
    organize_folder(workspace_inbox)

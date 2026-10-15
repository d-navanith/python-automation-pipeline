"""
tests/test_file_organizer.py - Automated QA Test Suite for File Organizer

Tests verify:
1. Dry-run mode does not move files.
2. Live mode moves files to the correct subfolder based on extension.
3. Temporary download files (.crdownload, .tmp) are ignored.
4. Name collisions automatically append counters (_1, _2).
"""

from pathlib import Path
import sys

# Add project root to sys.path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from downloads_cleaner import organize_downloads, get_unique_destination


class TestFileOrganizer:
    """Group of automated tests for the File Organizer logic."""

    def test_dry_run_does_not_move_files(self, tmp_path):
        """In dry_run mode, source files should remain in place."""
        # Create a sample PDF in temp test folder
        test_pdf = tmp_path / "sample_invoice.pdf"
        test_pdf.write_text("dummy invoice content", encoding="utf-8")

        stats = organize_downloads(tmp_path, dry_run=True)

        # Assertions
        assert test_pdf.exists(), "File should still exist in root during dry-run"
        assert not (tmp_path / "Documents" / "PDFs" / "sample_invoice.pdf").exists()
        assert stats["processed"] == 1

    def test_live_mode_moves_file_to_correct_folder(self, tmp_path):
        """In live mode, files must be moved into their designated category folder."""
        test_excel = tmp_path / "sales.xlsx"
        test_excel.write_text("excel data", encoding="utf-8")

        stats = organize_downloads(tmp_path, dry_run=False)

        # Assertions
        assert not test_excel.exists(), "Original file should have been moved from root"
        destination = tmp_path / "Spreadsheets" / "Excel" / "sales.xlsx"
        assert destination.exists(), f"File should exist at {destination}"
        assert stats["processed"] == 1

    def test_temporary_downloads_are_ignored(self, tmp_path):
        """Incomplete browser downloads (.crdownload, .tmp) must be skipped."""
        temp_download = tmp_path / "large_file.zip.crdownload"
        temp_download.write_text("in progress download data", encoding="utf-8")

        stats = organize_downloads(tmp_path, dry_run=False)

        # Assertions
        assert temp_download.exists(), "Temporary file must not be moved"
        assert stats["ignored"] == 1
        assert stats["processed"] == 0

    def test_name_collision_protection(self, tmp_path):
        """If a file with the same name already exists, append _1, _2."""
        dest_folder = tmp_path / "Documents" / "PDFs"
        dest_folder.mkdir(parents=True, exist_ok=True)

        # Existing file in destination
        (dest_folder / "contract.pdf").write_text("v1", encoding="utf-8")

        # Call get_unique_destination for incoming contract.pdf
        unique_path = get_unique_destination(dest_folder, "contract.pdf")

        # Assertions
        assert unique_path.name == "contract_1.pdf"

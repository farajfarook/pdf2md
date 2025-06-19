"""
Basic tests for the PDF to Markdown converter
"""

import pytest
from pathlib import Path
import tempfile
import os

# Import our modules
from src.pdf_analyzer import PDFAnalyzer
from src.converter import PDFToMarkdownConverter


class TestPDFAnalyzer:
    """Test the PDF analyzer functionality"""

    def test_analyzer_init(self):
        """Test that analyzer can be initialized"""
        # Create a dummy path for testing
        test_path = "test.pdf"
        analyzer = PDFAnalyzer(test_path)

        assert analyzer.pdf_path == test_path
        assert analyzer.doc is None
        assert analyzer.analysis_results == {}

    def test_analyzer_with_nonexistent_file(self):
        """Test analyzer behavior with non-existent file"""
        analyzer = PDFAnalyzer("nonexistent.pdf")
        result = analyzer.open_pdf()

        assert result is False


class TestPDFToMarkdownConverter:
    """Test the main converter functionality"""

    def test_converter_init(self):
        """Test that converter can be initialized"""
        test_path = "test.pdf"
        converter = PDFToMarkdownConverter(test_path)

        assert converter.pdf_path == Path(test_path)
        assert converter.output_path == Path("test.md")
        assert converter.images_dir == "images"
        assert converter.quality == "medium"
        assert converter.output_format == "standard"
        assert converter.verbose is False

    def test_converter_custom_output(self):
        """Test converter with custom output settings"""
        converter = PDFToMarkdownConverter(
            "test.pdf",
            output_path="custom.md",
            images_dir="assets",
            quality="high",
            output_format="github",
            verbose=True,
        )

        assert converter.output_path == Path("custom.md")
        assert converter.images_dir == "assets"
        assert converter.quality == "high"
        assert converter.output_format == "github"
        assert converter.verbose is True


class TestUtilityFunctions:
    """Test utility functions"""

    def test_path_handling(self):
        """Test that path handling works correctly"""
        # Test Path operations
        test_path = Path("test.pdf")
        md_path = test_path.with_suffix(".md")

        assert str(md_path) == "test.md"
        assert md_path.suffix == ".md"

    def test_file_extensions(self):
        """Test file extension handling"""
        pdf_files = ["doc.pdf", "report.PDF", "file.pdf"]

        for file in pdf_files:
            path = Path(file)
            assert path.suffix.lower() == ".pdf"


# Integration tests (these would need actual PDF files)
class TestIntegration:
    """Integration tests - these require actual PDF files to run"""

    @pytest.mark.skip(reason="Requires actual PDF file")
    def test_full_conversion_workflow(self):
        """Test the complete conversion workflow"""
        # This test would require a sample PDF file
        # It's skipped by default but can be enabled when PDF samples are available
        pass

    def test_temp_file_cleanup(self):
        """Test that temporary files are cleaned up properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some test files
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")

            assert test_file.exists()

        # After context manager, temp directory should be cleaned up
        assert not temp_path.exists()


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])

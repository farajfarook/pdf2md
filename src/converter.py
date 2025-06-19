"""
Main Converter - Orchestrates the PDF to Markdown conversion process
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Import our modules
from .pdf_analyzer import PDFAnalyzer
from .image_extractor import ImageExtractor
from .text_processor import TextProcessor
from .markdown_generator import MarkdownGenerator

logger = logging.getLogger(__name__)


class PDFToMarkdownConverter:
    """Main converter class that orchestrates the entire conversion process"""

    def __init__(
        self,
        pdf_path: str,
        output_path: Optional[str] = None,
        images_dir: str = "images",
        quality: str = "medium",
        output_format: str = "standard",
        verbose: bool = False,
    ):
        self.pdf_path = Path(pdf_path)
        self.output_path = (
            Path(output_path) if output_path else self.pdf_path.with_suffix(".md")
        )
        self.images_dir = images_dir
        self.quality = quality
        self.output_format = output_format
        self.verbose = verbose

        # Initialize components
        self.analyzer = None
        self.image_extractor = None
        self.text_processor = None
        self.markdown_generator = None

        # Results storage
        self.analysis_results = {}
        self.extracted_text = {}
        self.extracted_images = []
        self.generated_markdown = ""

        # Set up logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def convert(self) -> bool:
        """
        Main conversion method
        Returns: True if successful, False otherwise
        """
        try:
            logger.info(f"Starting conversion: {self.pdf_path} -> {self.output_path}")

            # Step 1: Analyze PDF
            if not self._analyze_pdf():
                logger.error("PDF analysis failed")
                return False

            # Step 2: Extract text and images
            if not self._extract_content():
                logger.error("Content extraction failed")
                return False

            # Step 3: Generate markdown
            if not self._generate_markdown():
                logger.error("Markdown generation failed")
                return False

            # Step 4: Save results
            if not self._save_results():
                logger.error("Failed to save results")
                return False

            logger.info("Conversion completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return False

    def _analyze_pdf(self) -> bool:
        """Analyze the PDF to determine extraction strategy"""
        try:
            logger.info("Analyzing PDF structure...")

            self.analyzer = PDFAnalyzer(str(self.pdf_path))
            if not self.analyzer.open_pdf():
                return False

            self.analysis_results = self.analyzer.analyze_document()

            if self.verbose:
                print(self.analyzer.get_document_summary())

            return True

        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            return False

    def _extract_content(self) -> bool:
        """Extract text and images from the PDF"""
        try:
            # Initialize processors
            self.text_processor = TextProcessor(self.analyzer.doc)
            self.image_extractor = ImageExtractor(self.analyzer.doc, self.images_dir)

            # Extract text
            logger.info("Extracting text content...")
            self.extracted_text = self.text_processor.extract_all_text()

            # Extract images
            logger.info("Extracting images...")
            self.extracted_images = self.image_extractor.extract_all_images()

            # Optimize images if requested
            if self.quality != "original":
                logger.info(f"Optimizing images (quality: {self.quality})...")
                for img in self.extracted_images:
                    self.image_extractor.optimize_image(img["filepath"], self.quality)

            if self.verbose:
                print(self.text_processor.get_extraction_summary())
                print(self.image_extractor.get_extraction_summary())

            return True

        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return False

    def _generate_markdown(self) -> bool:
        """Generate markdown from extracted content"""
        try:
            logger.info("Generating Markdown...")

            self.markdown_generator = MarkdownGenerator(
                self.extracted_text, self.extracted_images, self.output_format
            )

            self.generated_markdown = self.markdown_generator.generate_markdown()

            if self.verbose:
                print(self.markdown_generator.get_generation_summary())

            return True

        except Exception as e:
            logger.error(f"Markdown generation failed: {e}")
            return False

    def _save_results(self) -> bool:
        """Save the generated markdown and ensure images are accessible"""
        try:
            # Create output directory if needed
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save markdown
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(self.generated_markdown)

            logger.info(f"Saved markdown to: {self.output_path}")

            # Verify images directory exists and has content
            if self.extracted_images:
                images_path = Path(self.images_dir)
                if images_path.exists() and any(images_path.iterdir()):
                    logger.info(f"Images saved to: {images_path.absolute()}")
                else:
                    logger.warning("Images directory is empty or missing")

            return True

        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False

    def get_conversion_summary(self) -> str:
        """Get a comprehensive summary of the conversion process"""
        if not self.analysis_results:
            return "No conversion performed yet"

        summary = f"""
PDF to Markdown Conversion Summary
==================================

Input: {self.pdf_path}
Output: {self.output_path}
Images Directory: {self.images_dir}

Document Analysis:
- Total Pages: {self.analysis_results.get("total_pages", 0)}
- Total Text Length: {self.analysis_results.get("total_text_length", 0):,} characters
- Total Images: {self.analysis_results.get("total_images", 0)}
- Dominant Content Type: {self.analysis_results.get("dominant_content_type", "unknown")}
- Extraction Strategy: {self.analysis_results.get("extraction_strategy", "unknown")}

Extraction Results:
- Text Pages Processed: {len(self.extracted_text)}
- Images Extracted: {len(self.extracted_images)}
- Markdown Length: {len(self.generated_markdown):,} characters

Settings:
- Image Quality: {self.quality}
- Output Format: {self.output_format}
- Verbose Mode: {self.verbose}
        """.strip()

        return summary

    def cleanup(self):
        """Clean up resources"""
        if self.analyzer:
            self.analyzer.close_pdf()


def convert_pdf_to_markdown(pdf_path: str, **kwargs) -> bool:
    """
    Convenience function for single PDF conversion

    Args:
        pdf_path: Path to the PDF file
        **kwargs: Additional options (output_path, images_dir, quality, etc.)

    Returns:
        True if conversion successful, False otherwise
    """
    converter = PDFToMarkdownConverter(pdf_path, **kwargs)

    try:
        result = converter.convert()

        if kwargs.get("verbose", False):
            print(converter.get_conversion_summary())

        return result

    finally:
        converter.cleanup()


def batch_convert_pdfs(pdf_paths: List[str], **kwargs) -> Dict[str, bool]:
    """
    Convert multiple PDFs to Markdown

    Args:
        pdf_paths: List of PDF file paths
        **kwargs: Additional options

    Returns:
        Dictionary mapping file paths to conversion success status
    """
    results = {}

    for pdf_path in pdf_paths:
        logger.info(f"Converting {pdf_path}...")

        try:
            # Generate output path for each file
            output_path = Path(pdf_path).with_suffix(".md")
            images_dir = f"images_{Path(pdf_path).stem}"

            converter_kwargs = kwargs.copy()
            converter_kwargs.update(
                {"output_path": str(output_path), "images_dir": images_dir}
            )

            results[pdf_path] = convert_pdf_to_markdown(pdf_path, **converter_kwargs)

        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {e}")
            results[pdf_path] = False

    return results

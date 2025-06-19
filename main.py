#!/usr/bin/env python3
"""
PDF to Markdown Converter - Command Line Interface
"""

import click
import sys
from pathlib import Path
import glob
import logging

# Import our converter
from src.converter import convert_pdf_to_markdown, batch_convert_pdfs

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    "output_path",
    help="Output markdown file path (default: same name as input)",
)
@click.option(
    "-i",
    "--images-dir",
    "images_dir",
    default="images",
    help="Directory for extracted images (default: images)",
)
@click.option("--ocr", "force_ocr", is_flag=True, help="Force OCR for all content")
@click.option("--no-images", "skip_images", is_flag=True, help="Skip image extraction")
@click.option(
    "--quality",
    type=click.Choice(["low", "medium", "high", "original"]),
    default="medium",
    help="Image quality (default: medium)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["standard", "github", "obsidian"]),
    default="standard",
    help="Output format (default: standard)",
)
@click.option(
    "--batch",
    "batch_mode",
    is_flag=True,
    help="Process multiple files (use wildcards in input)",
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed processing information"
)
def main(
    input_file,
    output_path,
    images_dir,
    force_ocr,
    skip_images,
    quality,
    output_format,
    batch_mode,
    verbose,
):
    """
    Convert PDF files to Markdown with intelligent text and image extraction.

    Examples:

    \b
    # Basic conversion
    python main.py document.pdf

    \b
    # With custom output and image directory
    python main.py document.pdf -o report.md -i ./assets

    \b
    # Batch processing
    python main.py "*.pdf" --batch

    \b
    # High quality images, GitHub format
    python main.py document.pdf --quality high --format github
    """

    # Welcome message
    if verbose:
        click.echo("🔄 PDF to Markdown Converter v0.1.0")
        click.echo("=" * 40)

    try:
        if batch_mode:
            # Handle batch processing
            pdf_files = glob.glob(input_file)
            if not pdf_files:
                click.echo(f"❌ No files found matching: {input_file}", err=True)
                sys.exit(1)

            click.echo(f"📁 Found {len(pdf_files)} PDF files to process")

            # Prepare options
            options = {
                "quality": quality,
                "output_format": output_format,
                "verbose": verbose,
            }

            # Process files
            results = batch_convert_pdfs(pdf_files, **options)

            # Report results
            successful = sum(1 for success in results.values() if success)
            failed = len(results) - successful

            click.echo(f"\n📊 Batch conversion complete:")
            click.echo(f"   ✅ Successful: {successful}")
            click.echo(f"   ❌ Failed: {failed}")

            if failed > 0:
                click.echo("\n❌ Failed files:")
                for file_path, success in results.items():
                    if not success:
                        click.echo(f"   - {file_path}")

        else:
            # Single file processing
            input_path = Path(input_file)

            if not input_path.exists():
                click.echo(f"❌ File not found: {input_file}", err=True)
                sys.exit(1)

            if input_path.suffix.lower() != ".pdf":
                click.echo(f"❌ Not a PDF file: {input_file}", err=True)
                sys.exit(1)

            # Determine output path
            if not output_path:
                output_path = str(input_path.with_suffix(".md"))

            # Show processing info
            if verbose:
                click.echo(f"📄 Input: {input_file}")
                click.echo(f"📝 Output: {output_path}")
                click.echo(f"🖼️  Images: {images_dir}")
                click.echo(f"⚙️  Quality: {quality}")
                click.echo(f"📋 Format: {output_format}")
                click.echo()

            # Prepare options
            options = {
                "output_path": output_path,
                "images_dir": images_dir,
                "quality": quality,
                "output_format": output_format,
                "verbose": verbose,
            }

            # Convert
            click.echo(f"🔄 Converting {input_path.name}...")
            success = convert_pdf_to_markdown(str(input_path), **options)

            if success:
                click.echo(f"✅ Conversion successful!")
                click.echo(f"📝 Markdown saved to: {output_path}")

                # Check if images were extracted
                images_path = Path(images_dir)
                if images_path.exists() and any(images_path.iterdir()):
                    image_count = len(list(images_path.glob("*")))
                    click.echo(f"🖼️  {image_count} images saved to: {images_dir}")

            else:
                click.echo(f"❌ Conversion failed!", err=True)
                sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n⏹️  Conversion interrupted by user", err=True)
        sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@click.command()
@click.argument("pdf_file", type=click.Path(exists=True))
def analyze(pdf_file):
    """Analyze a PDF file and show its structure (without conversion)"""

    try:
        from src.pdf_analyzer import PDFAnalyzer

        click.echo(f"🔍 Analyzing {pdf_file}...")

        analyzer = PDFAnalyzer(pdf_file)
        if analyzer.open_pdf():
            results = analyzer.analyze_document()
            click.echo("\n" + analyzer.get_document_summary())
            analyzer.close_pdf()
        else:
            click.echo("❌ Failed to open PDF file", err=True)

    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}", err=True)


# Create a command group for multiple commands
@click.group()
def cli():
    """PDF to Markdown Converter - Convert PDFs to Markdown with image extraction"""
    pass


# Add commands to the group
cli.add_command(main, name="convert")
cli.add_command(analyze)


if __name__ == "__main__":
    # If called directly, run the main convert command
    main()

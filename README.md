# PDF to Markdown Converter

A powerful hybrid PDF to Markdown converter that intelligently extracts text and images from PDFs while preserving document structure and placing images at appropriate locations in the generated Markdown.

## Features

🔄 **Hybrid Extraction**: Combines direct text extraction with OCR fallback for optimal results  
🖼️ **Smart Image Handling**: Extracts images and places them intelligently in the Markdown flow  
📋 **Structure Preservation**: Maintains headers, paragraphs, lists, and document hierarchy  
⚙️ **Multiple Formats**: Supports standard Markdown, GitHub-flavored, and Obsidian formats  
🚀 **Simple CLI**: Single command converts any PDF to clean Markdown  
📦 **Batch Processing**: Convert multiple PDFs at once

## Installation

### Prerequisites

1. **Python 3.8+** required
2. **uv** (modern Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
3. **Tesseract OCR** (optional, for scanned documents)

### Quick Setup with uv

```bash
# Clone the repository
git clone <repository-url>
cd pdf-md-converter

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Alternative: Traditional pip

```bash
pip install -r requirements.txt
```

### Install Tesseract (Optional)

**Windows:**

```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**macOS:**

```bash
brew install tesseract
```

**Linux:**

```bash
sudo apt-get install tesseract-ocr
```

## Quick Start

### Basic Usage

```bash
# Convert a PDF to Markdown
python main.py document.pdf

# This creates:
# - document.md (the markdown file)
# - images/ (directory with extracted images)
```

### Advanced Usage

```bash
# Custom output location
python main.py document.pdf -o report.md -i ./assets

# High quality images, GitHub format
python main.py document.pdf --quality high --format github

# Batch convert all PDFs in a directory
python main.py "*.pdf" --batch

# Verbose output to see detailed processing
python main.py document.pdf --verbose
```

## Command Line Options

```
Usage: python main.py [OPTIONS] INPUT_FILE

Options:
  -o, --output PATH          Output markdown file path
  -i, --images-dir PATH      Directory for extracted images (default: images)
  --quality [low|medium|high|original]  Image quality (default: medium)
  --format [standard|github|obsidian]   Output format (default: standard)
  --batch                    Process multiple files (use wildcards)
  --verbose, -v              Show detailed processing information
  --help                     Show this message and exit
```

## How It Works

### 1. **PDF Analysis**

- Analyzes each page to determine content type (text, image, or mixed)
- Identifies the best extraction strategy for each page
- Detects document structure and layout patterns

### 2. **Hybrid Content Extraction**

- **Text-based pages**: Direct text extraction for clean, searchable content
- **Image-based pages**: OCR processing for scanned documents
- **Mixed pages**: Combines both approaches for optimal results

### 3. **Smart Image Processing**

- Extracts images with original quality
- Optimizes images for web usage (configurable quality)
- Determines optimal placement within text flow
- Generates proper Markdown image references

### 4. **Intelligent Markdown Generation**

- Preserves document hierarchy (headers, paragraphs, lists)
- Places images at logical breakpoints in text flow
- Maintains proper spacing and formatting
- Supports multiple output formats

## Examples

### Input PDF Structure:

```
Page 1: Title + Introduction paragraph + Image + More text
Page 2: Header + Bullet list + Table + Image
```

### Generated Markdown:

```markdown
# Document Title

Introduction paragraph with important information about the topic.

![Image from page 1](images/image_page1_1.jpg)

Additional text content continues here with proper formatting.

---

## Page 2

### Section Header

- First bullet point
- Second bullet point
- Third bullet point

![Image from page 2](images/image_page2_1.jpg)
```

## Output Formats

### Standard Markdown

```markdown
![Alt text](images/image.jpg)
```

### GitHub-Flavored Markdown

```markdown
![Alt text](images/image.jpg)
```

### Obsidian Format

```markdown
![[images/image.jpg]]
```

## Project Structure

```
pdf-md-converter/
├── src/
│   ├── __init__.py
│   ├── pdf_analyzer.py      # PDF analysis and content detection
│   ├── image_extractor.py   # Image extraction and processing
│   ├── text_processor.py    # Text extraction and cleaning
│   ├── markdown_generator.py # Markdown output generation
│   └── converter.py         # Main conversion orchestrator
├── main.py                  # CLI interface
├── requirements.txt
├── PROJECT_PLAN.md
└── README.md
```

## Configuration

### Image Quality Settings

- **low**: 60% quality, max 800x600px
- **medium**: 85% quality, max 1200x900px (default)
- **high**: 95% quality, max 1600x1200px
- **original**: No optimization

### Supported Input Formats

- ✅ **Text-based PDFs**: Direct extraction
- ✅ **Scanned PDFs**: OCR processing
- ✅ **Mixed content PDFs**: Hybrid approach
- ✅ **PDFs with images**: Full image extraction
- ✅ **Multi-page documents**: Batch processing

## Troubleshooting

### Common Issues

**"Import fitz could not be resolved"**

```bash
pip install PyMuPDF
```

**"No text extracted from PDF"**

- PDF might be image-based (scanned)
- Install Tesseract OCR for better results
- Try `--verbose` flag to see processing details

**"Images not appearing in output"**

- Check that `images/` directory was created
- Verify image paths in generated Markdown
- Ensure images directory is in the same location as the Markdown file

**"Poor text quality"**

- Try different extraction methods
- For scanned documents, ensure Tesseract is installed
- Use `--verbose` to see which extraction method is being used

### Performance Tips

- Use `--quality low` for faster processing of large documents
- Use `--batch` for multiple files to process them efficiently
- For very large PDFs, process them in smaller chunks

## Development

### Development Setup

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Or use the development helper script
python scripts/dev.py install
```

### Development Commands

```bash
# Format code
python scripts/dev.py format

# Lint code
python scripts/dev.py lint

# Run tests
python scripts/dev.py test

# Run all checks (format + lint + test)
python scripts/dev.py all

# Clean build artifacts
python scripts/dev.py clean
```

### Manual Commands

```bash
# Format code
black src/ main.py
isort src/ main.py

# Lint code
flake8 src/ main.py
mypy src/ main.py

# Run tests with coverage
pytest --cov=src --cov-report=html
```

### Project Structure

The project uses modern Python tooling:

- **uv**: Fast Python package manager
- **pyproject.toml**: Modern project configuration
- **pytest**: Testing framework with coverage
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Set up development environment: `uv pip install -e ".[dev]"`
4. Make your changes
5. Run tests: `python scripts/dev.py all`
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### v0.1.0 (Phase 1 MVP)

- ✅ Basic PDF text extraction
- ✅ Simple image extraction
- ✅ Basic Markdown generation
- ✅ Command-line interface
- ✅ Hybrid content detection
- ✅ Multiple output formats

### Planned Features (Phase 2)

- [ ] Advanced layout analysis
- [ ] Table extraction and formatting
- [ ] OCR integration for scanned PDFs
- [ ] Caption detection and association
- [ ] Multi-column layout support

# Test Samples Directory

This directory contains sample PDF files for testing the PDF to Markdown converter.

## Adding Test Files

To run integration tests, add PDF files to this directory:

1. **Simple text PDFs**: For testing basic text extraction
2. **PDFs with images**: For testing image extraction and placement
3. **Complex layouts**: For testing advanced layout analysis
4. **Scanned PDFs**: For testing OCR functionality

## File Naming Convention

Use descriptive names that indicate the test purpose:

- `simple_text.pdf` - Basic text-only document
- `with_images.pdf` - Document containing images
- `multi_column.pdf` - Multi-column layout
- `scanned_document.pdf` - Scanned/image-based PDF
- `tables_and_lists.pdf` - Document with tables and lists

## Note

Sample PDF files are gitignored to avoid repository bloat. Add your own test files locally for development and testing.

## Creating Test PDFs

You can create simple test PDFs using:

1. **Online tools**: Various PDF generators
2. **Office software**: Export documents as PDF
3. **Programming**: Use libraries like `reportlab` to generate test PDFs
4. **Scanning**: Create scanned PDFs for OCR testing

Example Python script to create a simple test PDF:

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Test Document")
    c.drawString(100, 700, "This is a simple test PDF for the converter.")
    c.showPage()
    c.save()

create_test_pdf("tests/samples/simple_test.pdf")
```

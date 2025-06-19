# PDF to Markdown Converter - Project Plan

## Overview
Build a hybrid PDF to Markdown converter that intelligently extracts text, preserves images, and maintains document structure with proper image placement in the resulting Markdown.

## Core Objectives
1. **Hybrid Text Extraction**: Combine direct text extraction with OCR for scanned content
2. **Image Preservation**: Extract and save images with proper referencing in Markdown
3. **Layout Understanding**: Maintain document structure (headers, paragraphs, lists, tables)
4. **Smart Image Placement**: Position images correctly within the Markdown flow

## Technical Architecture

### Phase 1: Core Infrastructure
#### 1.1 PDF Analysis Engine
- **Library**: PyMuPDF (fitz) - Best for hybrid text/image extraction
- **Functionality**: 
  - Detect text-based vs image-based content per page
  - Extract text blocks with positioning information
  - Identify image locations and boundaries
  - Determine reading order and layout structure

#### 1.2 Image Processing Pipeline
- **Image Extraction**: Extract images with original quality and format
- **Image Optimization**: Convert to web-friendly formats (PNG/JPEG)
- **Naming Convention**: `image_page{page_num}_{image_num}.{ext}`
- **Storage**: Create `images/` directory alongside output Markdown

#### 1.3 Text Processing Pipeline
- **Direct Text Extraction**: For searchable PDFs
- **OCR Fallback**: Tesseract for scanned content or poor-quality text
- **Text Cleaning**: Remove artifacts, normalize spacing
- **Structure Detection**: Identify headers, paragraphs, lists, tables

### Phase 2: Layout Understanding
#### 2.1 Document Structure Analysis
- **Header Detection**: Font size, weight, positioning patterns
- **Paragraph Segmentation**: Text block analysis
- **List Recognition**: Bullet points, numbering patterns
- **Table Detection**: Grid patterns, cell boundaries

#### 2.2 Image-Text Relationship Mapping
- **Spatial Analysis**: Determine image position relative to text blocks
- **Flow Integration**: Insert images at logical breakpoints
- **Caption Detection**: Identify and associate image captions
- **Reference Handling**: Maintain "Figure X" references

### Phase 3: Markdown Generation
#### 3.1 Content Ordering Engine
- **Reading Flow**: Top-to-bottom, left-to-right processing
- **Image Insertion Points**: 
  - After relevant paragraphs
  - Before/after section breaks
  - Inline for small diagrams
  - Block-level for large images

#### 3.2 Markdown Formatting
- **Headers**: `#`, `##`, `###` based on hierarchy
- **Images**: `![alt-text](images/filename.ext)`
- **Tables**: Markdown table syntax
- **Lists**: Proper bullet/number formatting
- **Code Blocks**: For technical content detection

### Phase 4: Quality Assurance
#### 4.1 Validation System
- **Image Integrity**: Verify all images are extracted and referenced
- **Link Validation**: Ensure all image links are valid
- **Structure Verification**: Check header hierarchy and flow
- **Content Completeness**: Compare input vs output content

#### 4.2 Error Handling
- **Corrupted Images**: Skip with warning, maintain text flow
- **OCR Failures**: Fallback to image-only sections
- **Layout Ambiguity**: Use best-guess positioning with comments

## Implementation Strategy

### Technology Stack
```
Core Libraries:
- PyMuPDF (fitz): PDF processing and image extraction
- Pillow (PIL): Image processing and optimization
- pytesseract: OCR for scanned content
- python-markdown: Markdown generation utilities

Optional Enhancements:
- pdfplumber: Alternative text extraction
- opencv-python: Advanced image processing
- spacy/nltk: Text analysis and structure detection
```

### File Structure
```
pdf-md-converter/
├── src/
│   ├── __init__.py
│   ├── pdf_analyzer.py      # PDF analysis and content detection
│   ├── image_extractor.py   # Image extraction and processing
│   ├── text_processor.py    # Text extraction and cleaning
│   ├── layout_analyzer.py   # Document structure analysis
│   ├── markdown_generator.py # Markdown output generation
│   └── converter.py         # Main conversion orchestrator
├── tests/
│   ├── test_samples/        # Sample PDFs for testing
│   └── test_*.py           # Unit tests
├── requirements.txt
├── README.md
└── main.py                 # CLI interface
```

### Development Phases

#### Phase 1: MVP (Minimum Viable Product)
- [x] Basic PDF text extraction
- [ ] Simple image extraction
- [ ] Basic Markdown generation
- [ ] Command-line interface

#### Phase 2: Layout Intelligence
- [ ] Document structure detection
- [ ] Smart image placement
- [ ] Table extraction
- [ ] Header hierarchy detection

#### Phase 3: Advanced Features
- [ ] OCR integration for scanned PDFs
- [ ] Caption detection and association
- [ ] Multi-column layout handling
- [ ] Batch processing capabilities

#### Phase 4: Polish & Optimization
- [ ] Performance optimization
- [ ] Error handling improvements
- [ ] Configuration options
- [ ] Documentation and examples

## Key Algorithms

### 1. Hybrid Content Detection
```python
def analyze_page_content(page):
    """
    Determine if page content is text-based or image-based
    Returns: 'text', 'image', or 'mixed'
    """
    text_blocks = page.get_text_blocks()
    images = page.get_images()
    
    if len(text_blocks) > threshold and text_quality_good(text_blocks):
        return 'text'
    elif len(images) > 0 and text_quality_poor(text_blocks):
        return 'image'
    else:
        return 'mixed'
```

### 2. Image Placement Algorithm
```python
def determine_image_placement(text_blocks, image_bbox):
    """
    Find optimal insertion point for image in text flow
    Returns: insertion_index, placement_type
    """
    # Analyze spatial relationships
    # Find logical breakpoints
    # Maintain reading flow
    # Return optimal placement
```

### 3. Structure Detection
```python
def detect_document_structure(text_blocks):
    """
    Identify headers, paragraphs, lists, tables
    Returns: structured_content
    """
    # Font analysis for headers
    # Indentation patterns for lists
    # Grid detection for tables
    # Spacing analysis for paragraphs
```

## Success Metrics
1. **Accuracy**: >95% text extraction accuracy
2. **Completeness**: All images extracted and properly placed
3. **Structure**: Maintains logical document flow
4. **Usability**: Simple CLI interface with clear options
5. **Performance**: Processes typical PDFs in <30 seconds

## Risk Mitigation
- **Complex Layouts**: Fallback to best-effort positioning
- **Poor OCR**: Provide image-only sections with warnings
- **Large Files**: Implement streaming and progress indicators
- **Memory Issues**: Process pages individually, cleanup resources

## Future Enhancements
- Web interface for easier usage
- API endpoints for integration
- Support for additional output formats (HTML, DOCX)
- AI-powered layout understanding
- Batch processing with parallel execution
- Custom styling and formatting options

---

## CLI Interface Design

### Single Command Usage
```bash
# Basic conversion
pdf2md document.pdf

# With options
pdf2md document.pdf --output report.md --images-dir ./assets

# Batch processing
pdf2md *.pdf --batch

# Advanced options
pdf2md document.pdf --ocr --quality high --format github
```

### Command Structure
```
pdf2md [INPUT_FILE] [OPTIONS]

Arguments:
  INPUT_FILE    Path to PDF file to convert

Options:
  -o, --output     Output markdown file (default: same name as input)
  -i, --images-dir Directory for extracted images (default: ./images)
  --ocr           Force OCR for all content
  --no-images     Skip image extraction
  --quality       Image quality: low|medium|high (default: medium)
  --format        Output format: standard|github|obsidian (default: standard)
  --batch         Process multiple files
  --verbose       Show detailed processing information
  --help          Show help message
```

### Installation
```bash
# Install via pip (future)
pip install pdf2md

# Or run directly
python main.py document.pdf
```

## Next Steps
1. Set up development environment
2. Implement Phase 1 MVP with CLI interface
3. Test with sample PDFs
4. Iterate based on results
5. Expand to Phase 2 features 
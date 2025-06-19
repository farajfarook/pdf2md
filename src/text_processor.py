"""
Text Processor - Extracts and processes text from PDF pages
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple, Any
import logging
from PIL import Image
import io

# OCR support (optional)
try:
    import pytesseract

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None

logger = logging.getLogger(__name__)


class TextProcessor:
    """Processes and extracts text from PDF documents"""

    def __init__(self, pdf_doc: fitz.Document):
        self.doc = pdf_doc
        self.extracted_text = {}
        self.text_blocks = {}

    def extract_page_text_ocr(self, page_num: int) -> Dict[str, Any]:
        """
        Extract text using OCR from a page rendered as image
        """
        if not OCR_AVAILABLE:
            logger.warning("OCR not available - pytesseract not installed")
            return {
                "page_num": page_num,
                "raw_text": "",
                "cleaned_text": "",
                "extraction_method": "ocr_unavailable",
                "text_length": 0,
                "line_count": 0,
            }

        if page_num >= len(self.doc):
            return {}

        try:
            page = self.doc[page_num]

            # Render page as image
            mat = fitz.Matrix(2.0, 2.0)  # Higher resolution for better OCR
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))

            # Perform OCR
            ocr_text = pytesseract.image_to_string(pil_image, lang="eng")

            # Clean the OCR text
            cleaned_text = self._clean_text(ocr_text)

            page_text_info = {
                "page_num": page_num,
                "raw_text": ocr_text,
                "cleaned_text": cleaned_text,
                "text_blocks": [],  # OCR doesn't provide block structure
                "extraction_method": "ocr",
                "text_length": len(cleaned_text),
                "line_count": len(cleaned_text.split("\n")) if cleaned_text else 0,
            }

            self.extracted_text[page_num] = page_text_info
            return page_text_info

        except Exception as e:
            logger.error(f"OCR extraction failed for page {page_num}: {e}")
            return {
                "page_num": page_num,
                "raw_text": "",
                "cleaned_text": "",
                "extraction_method": "ocr_failed",
                "text_length": 0,
                "line_count": 0,
            }

    def extract_page_text(self, page_num: int, method: str = "auto") -> Dict[str, Any]:
        """
        Extract text from a specific page
        method: 'auto', 'direct', 'blocks', 'dict'
        """
        if page_num >= len(self.doc):
            return {}

        page = self.doc[page_num]

        # Extract text using different methods based on content type
        if method == "auto":
            # Try direct text first
            text_content = page.get_text().strip()
            if len(text_content) > 50:  # Has meaningful text
                method = "blocks"
            else:
                method = "dict"  # For better structure analysis

        if method == "direct":
            text_content = page.get_text()
            text_blocks = []
        elif method == "blocks":
            text_blocks = page.get_text("blocks")
            text_content = "\n".join(
                [block[4] for block in text_blocks if len(block) > 4]
            )
        elif method == "dict":
            text_dict = page.get_text("dict")
            text_content, text_blocks = self._process_text_dict(text_dict)
        else:
            text_content = page.get_text()
            text_blocks = []

        # Clean and process text
        cleaned_text = self._clean_text(text_content)

        page_text_info = {
            "page_num": page_num,
            "raw_text": text_content,
            "cleaned_text": cleaned_text,
            "text_blocks": text_blocks,
            "extraction_method": method,
            "text_length": len(cleaned_text),
            "line_count": len(cleaned_text.split("\n")) if cleaned_text else 0,
        }

        self.extracted_text[page_num] = page_text_info
        return page_text_info

    def _process_text_dict(self, text_dict: Dict) -> Tuple[str, List[Dict]]:
        """Process text dictionary format to extract structured text"""
        text_parts = []
        text_blocks = []

        for block in text_dict.get("blocks", []):
            if "lines" in block:  # Text block
                block_text = ""
                block_info = {
                    "bbox": block.get("bbox", [0, 0, 0, 0]),
                    "type": "text",
                    "lines": [],
                }

                for line in block["lines"]:
                    line_text = ""
                    line_info = {"bbox": line.get("bbox", [0, 0, 0, 0]), "spans": []}

                    for span in line.get("spans", []):
                        span_text = span.get("text", "")
                        line_text += span_text

                        span_info = {
                            "text": span_text,
                            "bbox": span.get("bbox", [0, 0, 0, 0]),
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                            "flags": span.get("flags", 0),
                        }
                        line_info["spans"].append(span_info)

                    if line_text.strip():
                        block_text += line_text + "\n"
                        line_info["text"] = line_text
                        block_info["lines"].append(line_info)

                if block_text.strip():
                    text_parts.append(block_text.strip())
                    block_info["text"] = block_text.strip()
                    text_blocks.append(block_info)

        return "\n\n".join(text_parts), text_blocks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Fix common PDF extraction issues
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # Add space between camelCase
        text = re.sub(r"(\.)([A-Z])", r"\1 \2", text)  # Add space after periods
        text = re.sub(
            r"([a-z])(\d)", r"\1 \2", text
        )  # Add space between letters and numbers
        text = re.sub(
            r"(\d)([a-z])", r"\1 \2", text
        )  # Add space between numbers and letters

        # Remove control characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

        # Normalize line breaks
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\r", "\n", text)

        # Remove excessive empty lines
        text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)

        return text.strip()

    def extract_all_text(self) -> Dict[int, Dict[str, Any]]:
        """Extract text from all pages"""
        logger.info(f"Extracting text from {len(self.doc)} pages...")

        for page_num in range(len(self.doc)):
            self.extract_page_text(page_num)

        total_text_length = sum(
            info["text_length"] for info in self.extracted_text.values()
        )
        logger.info(f"Extracted {total_text_length} characters of text")

        return self.extracted_text

    def get_page_text(self, page_num: int) -> str:
        """Get cleaned text for a specific page"""
        if page_num in self.extracted_text:
            return self.extracted_text[page_num]["cleaned_text"]
        else:
            page_info = self.extract_page_text(page_num)
            return page_info["cleaned_text"]

    def detect_headers(self, page_num: int) -> List[Dict[str, Any]]:
        """Detect headers in page text based on font size and formatting"""
        if page_num not in self.extracted_text:
            self.extract_page_text(page_num, method="dict")

        page_info = self.extracted_text[page_num]
        text_blocks = page_info.get("text_blocks", [])

        headers = []

        for block in text_blocks:
            if block.get("type") == "text":
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font_size = span.get("size", 0)
                        font_flags = span.get("flags", 0)
                        text = span.get("text", "").strip()

                        # Detect headers based on font size and formatting
                        is_bold = font_flags & 2**4  # Bold flag
                        is_large = font_size > 12
                        is_short = len(text.split()) < 10

                        if (is_bold and is_large) or (is_large and is_short):
                            header_level = self._determine_header_level(font_size)
                            headers.append(
                                {
                                    "text": text,
                                    "level": header_level,
                                    "font_size": font_size,
                                    "is_bold": is_bold,
                                    "bbox": span.get("bbox", [0, 0, 0, 0]),
                                }
                            )

        return headers

    def _determine_header_level(self, font_size: float) -> int:
        """Determine header level based on font size"""
        if font_size >= 20:
            return 1
        elif font_size >= 16:
            return 2
        elif font_size >= 14:
            return 3
        else:
            return 4

    def get_text_structure(self, page_num: int) -> Dict[str, Any]:
        """Analyze text structure for a page"""
        headers = self.detect_headers(page_num)
        page_text = self.get_page_text(page_num)

        # Basic structure analysis
        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
        lines = [l.strip() for l in page_text.split("\n") if l.strip()]

        # Detect lists
        list_items = []
        for line in lines:
            if re.match(r"^\s*[-•*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
                list_items.append(line)

        return {
            "page_num": page_num,
            "headers": headers,
            "paragraphs": paragraphs,
            "lines": lines,
            "list_items": list_items,
            "paragraph_count": len(paragraphs),
            "line_count": len(lines),
            "list_count": len(list_items),
        }

    def get_extraction_summary(self) -> str:
        """Get a summary of text extraction"""
        if not self.extracted_text:
            return "No text extracted"

        total_pages = len(self.extracted_text)
        total_chars = sum(info["text_length"] for info in self.extracted_text.values())
        total_lines = sum(info["line_count"] for info in self.extracted_text.values())

        summary = f"""
Text Extraction Summary:
- Pages processed: {total_pages}
- Total characters: {total_chars:,}
- Total lines: {total_lines:,}
- Average chars per page: {total_chars // total_pages if total_pages > 0 else 0:,}

Pages by text length:
"""

        for page_num, info in sorted(self.extracted_text.items()):
            summary += f"- Page {page_num + 1}: {info['text_length']:,} characters\n"

        return summary.strip()

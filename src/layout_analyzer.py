"""
Layout Analyzer - Analyzes document structure and layout patterns
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class LayoutAnalyzer:
    """Analyzes document layout and structure patterns"""

    def __init__(self, pdf_doc: fitz.Document):
        self.doc = pdf_doc
        self.layout_analysis = {}
        self.font_statistics = {}

    def analyze_page_layout(self, page_num: int) -> Dict[str, Any]:
        """
        Analyze layout structure of a single page
        Returns: Dictionary with layout analysis results
        """
        if page_num >= len(self.doc):
            return {}

        page = self.doc[page_num]

        # Get text with detailed formatting information
        text_dict = page.get_text("dict")

        # Analyze font usage and hierarchy
        font_analysis = self._analyze_fonts(text_dict)

        # Detect structural elements
        headers = self._detect_headers(text_dict, font_analysis)
        paragraphs = self._detect_paragraphs(text_dict)
        lists = self._detect_lists(text_dict)
        tables = self._detect_tables(text_dict)

        # Analyze spatial layout
        reading_order = self._determine_reading_order(text_dict)
        columns = self._detect_columns(text_dict)

        layout_info = {
            "page_num": page_num,
            "font_analysis": font_analysis,
            "headers": headers,
            "paragraphs": paragraphs,
            "lists": lists,
            "tables": tables,
            "reading_order": reading_order,
            "columns": columns,
            "page_bbox": page.rect,
        }

        self.layout_analysis[page_num] = layout_info
        return layout_info

    def _analyze_fonts(self, text_dict: Dict) -> Dict[str, Any]:
        """Analyze font usage patterns to understand document hierarchy"""
        fonts = {}
        font_sizes = []

        for block in text_dict.get("blocks", []):
            if "lines" in block:  # Text block
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        font_name = span.get("font", "")
                        font_size = span.get("size", 0)
                        font_flags = span.get("flags", 0)
                        text_length = len(span.get("text", ""))

                        # Track font statistics
                        font_key = f"{font_name}_{font_size}_{font_flags}"
                        if font_key not in fonts:
                            fonts[font_key] = {
                                "font": font_name,
                                "size": font_size,
                                "flags": font_flags,
                                "is_bold": bool(font_flags & 2**4),
                                "is_italic": bool(font_flags & 2**1),
                                "usage_count": 0,
                                "total_chars": 0,
                            }

                        fonts[font_key]["usage_count"] += 1
                        fonts[font_key]["total_chars"] += text_length
                        font_sizes.append(font_size)

        # Determine font hierarchy
        if font_sizes:
            avg_font_size = sum(font_sizes) / len(font_sizes)
            max_font_size = max(font_sizes)
            min_font_size = min(font_sizes)
        else:
            avg_font_size = max_font_size = min_font_size = 12

        # Find most common font (likely body text)
        body_font = (
            max(fonts.values(), key=lambda x: x["total_chars"]) if fonts else None
        )

        return {
            "fonts": fonts,
            "avg_font_size": avg_font_size,
            "max_font_size": max_font_size,
            "min_font_size": min_font_size,
            "body_font": body_font,
            "font_count": len(fonts),
        }

    def _detect_headers(
        self, text_dict: Dict, font_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """Detect headers based on font size, weight, and positioning"""
        headers = []
        body_font_size = font_analysis.get("body_font", {}).get("size", 12)

        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    line_fonts = []

                    for span in line.get("spans", []):
                        span_text = span.get("text", "").strip()
                        if span_text:
                            line_text += span_text + " "
                            line_fonts.append(
                                {
                                    "size": span.get("size", 0),
                                    "flags": span.get("flags", 0),
                                    "font": span.get("font", ""),
                                }
                            )

                    line_text = line_text.strip()

                    # Header detection heuristics
                    if line_text and line_fonts:
                        avg_size = sum(f["size"] for f in line_fonts) / len(line_fonts)
                        is_bold = any(f["flags"] & 2**4 for f in line_fonts)

                        # Check if it's likely a header
                        is_larger = avg_size > body_font_size * 1.1
                        is_short = len(line_text.split()) <= 10
                        is_title_case = line_text.istitle() or line_text.isupper()
                        starts_with_number = re.match(r"^\d+\.?\s+", line_text)

                        if (
                            (is_larger and is_short)
                            or (is_bold and is_short)
                            or starts_with_number
                        ):
                            header_level = self._determine_header_level(
                                avg_size, body_font_size, is_bold
                            )

                            headers.append(
                                {
                                    "text": line_text,
                                    "level": header_level,
                                    "font_size": avg_size,
                                    "is_bold": is_bold,
                                    "bbox": line.get("bbox", [0, 0, 0, 0]),
                                    "confidence": self._calculate_header_confidence(
                                        avg_size,
                                        body_font_size,
                                        is_bold,
                                        is_short,
                                        is_title_case,
                                    ),
                                }
                            )

        return headers

    def _determine_header_level(
        self, font_size: float, body_size: float, is_bold: bool
    ) -> int:
        """Determine header level based on font size relative to body text"""
        size_ratio = font_size / body_size if body_size > 0 else 1

        if size_ratio >= 1.8:
            return 1  # H1
        elif size_ratio >= 1.5:
            return 2  # H2
        elif size_ratio >= 1.2 or is_bold:
            return 3  # H3
        else:
            return 4  # H4

    def _calculate_header_confidence(
        self,
        font_size: float,
        body_size: float,
        is_bold: bool,
        is_short: bool,
        is_title_case: bool,
    ) -> float:
        """Calculate confidence score for header detection"""
        confidence = 0.0

        size_ratio = font_size / body_size if body_size > 0 else 1
        if size_ratio > 1.1:
            confidence += 0.3

        if is_bold:
            confidence += 0.3

        if is_short:
            confidence += 0.2

        if is_title_case:
            confidence += 0.2

        return min(confidence, 1.0)

    def _detect_paragraphs(self, text_dict: Dict) -> List[Dict[str, Any]]:
        """Detect paragraph boundaries and structure"""
        paragraphs = []

        for block in text_dict.get("blocks", []):
            if "lines" in block:
                block_text = ""
                block_bbox = block.get("bbox", [0, 0, 0, 0])

                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")

                    if line_text.strip():
                        block_text += line_text + "\n"

                if block_text.strip():
                    paragraphs.append(
                        {
                            "text": block_text.strip(),
                            "bbox": block_bbox,
                            "line_count": len(
                                [l for l in block_text.split("\n") if l.strip()]
                            ),
                            "word_count": len(block_text.split()),
                        }
                    )

        return paragraphs

    def _detect_lists(self, text_dict: Dict) -> List[Dict[str, Any]]:
        """Detect list structures (bulleted and numbered)"""
        lists = []
        current_list = None

        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")

                    line_text = line_text.strip()

                    # Check for list patterns
                    bullet_match = re.match(r"^[-•*]\s+(.+)", line_text)
                    number_match = re.match(r"^(\d+)\.?\s+(.+)", line_text)
                    letter_match = re.match(r"^([a-zA-Z])\.?\s+(.+)", line_text)

                    if bullet_match or number_match or letter_match:
                        if current_list is None:
                            current_list = {
                                "type": "bullet" if bullet_match else "numbered",
                                "items": [],
                                "bbox": line.get("bbox", [0, 0, 0, 0]),
                            }

                        item_text = (
                            bullet_match or number_match or letter_match
                        ).group(-1)
                        current_list["items"].append(
                            {
                                "text": item_text,
                                "original": line_text,
                                "bbox": line.get("bbox", [0, 0, 0, 0]),
                            }
                        )
                    else:
                        # End of list
                        if current_list and len(current_list["items"]) > 0:
                            lists.append(current_list)
                            current_list = None

        # Don't forget the last list
        if current_list and len(current_list["items"]) > 0:
            lists.append(current_list)

        return lists

    def _detect_tables(self, text_dict: Dict) -> List[Dict[str, Any]]:
        """Basic table detection based on text alignment patterns"""
        # This is a simplified table detection
        # More sophisticated detection would require analyzing spacing and alignment
        tables = []

        # Look for patterns that might indicate tables
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                lines_with_tabs = []
                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")

                    # Simple heuristic: multiple spaces or tabs might indicate table structure
                    if (
                        re.search(r"\s{3,}|\t", line_text)
                        and len(line_text.split()) >= 2
                    ):
                        lines_with_tabs.append(
                            {"text": line_text, "bbox": line.get("bbox", [0, 0, 0, 0])}
                        )

                if (
                    len(lines_with_tabs) >= 2
                ):  # At least 2 rows to be considered a table
                    tables.append(
                        {
                            "rows": lines_with_tabs,
                            "bbox": block.get("bbox", [0, 0, 0, 0]),
                            "confidence": 0.5,  # Low confidence for this simple detection
                        }
                    )

        return tables

    def _determine_reading_order(self, text_dict: Dict) -> List[Dict[str, Any]]:
        """Determine the reading order of text blocks"""
        blocks = []

        for block in text_dict.get("blocks", []):
            if "lines" in block:
                bbox = block.get("bbox", [0, 0, 0, 0])
                blocks.append(
                    {"bbox": bbox, "y_top": bbox[1], "x_left": bbox[0], "block": block}
                )

        # Sort by Y position (top to bottom), then X position (left to right)
        blocks.sort(key=lambda b: (b["y_top"], b["x_left"]))

        return [{"bbox": b["bbox"], "order": i} for i, b in enumerate(blocks)]

    def _detect_columns(self, text_dict: Dict) -> Dict[str, Any]:
        """Detect multi-column layout"""
        blocks = []

        for block in text_dict.get("blocks", []):
            if "lines" in block:
                bbox = block.get("bbox", [0, 0, 0, 0])
                blocks.append(
                    {
                        "bbox": bbox,
                        "x_center": (bbox[0] + bbox[2]) / 2,
                        "width": bbox[2] - bbox[0],
                    }
                )

        if not blocks:
            return {"column_count": 1, "columns": []}

        # Simple column detection based on X positions
        x_centers = [b["x_center"] for b in blocks]

        # If there are distinct groups of X centers, we might have columns
        # This is a very basic implementation
        column_count = 1
        if len(set(int(x) for x in x_centers)) > 1:
            # More sophisticated column detection would be needed here
            column_count = min(2, len(set(int(x / 50) for x in x_centers)))

        return {
            "column_count": column_count,
            "columns": [],  # Would need more sophisticated analysis
            "is_multi_column": column_count > 1,
        }

    def get_document_structure(self) -> Dict[str, Any]:
        """Get overall document structure analysis"""
        if not self.layout_analysis:
            # Analyze all pages if not done yet
            for page_num in range(len(self.doc)):
                self.analyze_page_layout(page_num)

        # Aggregate statistics
        total_headers = sum(
            len(analysis.get("headers", []))
            for analysis in self.layout_analysis.values()
        )
        total_paragraphs = sum(
            len(analysis.get("paragraphs", []))
            for analysis in self.layout_analysis.values()
        )
        total_lists = sum(
            len(analysis.get("lists", [])) for analysis in self.layout_analysis.values()
        )
        total_tables = sum(
            len(analysis.get("tables", []))
            for analysis in self.layout_analysis.values()
        )

        multi_column_pages = sum(
            1
            for analysis in self.layout_analysis.values()
            if analysis.get("columns", {}).get("is_multi_column", False)
        )

        return {
            "total_pages": len(self.layout_analysis),
            "total_headers": total_headers,
            "total_paragraphs": total_paragraphs,
            "total_lists": total_lists,
            "total_tables": total_tables,
            "multi_column_pages": multi_column_pages,
            "page_analyses": self.layout_analysis,
        }

    def get_analysis_summary(self) -> str:
        """Get a human-readable summary of the layout analysis"""
        structure = self.get_document_structure()

        summary = f"""
Layout Analysis Summary:
- Total Pages: {structure["total_pages"]}
- Headers: {structure["total_headers"]}
- Paragraphs: {structure["total_paragraphs"]}
- Lists: {structure["total_lists"]}
- Tables: {structure["total_tables"]}
- Multi-column Pages: {structure["multi_column_pages"]}

Page-by-page breakdown:
"""

        for page_num, analysis in structure["page_analyses"].items():
            headers = len(analysis.get("headers", []))
            paragraphs = len(analysis.get("paragraphs", []))
            lists = len(analysis.get("lists", []))
            tables = len(analysis.get("tables", []))

            summary += f"- Page {page_num + 1}: {headers}H, {paragraphs}P, {lists}L, {tables}T\n"

        return summary.strip()

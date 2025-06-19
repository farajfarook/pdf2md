"""
Markdown Generator - Combines text and images into properly formatted Markdown
"""

import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Generates Markdown from extracted text and images"""

    def __init__(
        self,
        text_data: Dict[int, Dict],
        image_data: List[Dict],
        output_format: str = "standard",
    ):
        self.text_data = text_data
        self.image_data = image_data
        self.output_format = output_format
        self.markdown_content = []

        # Group images by page for easier processing
        self.images_by_page = {}
        for img in image_data:
            page_num = img["page_num"]
            if page_num not in self.images_by_page:
                self.images_by_page[page_num] = []
            self.images_by_page[page_num].append(img)

    def generate_markdown(self) -> str:
        """Generate complete Markdown document"""
        logger.info("Generating Markdown content...")

        self.markdown_content = []

        # Process each page
        for page_num in sorted(self.text_data.keys()):
            page_markdown = self._process_page(page_num)
            if page_markdown.strip():
                self.markdown_content.append(page_markdown)

        # Join all content
        full_markdown = "\n\n---\n\n".join(self.markdown_content)

        # Post-process the markdown
        full_markdown = self._post_process_markdown(full_markdown)

        logger.info(f"Generated {len(full_markdown)} characters of Markdown")
        return full_markdown

    def _process_page(self, page_num: int) -> str:
        """Process a single page and generate its Markdown"""
        page_text_info = self.text_data.get(page_num, {})
        page_images = self.images_by_page.get(page_num, [])

        # Get text structure
        page_text = page_text_info.get("cleaned_text", "")
        if not page_text.strip():
            # If no text, just add images
            return self._generate_images_markdown(page_images)

        # Process text structure
        text_structure = self._analyze_text_structure(page_text)

        # Generate markdown with intelligent image placement
        page_markdown = self._generate_page_markdown(
            text_structure, page_images, page_num
        )

        return page_markdown

    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure to identify components"""
        lines = text.split("\n")

        structure = {"headers": [], "paragraphs": [], "lists": [], "other": []}

        current_paragraph = []
        current_list = []
        in_list = False

        for line in lines:
            line = line.strip()
            if not line:
                # Empty line - end current paragraph or list
                if current_paragraph:
                    structure["paragraphs"].append("\n".join(current_paragraph))
                    current_paragraph = []
                if current_list:
                    structure["lists"].append(current_list)
                    current_list = []
                    in_list = False
                continue

            # Check if it's a header (simple heuristic)
            if self._is_likely_header(line):
                # End current paragraph/list
                if current_paragraph:
                    structure["paragraphs"].append("\n".join(current_paragraph))
                    current_paragraph = []
                if current_list:
                    structure["lists"].append(current_list)
                    current_list = []
                    in_list = False

                structure["headers"].append(line)

            # Check if it's a list item
            elif self._is_list_item(line):
                # End current paragraph
                if current_paragraph:
                    structure["paragraphs"].append("\n".join(current_paragraph))
                    current_paragraph = []

                current_list.append(line)
                in_list = True

            else:
                # Regular text
                if in_list:
                    # End current list
                    structure["lists"].append(current_list)
                    current_list = []
                    in_list = False

                current_paragraph.append(line)

        # Handle remaining content
        if current_paragraph:
            structure["paragraphs"].append("\n".join(current_paragraph))
        if current_list:
            structure["lists"].append(current_list)

        return structure

    def _is_likely_header(self, line: str) -> bool:
        """Determine if a line is likely a header"""
        # Simple heuristics for header detection
        if len(line) > 100:  # Too long to be a header
            return False

        # Check for common header patterns
        if re.match(r"^\d+\.?\s+[A-Z]", line):  # "1. Introduction" or "1 Introduction"
            return True

        if re.match(r"^[A-Z][A-Z\s]+$", line):  # ALL CAPS
            return True

        if (
            re.match(r"^[A-Z].*[^.!?]$", line) and len(line.split()) <= 8
        ):  # Short, starts with capital, no ending punctuation
            return True

        return False

    def _is_list_item(self, line: str) -> bool:
        """Determine if a line is a list item"""
        # Bullet points
        if re.match(r"^\s*[-•*]\s+", line):
            return True

        # Numbered lists
        if re.match(r"^\s*\d+\.\s+", line):
            return True

        # Lettered lists
        if re.match(r"^\s*[a-zA-Z]\.\s+", line):
            return True

        return False

    def _generate_page_markdown(
        self, text_structure: Dict, images: List[Dict], page_num: int
    ) -> str:
        """Generate markdown for a page with intelligent image placement"""
        markdown_parts = []

        # Add page header if multiple pages
        if len(self.text_data) > 1:
            markdown_parts.append(f"## Page {page_num + 1}")

        # Process structure elements
        all_elements = []

        # Add headers
        for header in text_structure["headers"]:
            header_level = self._determine_header_level(header)
            all_elements.append(
                {
                    "type": "header",
                    "content": f"{'#' * header_level} {header}",
                    "original": header,
                }
            )

        # Add paragraphs
        for paragraph in text_structure["paragraphs"]:
            all_elements.append(
                {"type": "paragraph", "content": paragraph, "original": paragraph}
            )

        # Add lists
        for list_items in text_structure["lists"]:
            list_markdown = self._format_list(list_items)
            all_elements.append(
                {"type": "list", "content": list_markdown, "original": list_items}
            )

        # Insert images at appropriate points
        if images:
            # Simple strategy: add images after first paragraph or at the end
            if len(all_elements) > 1:
                # Insert after first element
                insert_point = 1
            else:
                # Add at the end
                insert_point = len(all_elements)

            images_markdown = self._generate_images_markdown(images)
            all_elements.insert(
                insert_point,
                {"type": "images", "content": images_markdown, "original": images},
            )

        # Combine all elements
        for element in all_elements:
            markdown_parts.append(element["content"])

        return "\n\n".join(markdown_parts)

    def _determine_header_level(self, header: str) -> int:
        """Determine appropriate header level"""
        # Simple heuristic based on content
        if re.match(r"^\d+\.?\s+", header):  # Numbered section
            return 2
        elif len(header.split()) <= 3:  # Short headers
            return 3
        else:
            return 4

    def _format_list(self, list_items: List[str]) -> str:
        """Format list items as Markdown"""
        formatted_items = []

        for item in list_items:
            # Clean up the item
            item = item.strip()

            # Convert to markdown format
            if re.match(r"^\s*[-•*]\s+", item):
                # Already bullet format, just clean up
                item = re.sub(r"^\s*[-•*]\s+", "- ", item)
            elif re.match(r"^\s*\d+\.\s+", item):
                # Numbered list - keep as is
                pass
            else:
                # Add bullet point
                item = f"- {item}"

            formatted_items.append(item)

        return "\n".join(formatted_items)

    def _generate_images_markdown(self, images: List[Dict]) -> str:
        """Generate Markdown for images"""
        if not images:
            return ""

        image_parts = []

        for img in images:
            filename = img["filename"]
            relative_path = img["relative_path"]

            # Generate alt text
            alt_text = f"Image from page {img['page_num'] + 1}"

            # Create markdown image reference
            if self.output_format == "obsidian":
                # Obsidian format
                image_md = f"![[{relative_path}]]"
            else:
                # Standard markdown
                image_md = f"![{alt_text}]({relative_path})"

            image_parts.append(image_md)

        return "\n\n".join(image_parts)

    def _post_process_markdown(self, markdown: str) -> str:
        """Post-process the generated markdown"""
        # Remove excessive empty lines
        markdown = re.sub(r"\n\s*\n\s*\n", "\n\n", markdown)

        # Fix spacing around headers
        markdown = re.sub(r"\n(#{1,6}\s)", r"\n\n\1", markdown)
        markdown = re.sub(r"(#{1,6}.*)\n([^#\n])", r"\1\n\n\2", markdown)

        # Ensure proper spacing around images
        markdown = re.sub(r"([^\n])\n(!\[.*?\]\(.*?\))", r"\1\n\n\2", markdown)
        markdown = re.sub(r"(!\[.*?\]\(.*?\))\n([^\n])", r"\1\n\n\2", markdown)

        # Clean up list formatting
        markdown = re.sub(r"\n(-\s+.*?)\n([^-\n])", r"\n\1\n\n\2", markdown)

        return markdown.strip()

    def save_markdown(self, output_path: str) -> bool:
        """Save generated markdown to file"""
        try:
            markdown_content = self.generate_markdown()

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"Saved markdown to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save markdown: {e}")
            return False

    def get_generation_summary(self) -> str:
        """Get a summary of the markdown generation"""
        total_pages = len(self.text_data)
        total_images = len(self.image_data)

        # Count elements
        total_headers = 0
        total_paragraphs = 0
        total_lists = 0

        for page_num, page_data in self.text_data.items():
            text = page_data.get("cleaned_text", "")
            structure = self._analyze_text_structure(text)
            total_headers += len(structure["headers"])
            total_paragraphs += len(structure["paragraphs"])
            total_lists += len(structure["lists"])

        summary = f"""
Markdown Generation Summary:
- Pages processed: {total_pages}
- Images included: {total_images}
- Headers detected: {total_headers}
- Paragraphs: {total_paragraphs}
- Lists: {total_lists}
- Output format: {self.output_format}

Images by page:
"""

        for page_num in sorted(self.images_by_page.keys()):
            images = self.images_by_page[page_num]
            summary += f"- Page {page_num + 1}: {len(images)} images\n"

        return summary.strip()

"""
Image Extractor - Extracts and processes images from PDF pages
"""

import fitz  # PyMuPDF
from PIL import Image
import os
from pathlib import Path
from typing import List, Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extracts and processes images from PDF documents"""

    def __init__(self, pdf_doc: fitz.Document, output_dir: str = "images"):
        self.doc = pdf_doc
        self.output_dir = Path(output_dir)
        self.extracted_images = []
        self.image_references = {}  # Maps image info to file paths

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

    def extract_page_images(self, page_num: int) -> List[Dict[str, Any]]:
        """
        Extract all images from a specific page
        Returns: List of image info dictionaries
        """
        if page_num >= len(self.doc):
            return []

        page = self.doc[page_num]
        image_list = page.get_images()
        extracted_images = []

        logger.info(f"Extracting {len(image_list)} images from page {page_num + 1}")

        for img_index, img in enumerate(image_list):
            try:
                # Get image info
                xref = img[0]  # Image reference number
                pix = fitz.Pixmap(self.doc, xref)

                # Skip if image is too small (likely artifacts)
                if pix.width < 50 or pix.height < 50:
                    logger.debug(f"Skipping small image: {pix.width}x{pix.height}")
                    pix = None
                    continue

                # Generate filename
                filename = f"image_page{page_num + 1}_{img_index + 1}"

                # Determine format and save
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    if pix.n == 1:  # Grayscale
                        filename += ".png"
                    else:  # RGB
                        filename += ".jpg"

                    filepath = self.output_dir / filename

                    # Save image
                    if pix.n - pix.alpha == 1:  # Grayscale
                        pix.save(str(filepath))
                    else:  # RGB
                        # Convert to PIL Image for better compression
                        img_data = pix.tobytes("ppm")
                        pil_img = Image.open(io.BytesIO(img_data))
                        pil_img.save(str(filepath), "JPEG", quality=85, optimize=True)

                    # Get image position on page
                    img_rect = (
                        page.get_image_rects(xref)[0]
                        if page.get_image_rects(xref)
                        else fitz.Rect(0, 0, 0, 0)
                    )

                    image_info = {
                        "filename": filename,
                        "filepath": str(filepath),
                        "page_num": page_num,
                        "img_index": img_index,
                        "xref": xref,
                        "width": pix.width,
                        "height": pix.height,
                        "bbox": img_rect,
                        "relative_path": f"images/{filename}",
                    }

                    extracted_images.append(image_info)
                    self.extracted_images.append(image_info)

                    logger.debug(
                        f"Extracted image: {filename} ({pix.width}x{pix.height})"
                    )

                else:  # CMYK or other
                    logger.warning(f"Skipping CMYK image on page {page_num + 1}")

                pix = None  # Free memory

            except Exception as e:
                logger.error(
                    f"Failed to extract image {img_index} from page {page_num + 1}: {e}"
                )
                continue

        return extracted_images

    def extract_all_images(self) -> List[Dict[str, Any]]:
        """
        Extract all images from the entire document
        Returns: List of all extracted image info
        """
        logger.info(f"Extracting images from {len(self.doc)} pages...")

        all_images = []
        for page_num in range(len(self.doc)):
            page_images = self.extract_page_images(page_num)
            all_images.extend(page_images)

        logger.info(f"Extracted {len(all_images)} images total")
        return all_images

    def get_image_at_position(self, page_num: int, bbox: fitz.Rect) -> Dict[str, Any]:
        """
        Find image at a specific position on a page
        Returns: Image info dict or None
        """
        page_images = [
            img for img in self.extracted_images if img["page_num"] == page_num
        ]

        for img in page_images:
            img_bbox = img["bbox"]
            # Check if bounding boxes overlap
            if bbox.intersects(img_bbox):
                return img

        return None

    def optimize_image(self, image_path: str, quality: str = "medium") -> bool:
        """
        Optimize an extracted image for web usage
        quality: 'low', 'medium', 'high'
        """
        try:
            quality_settings = {
                "low": {"quality": 60, "max_size": (800, 600)},
                "medium": {"quality": 85, "max_size": (1200, 900)},
                "high": {"quality": 95, "max_size": (1600, 1200)},
            }

            settings = quality_settings.get(quality, quality_settings["medium"])

            with Image.open(image_path) as img:
                # Resize if too large
                if (
                    img.size[0] > settings["max_size"][0]
                    or img.size[1] > settings["max_size"][1]
                ):
                    img.thumbnail(settings["max_size"], Image.Resampling.LANCZOS)

                # Save with optimization
                if image_path.lower().endswith(".jpg") or image_path.lower().endswith(
                    ".jpeg"
                ):
                    img.save(
                        image_path, "JPEG", quality=settings["quality"], optimize=True
                    )
                else:
                    img.save(image_path, optimize=True)

            return True

        except Exception as e:
            logger.error(f"Failed to optimize image {image_path}: {e}")
            return False

    def get_extraction_summary(self) -> str:
        """Get a summary of extracted images"""
        if not self.extracted_images:
            return "No images extracted"

        total_images = len(self.extracted_images)
        pages_with_images = len(set(img["page_num"] for img in self.extracted_images))

        summary = f"""
Image Extraction Summary:
- Total images extracted: {total_images}
- Pages with images: {pages_with_images}
- Output directory: {self.output_dir}

Images by page:
"""

        # Group by page
        by_page = {}
        for img in self.extracted_images:
            page = img["page_num"]
            if page not in by_page:
                by_page[page] = []
            by_page[page].append(img)

        for page_num in sorted(by_page.keys()):
            images = by_page[page_num]
            summary += f"- Page {page_num + 1}: {len(images)} images\n"

        return summary.strip()


# Fix import issue
import io

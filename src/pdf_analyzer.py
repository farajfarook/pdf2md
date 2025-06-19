"""
PDF Analyzer - Analyzes PDF content and determines extraction strategy
"""

import fitz  # PyMuPDF
from typing import Dict, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFAnalyzer:
    """Analyzes PDF content to determine the best extraction strategy"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.analysis_results = {}
    
    def open_pdf(self) -> bool:
        """Open the PDF document"""
        try:
            self.doc = fitz.open(self.pdf_path)
            logger.info(f"Opened PDF: {self.pdf_path} ({len(self.doc)} pages)")
            return True
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            return False
    
    def close_pdf(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close()
    
    def analyze_page_content(self, page_num: int) -> Dict[str, Any]:
        """
        Analyze a single page to determine content type
        Returns: dict with analysis results
        """
        if not self.doc:
            return {}
        
        page = self.doc[page_num]
        
        # Get text blocks with positioning
        text_blocks = page.get_text("dict")
        text_content = page.get_text().strip()
        
        # Get images
        image_list = page.get_images()
        
        # Analyze text quality
        text_length = len(text_content)
        has_meaningful_text = text_length > 50  # Threshold for meaningful text
        
        # Determine content type
        if len(image_list) == 0 and has_meaningful_text:
            content_type = "text"
        elif len(image_list) > 0 and not has_meaningful_text:
            content_type = "image"
        elif len(image_list) > 0 and has_meaningful_text:
            content_type = "mixed"
        else:
            content_type = "empty"
        
        analysis = {
            "page_num": page_num,
            "content_type": content_type,
            "text_length": text_length,
            "image_count": len(image_list),
            "has_text": has_meaningful_text,
            "text_blocks": text_blocks,
            "images": image_list,
            "bbox": page.rect  # Page bounding box
        }
        
        return analysis
    
    def analyze_document(self) -> Dict[str, Any]:
        """
        Analyze the entire document
        Returns: comprehensive analysis results
        """
        if not self.doc:
            if not self.open_pdf():
                return {}
        
        logger.info("Analyzing document structure...")
        
        page_analyses = []
        total_text_length = 0
        total_images = 0
        content_types = {"text": 0, "image": 0, "mixed": 0, "empty": 0}
        
        # Analyze each page
        for page_num in range(len(self.doc)):
            page_analysis = self.analyze_page_content(page_num)
            page_analyses.append(page_analysis)
            
            total_text_length += page_analysis.get("text_length", 0)
            total_images += page_analysis.get("image_count", 0)
            content_types[page_analysis.get("content_type", "empty")] += 1
        
        # Determine overall document characteristics
        dominant_type = max(content_types.items(), key=lambda x: x[1])[0]
        
        self.analysis_results = {
            "pdf_path": self.pdf_path,
            "total_pages": len(self.doc),
            "page_analyses": page_analyses,
            "total_text_length": total_text_length,
            "total_images": total_images,
            "content_type_distribution": content_types,
            "dominant_content_type": dominant_type,
            "extraction_strategy": self._determine_extraction_strategy(content_types, dominant_type)
        }
        
        logger.info(f"Analysis complete: {self.analysis_results['total_pages']} pages, "
                   f"{total_images} images, dominant type: {dominant_type}")
        
        return self.analysis_results
    
    def _determine_extraction_strategy(self, content_types: Dict[str, int], dominant_type: str) -> str:
        """Determine the best extraction strategy based on content analysis"""
        if dominant_type == "text":
            return "direct_text"
        elif dominant_type == "image":
            return "ocr_heavy"
        elif dominant_type == "mixed":
            return "hybrid"
        else:
            return "fallback"
    
    def get_page_analysis(self, page_num: int) -> Dict[str, Any]:
        """Get analysis results for a specific page"""
        if not self.analysis_results:
            self.analyze_document()
        
        page_analyses = self.analysis_results.get("page_analyses", [])
        if 0 <= page_num < len(page_analyses):
            return page_analyses[page_num]
        return {}
    
    def get_document_summary(self) -> str:
        """Get a human-readable summary of the document analysis"""
        if not self.analysis_results:
            return "No analysis available"
        
        results = self.analysis_results
        summary = f"""
Document Analysis Summary:
- File: {results['pdf_path']}
- Pages: {results['total_pages']}
- Total Text Length: {results['total_text_length']} characters
- Total Images: {results['total_images']}
- Dominant Content Type: {results['dominant_content_type']}
- Recommended Strategy: {results['extraction_strategy']}

Page Distribution:
- Text-based pages: {results['content_type_distribution']['text']}
- Image-based pages: {results['content_type_distribution']['image']}
- Mixed content pages: {results['content_type_distribution']['mixed']}
- Empty pages: {results['content_type_distribution']['empty']}
        """.strip()
        
        return summary 
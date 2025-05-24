"""
PDF document processor.

This module handles extraction of text, images, tables, and metadata from PDF files.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

import fitz  # PyMuPDF
import PyPDF2
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDF document processor using PyMuPDF for advanced extraction."""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    async def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process PDF file and extract all content.
        
        Returns:
            Dict containing extracted content, metadata, and structure
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Open PDF with PyMuPDF for advanced processing
            doc = fitz.open(str(file_path))
            
            # Extract basic metadata
            metadata = self._extract_metadata(doc)
            
            # Extract content from all pages
            pages = []
            all_text = ""
            images = []
            tables = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with formatting
                page_text = self._extract_page_text(page)
                all_text += page_text + "\n\n"
                
                # Extract images
                page_images = self._extract_page_images(page, page_num)
                images.extend(page_images)
                
                # Extract tables
                page_tables = self._extract_page_tables(page, page_num)
                tables.extend(page_tables)
                
                # Store page information
                pages.append({
                    "page_number": page_num + 1,
                    "text": page_text,
                    "word_count": len(page_text.split()),
                    "images_count": len(page_images),
                    "tables_count": len(page_tables),
                })
            
            doc.close()
            
            # Analyze document structure
            structure = self._analyze_structure(all_text, pages)
            
            # Extract brand elements
            brand_elements = self._extract_brand_elements(all_text, images)
            
            return {
                "content_type": "pdf",
                "metadata": metadata,
                "page_count": len(pages),
                "word_count": len(all_text.split()),
                "text": all_text,
                "pages": pages,
                "images": images,
                "tables": tables,
                "structure": structure,
                "brand_elements": brand_elements,
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise
    
    def _extract_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "keywords": metadata.get("keywords", ""),
            "page_count": len(doc),
        }
    
    def _extract_page_text(self, page: fitz.Page) -> str:
        """Extract text from a page with formatting preservation."""
        try:
            # Get text with layout information
            text_dict = page.get_text("dict")
            
            # Process text blocks to preserve structure
            text_content = []
            
            for block in text_dict["blocks"]:
                if "lines" in block:  # Text block
                    block_text = []
                    for line in block["lines"]:
                        line_text = []
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                # Preserve formatting information
                                font_size = span["size"]
                                font_flags = span["flags"]
                                
                                # Mark headings based on font size and formatting
                                if font_size > 14 or font_flags & 2**4:  # Bold
                                    text = f"**{text}**"
                                
                                line_text.append(text)
                        
                        if line_text:
                            block_text.append(" ".join(line_text))
                    
                    if block_text:
                        text_content.append("\n".join(block_text))
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.warning(f"Error extracting formatted text, falling back to simple extraction: {e}")
            return page.get_text()
    
    def _extract_page_images(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from a page."""
        images = []
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    pix = fitz.Pixmap(page.parent, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        # Convert to PIL Image
                        img_data = pix.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        # Convert to base64 for storage
                        buffer = io.BytesIO()
                        pil_image.save(buffer, format="PNG")
                        img_base64 = base64.b64encode(buffer.getvalue()).decode()
                        
                        images.append({
                            "page_number": page_num + 1,
                            "image_index": img_index,
                            "width": pix.width,
                            "height": pix.height,
                            "format": "png",
                            "data": img_base64,
                            "size_bytes": len(img_data),
                        })
                    
                    pix = None  # Free memory
                    
                except Exception as e:
                    logger.warning(f"Error extracting image {img_index} from page {page_num}: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Error extracting images from page {page_num}: {e}")
        
        return images
    
    def _extract_page_tables(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables from a page."""
        tables = []
        
        try:
            # Simple table detection based on text positioning
            # This is a basic implementation - could be enhanced with more sophisticated algorithms
            text_dict = page.get_text("dict")
            
            # Look for text blocks that might be tables
            potential_tables = []
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    lines = block["lines"]
                    if len(lines) > 2:  # Potential table with multiple rows
                        # Check if lines have similar structure (multiple columns)
                        line_spans = [len(line["spans"]) for line in lines]
                        if len(set(line_spans)) <= 2 and max(line_spans) > 2:  # Consistent column structure
                            table_data = []
                            for line in lines:
                                row = [span["text"].strip() for span in line["spans"] if span["text"].strip()]
                                if row:
                                    table_data.append(row)
                            
                            if len(table_data) > 1:  # At least header + one row
                                tables.append({
                                    "page_number": page_num + 1,
                                    "table_index": len(tables),
                                    "rows": len(table_data),
                                    "columns": len(table_data[0]) if table_data else 0,
                                    "data": table_data,
                                })
            
        except Exception as e:
            logger.warning(f"Error extracting tables from page {page_num}: {e}")
        
        return tables
    
    def _analyze_structure(self, text: str, pages: List[Dict]) -> Dict[str, Any]:
        """Analyze document structure and identify sections."""
        structure = {
            "sections": [],
            "headings": [],
            "outline": [],
        }
        
        try:
            # Simple heading detection based on formatting markers
            lines = text.split('\n')
            current_section = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Detect headings (marked with ** from formatting)
                if line.startswith('**') and line.endswith('**'):
                    heading = line.strip('*').strip()
                    if len(heading) > 0 and len(heading) < 100:  # Reasonable heading length
                        structure["headings"].append({
                            "text": heading,
                            "line_number": i,
                            "level": 1,  # Could be enhanced to detect levels
                        })
                        
                        # Start new section
                        if current_section:
                            structure["sections"].append(current_section)
                        
                        current_section = {
                            "title": heading,
                            "start_line": i,
                            "content": [],
                        }
                elif current_section:
                    current_section["content"].append(line)
            
            # Add last section
            if current_section:
                structure["sections"].append(current_section)
            
        except Exception as e:
            logger.warning(f"Error analyzing document structure: {e}")
        
        return structure
    
    def _extract_brand_elements(self, text: str, images: List[Dict]) -> Dict[str, Any]:
        """Extract brand-specific elements from the document."""
        brand_elements = {
            "colors": [],
            "fonts": [],
            "logos": [],
            "brand_mentions": [],
            "guidelines": [],
        }
        
        try:
            # Look for color mentions (hex codes, RGB, color names)
            import re
            
            # Hex colors
            hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', text)
            brand_elements["colors"].extend(hex_colors)
            
            # RGB colors
            rgb_colors = re.findall(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', text, re.IGNORECASE)
            brand_elements["colors"].extend(rgb_colors)
            
            # Common brand-related keywords
            brand_keywords = [
                "brand", "logo", "color", "font", "typography", "voice", "tone",
                "guidelines", "identity", "palette", "style", "design"
            ]
            
            for keyword in brand_keywords:
                mentions = []
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if keyword.lower() in line.lower():
                        mentions.append({
                            "keyword": keyword,
                            "line": line.strip(),
                            "line_number": i,
                        })
                
                if mentions:
                    brand_elements["brand_mentions"].extend(mentions)
            
            # Identify potential logos in images (basic heuristic)
            for img in images:
                # Small images might be logos
                if img["width"] < 500 and img["height"] < 500:
                    brand_elements["logos"].append({
                        "page": img["page_number"],
                        "size": f"{img['width']}x{img['height']}",
                        "image_data": img["data"][:100] + "...",  # Truncated for storage
                    })
            
        except Exception as e:
            logger.warning(f"Error extracting brand elements: {e}")
        
        return brand_elements

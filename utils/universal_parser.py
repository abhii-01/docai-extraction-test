"""
Universal Document Parser using Google Document AI Layout Parser
Recursively extracts structure, tables, and images into a hierarchical JSON tree.

Note: Type hints for Document AI objects are intentionally omitted because
the Block/Document classes are not directly importable from documentai_v1.
They exist dynamically in the API response objects.
"""

import os
from typing import List, Dict, Any, Optional
from google.cloud import documentai_v1 as documentai
from pdf2image import convert_from_path
from PIL import Image


class UniversalParser:
    """
    Parses PDF documents into a hierarchical JSON structure using Document AI.
    Preserves:
    1. Logical Hierarchy (Sections -> Children)
    2. Table Structure (Grid format)
    3. Visual Content (Images/Charts extracted as files)
    """

    def __init__(self, docai_client, output_dir: str = "output"):
        """
        Args:
            docai_client: Instance of DocumentAIClient
            output_dir: Directory to save extracted images and results
        """
        self.client = docai_client
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main entry point to parse a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing the hierarchical document structure
        """
        print(f"Processing document: {pdf_path}")
        
        # 1. Process with Document AI
        doc = self.client.process_document(pdf_path)
        
        # 2. Load PDF pages as images (for cropping visuals)
        print("Loading PDF pages for image extraction...")
        try:
            page_images = convert_from_path(pdf_path)
        except Exception as e:
            print(f"Warning: Could not load PDF images ({e}). Image extraction will be skipped.")
            page_images = []

        # 3. Get the full document text (used for text_anchor extraction)
        full_text = getattr(doc, 'text', '') or ''

        # 4. Begin Recursive Parsing from the Layout root
        # Layout Parser results are in doc.document_layout.blocks
        root_blocks = []
        if hasattr(doc, 'document_layout') and doc.document_layout:
            root_blocks = getattr(doc.document_layout, 'blocks', []) or []
        
        parsed_structure = []
        for block in root_blocks:
            node = self._visit_block(block, full_text, page_images, pdf_path)
            if node:
                parsed_structure.append(node)
        
        # 5. Get page count safely
        page_count = len(doc.pages) if hasattr(doc, 'pages') and doc.pages else 0
                
        result = {
            "metadata": {
                "filename": os.path.basename(pdf_path),
                "page_count": page_count,
                "text_length": len(full_text)
            },
            "structure": parsed_structure
        }
        
        return result

    def _visit_block(self, block, full_text: str, page_images: List[Image.Image], pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Recursively processes a block and its children.
        Uses defensive attribute access to handle API variations.
        """
        # 1. Identify Block Type
        block_type = self._get_block_type(block)
        
        # 2. Get block ID safely
        block_id = getattr(block, 'block_id', None) or "unknown"
        
        # 3. Get page number safely
        page_span = getattr(block, 'page_span', None)
        page_num = getattr(page_span, 'page_start', 1) if page_span else 1
        
        # 4. Get bounding box safely
        layout = getattr(block, 'layout', None)
        bbox = None
        if layout:
            bounding_poly = getattr(layout, 'bounding_poly', None)
            if bounding_poly:
                bbox = self._normalize_bbox(bounding_poly)
        
        # 5. Base Node Structure
        node = {
            "id": block_id,
            "type": block_type,
            "page": page_num,
            "bbox": bbox,
            "children": []
        }

        # 6. Handle Content based on Type
        
        # CASE A: TABLES
        table_block = getattr(block, 'table_block', None)
        if table_block:
            node["type"] = "table"
            node["data"] = self._extract_table_grid(table_block, full_text)
            return node

        # CASE B: IMAGES / CHARTS
        image_block = getattr(block, 'image_block', None)
        text_block = getattr(block, 'text_block', None)
        
        if image_block or (text_block and block_type in ["image", "figure", "chart", "diagram", "Figure", "Image"]):
            node["type"] = block_type if block_type not in ["unknown"] else "image"
            
            if page_images:
                image_path = self._save_crop(block, page_images)
                if image_path:
                    node["file_path"] = image_path
            return node

        # CASE C: LISTS
        list_block = getattr(block, 'list_block', None)
        if list_block:
            node["type"] = "list"
            # Fall through to text block handling below for content

        # CASE D: TEXT & CONTAINERS (Headings, Paragraphs, Sections)
        if text_block:
            # Extract text using text_anchor
            text_anchor = getattr(layout, 'text_anchor', None) if layout else None
            node["text"] = self._get_text(text_anchor, full_text)
            
            # --- RECURSION ---
            # Layout Parser blocks can be nested inside text_block.blocks
            child_blocks = getattr(text_block, 'blocks', None) or []
            for child_block in child_blocks:
                child_node = self._visit_block(child_block, full_text, page_images, pdf_path)
                if child_node:
                    node["children"].append(child_node)
            
            return node
            
        return None  # Skip empty/unknown blocks

    def _get_block_type(self, block) -> str:
        """Determines the semantic type of the block using defensive attribute access."""
        # Check for specific block types
        if getattr(block, 'table_block', None):
            return "table"
        if getattr(block, 'image_block', None):
            return "image"
        if getattr(block, 'list_block', None):
            return "list"
        
        # Check text_block.type_ for semantic type (heading, paragraph, etc.)
        text_block = getattr(block, 'text_block', None)
        if text_block:
            type_value = getattr(text_block, 'type_', None)
            if type_value:
                # type_ might be an enum or string, convert to string
                return str(type_value)
            
        return "unknown"

    def _get_text(self, text_anchor, full_text: str) -> str:
        """Extracts text from the document string using the anchor segments."""
        if not text_anchor:
            return ""
        
        text_segments = getattr(text_anchor, 'text_segments', None) or []
        if not text_segments:
            return ""
            
        extracted_text = ""
        for segment in text_segments:
            start = int(getattr(segment, 'start_index', 0) or 0)
            end = int(getattr(segment, 'end_index', 0) or 0)
            if end > start and end <= len(full_text):
                extracted_text += full_text[start:end]
            
        return extracted_text.strip()

    def _extract_table_grid(self, table_block, full_text: str) -> Dict[str, Any]:
        """
        Reconstructs the table into a structured grid format.
        """
        rows_data = []
        
        # Combine header and body rows safely
        header_rows = list(getattr(table_block, 'header_rows', []) or [])
        body_rows = list(getattr(table_block, 'body_rows', []) or [])
        all_rows = header_rows + body_rows
        
        for row in all_rows:
            row_cells = []
            cells = getattr(row, 'cells', []) or []
            for cell in cells:
                # Get cell text via layout.text_anchor
                cell_layout = getattr(cell, 'layout', None)
                cell_text_anchor = getattr(cell_layout, 'text_anchor', None) if cell_layout else None
                cell_text = self._get_text(cell_text_anchor, full_text)
                
                cell_info = {
                    "text": cell_text,
                    "row_span": getattr(cell, 'row_span', 1) or 1,
                    "col_span": getattr(cell, 'col_span', 1) or 1
                }
                row_cells.append(cell_info)
            rows_data.append(row_cells)

        # Create a simple 2D text matrix for easier reading
        simple_matrix = []
        for row in rows_data:
            simple_matrix.append([cell["text"] for cell in row])

        return {
            "structured_rows": rows_data,
            "simple_matrix": simple_matrix
        }

    def _save_crop(self, block, page_images: List[Image.Image]) -> Optional[str]:
        """
        Crops the region from the page image and saves it to disk.
        """
        try:
            layout = getattr(block, 'layout', None)
            if not layout:
                return None
                
            bounding_poly = getattr(layout, 'bounding_poly', None)
            if not bounding_poly:
                return None

            page_span = getattr(block, 'page_span', None)
            page_start = getattr(page_span, 'page_start', 1) if page_span else 1
            page_idx = page_start - 1  # 0-indexed
            
            if page_idx < 0 or page_idx >= len(page_images):
                return None
                
            image = page_images[page_idx]
            width, height = image.size
            
            # Get normalized vertices
            vertices = getattr(bounding_poly, 'normalized_vertices', None) or []
            if not vertices:
                return None
                
            # Calculate pixel coordinates
            x_coords = [getattr(v, 'x', 0) or 0 for v in vertices]
            y_coords = [getattr(v, 'y', 0) or 0 for v in vertices]
            
            x_min = int(min(x_coords) * width)
            y_min = int(min(y_coords) * height)
            x_max = int(max(x_coords) * width)
            y_max = int(max(y_coords) * height)
            
            # Validate crop box
            if x_max <= x_min or y_max <= y_min:
                return None
            
            # Crop
            cropped_img = image.crop((x_min, y_min, x_max, y_max))
            
            # Save
            block_id = getattr(block, 'block_id', 'unknown') or 'unknown'
            # Sanitize block_id for filename
            safe_block_id = str(block_id).replace('/', '_').replace('\\', '_')
            filename = f"block_{safe_block_id}.png"
            save_path = os.path.join(self.images_dir, filename)
            cropped_img.save(save_path)
            
            return save_path
            
        except Exception as e:
            block_id = getattr(block, 'block_id', 'unknown')
            print(f"Error saving crop for block {block_id}: {e}")
            return None

    def _normalize_bbox(self, bbox) -> List[float]:
        """Returns [min_x, min_y, max_x, max_y] normalized coordinates."""
        vertices = getattr(bbox, 'normalized_vertices', None) or []
        if not vertices:
            return []
            
        x_coords = [getattr(v, 'x', 0) or 0 for v in vertices]
        y_coords = [getattr(v, 'y', 0) or 0 for v in vertices]
        
        return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

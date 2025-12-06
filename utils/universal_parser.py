"""
Universal Document Parser using Google Document AI Layout Parser
Recursively extracts structure, tables, and images into a hierarchical JSON tree.
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

        # 3. Begin Recursive Parsing from the Layout root
        # Layout Parser results are in doc.document_layout.blocks
        root_blocks = doc.document_layout.blocks
        
        parsed_structure = []
        for block in root_blocks:
            node = self._visit_block(block, doc, page_images, pdf_path)
            if node:
                parsed_structure.append(node)
                
        result = {
            "metadata": {
                "filename": os.path.basename(pdf_path),
                "page_count": len(doc.pages),
                "text_length": len(doc.text)
            },
            "structure": parsed_structure
        }
        
        return result

    def _visit_block(self, block, doc, page_images: List[Image.Image], pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Recursively processes a block and its children.
        """
        # 1. Identify Block Type
        block_type = self._get_block_type(block)
        
        # 2. Base Node Structure
        node = {
            "id": block.block_id,
            "type": block_type,
            "page": block.page_span.page_start if block.page_span else 1,
            "bbox": self._normalize_bbox(block.layout.bounding_poly) if block.layout.bounding_poly else None,
            "children": []
        }

        # 3. Handle Content based on Type
        
        # CASE A: TABLES
        if block.table_block:
            node["type"] = "table" # Ensure type is set explicitly
            node["data"] = self._extract_table_grid(block.table_block, doc.text)
            # Tables usually don't have children in the layout sense we care about
            return node

        # CASE B: IMAGES / CHARTS
        # Note: Layout Parser might classify things as 'image' inside a text_block type
        # or as a dedicated image_block.
        elif block.image_block or (block.text_block and block_type in ["image", "figure", "chart", "diagram"]):
            node["type"] = block_type if block_type in ["image", "figure", "chart", "diagram"] else "image"
            
            if page_images:
                image_path = self._save_crop(block, page_images, pdf_path)
                node["file_path"] = image_path
            return node

        # CASE C: LISTS
        elif block.list_block:
            node["type"] = "list"
            # List blocks often contain list items as children blocks (if nested) 
            # or we might need to look at text_block.blocks if defined there.
            # Document AI structure can vary, but we'll fall through to text block recursion below if present.

        # CASE D: TEXT & CONTAINERS (Headings, Paragraphs, Sections)
        if block.text_block:
            node["text"] = self._get_text(block.layout.text_anchor, doc.text)
            
            # --- RECURSION ---
            # Layout Parser blocks can be nested. 
            if block.text_block.blocks:
                for child_block in block.text_block.blocks:
                    child_node = self._visit_block(child_block, doc, page_images, pdf_path)
                    if child_node:
                        node["children"].append(child_node)
            
            return node
            
        return None # Skip empty/unknown blocks

    def _get_block_type(self, block) -> str:
        """Determines the semantic type of the block."""
        if block.table_block:
            return "table"
        if block.image_block:
            return "image"
        if block.list_block:
            return "list"
        
        if block.text_block and block.text_block.type_:
            return block.text_block.type_
            
        return "unknown"

    def _get_text(self, text_anchor, full_text: str) -> str:
        """Extracts text from the document string using the anchor segments."""
        if not text_anchor or not text_anchor.text_segments:
            return ""
            
        extracted_text = ""
        for segment in text_anchor.text_segments:
            start = int(segment.start_index)
            end = int(segment.end_index)
            extracted_text += full_text[start:end]
            
        return extracted_text.strip()

    def _extract_table_grid(self, table_block, full_text: str) -> Dict[str, Any]:
        """
        Reconstructs the table into a structured grid format.
        """
        rows_data = []
        
        # Combine header and body rows
        all_rows = list(table_block.header_rows) + list(table_block.body_rows)
        
        for row in all_rows:
            row_cells = []
            for cell in row.cells:
                cell_text = self._get_text(cell.layout.text_anchor, full_text)
                cell_info = {
                    "text": cell_text,
                    "row_span": cell.row_span,
                    "col_span": cell.col_span
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

    def _save_crop(self, block, page_images: List[Image.Image], pdf_path: str) -> Optional[str]:
        """
        Crops the region from the page image and saves it to disk.
        """
        try:
            if not block.layout.bounding_poly:
                return None

            page_idx = block.page_span.page_start - 1 # 0-indexed
            if page_idx < 0 or page_idx >= len(page_images):
                return None
                
            image = page_images[page_idx]
            width, height = image.size
            
            # Get normalized vertices
            vertices = block.layout.bounding_poly.normalized_vertices
            if not vertices:
                return None
                
            # Calculate pixel coordinates
            x_min = int(min(v.x for v in vertices) * width)
            y_min = int(min(v.y for v in vertices) * height)
            x_max = int(max(v.x for v in vertices) * width)
            y_max = int(max(v.y for v in vertices) * height)
            
            # Crop
            cropped_img = image.crop((x_min, y_min, x_max, y_max))
            
            # Save
            filename = f"block_{block.block_id}.png"
            save_path = os.path.join(self.images_dir, filename)
            cropped_img.save(save_path)
            
            return save_path
            
        except Exception as e:
            print(f"Error saving crop for block {block.block_id}: {e}")
            return None

    def _normalize_bbox(self, bbox) -> List[float]:
        """Returns [min_x, min_y, max_x, max_y] normalized coordinates."""
        if bbox.normalized_vertices:
            xs = [v.x for v in bbox.normalized_vertices]
            ys = [v.y for v in bbox.normalized_vertices]
            return [min(xs), min(ys), max(xs), max(ys)]
        return []

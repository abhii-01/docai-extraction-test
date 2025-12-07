# Document AI Enhancement Roadmap

This document lists potential enhancements for the Document AI parsing pipeline, with source references and code snippets for future implementation.

---

## Current Implementation Status

| Feature | Status | File |
|---------|--------|------|
| Document AI Client | ✅ Done | `utils/docai_client.py` |
| Layout Parser Integration | ✅ Done | `utils/universal_parser.py` |
| Recursive Block Traversal | ✅ Done | `_visit_block()` |
| Hierarchical JSON Output | ✅ Done | Returns nested structure |
| Table Extraction (Grid) | ✅ Done | `_extract_table_grid()` |
| Image/Chart Cropping | ✅ Done | `_save_crop()` |
| Text Extraction via Anchors | ✅ Done | `_get_text()` |

---

## Enhancement #1: Multi-Processor Support (PRIORITY: HIGH)

**Goal:** Support multiple Document AI processors (Layout Parser, Form Parser, OCR) and auto-select based on document type.

**Source:** [GoogleCloudPlatform/document-ai-samples](https://github.com/GoogleCloudPlatform/document-ai-samples)

**Use Cases:**
- Layout Parser → Born-digital PDFs with complex layouts
- Form Parser → Structured forms, invoices, receipts
- OCR Processor → Scanned documents
- Custom Processors → Domain-specific extraction

**Code Snippet:**
```python
from enum import Enum
from typing import Optional

class ProcessorType(Enum):
    LAYOUT = "layout"
    FORM = "form"
    OCR = "ocr"
    CUSTOM = "custom"

class MultiProcessorClient:
    """Client supporting multiple Document AI processors"""
    
    def __init__(
        self,
        project_id: str,
        location: str,
        layout_processor_id: Optional[str] = None,
        form_processor_id: Optional[str] = None,
        ocr_processor_id: Optional[str] = None,
    ):
        self.project_id = project_id
        self.location = location
        self.processors = {}
        
        if layout_processor_id:
            self.processors[ProcessorType.LAYOUT] = self._build_processor_name(layout_processor_id)
        if form_processor_id:
            self.processors[ProcessorType.FORM] = self._build_processor_name(form_processor_id)
        if ocr_processor_id:
            self.processors[ProcessorType.OCR] = self._build_processor_name(ocr_processor_id)
    
    def _build_processor_name(self, processor_id: str) -> str:
        return f"projects/{self.project_id}/locations/{self.location}/processors/{processor_id}"
    
    def process_document(self, file_path: str, processor_type: ProcessorType):
        """Process document with specified processor"""
        if processor_type not in self.processors:
            raise ValueError(f"Processor {processor_type} not configured")
        
        processor_name = self.processors[processor_type]
        # ... processing logic
```

---

## Enhancement #2: Confidence Scores

**Goal:** Track confidence scores for each extracted element for quality control.

**Source:** [Hegghammer/daiR](https://github.com/Hegghammer/daiR), [GoogleCloudPlatform/professional-services](https://github.com/GoogleCloudPlatform/professional-services)

**Code Snippet:**
```python
# In _visit_block(), add confidence to node:
node = {
    "id": block_id,
    "type": block_type,
    "page": page_num,
    "bbox": bbox,
    "confidence": getattr(layout, 'confidence', None) if layout else None,  # ADD THIS
    "children": []
}
```

---

## Enhancement #3: Table to DataFrame/CSV Export

**Goal:** Convert extracted tables directly to pandas DataFrame or CSV.

**Source:** [Hegghammer/daiR](https://github.com/Hegghammer/daiR)

**Code Snippet:**
```python
import pandas as pd
from typing import Dict, Any

def table_to_dataframe(table_data: Dict[str, Any]) -> pd.DataFrame:
    """Convert extracted table to pandas DataFrame"""
    simple_matrix = table_data.get("simple_matrix", [])
    
    if not simple_matrix:
        return pd.DataFrame()
    
    # First row as header
    if len(simple_matrix) > 1:
        df = pd.DataFrame(simple_matrix[1:], columns=simple_matrix[0])
    else:
        df = pd.DataFrame(simple_matrix)
    
    return df

def export_tables_to_csv(parsed_result: Dict, output_dir: str):
    """Export all tables from parsed result to CSV files"""
    tables = extract_all_tables(parsed_result)  # Helper to find all table nodes
    for i, table in enumerate(tables):
        df = table_to_dataframe(table["data"])
        df.to_csv(f"{output_dir}/table_{i}.csv", index=False)
```

---

## Enhancement #4: PDF Type Detection

**Goal:** Auto-detect if PDF is born-digital, scanned, or handwritten.

**Source:** Common pattern (PyMuPDF), [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF)

**Note:** This is a recommended practice, not directly from the Document AI repos. Useful for auto-selecting processors.

**Code Snippet:**
```python
import fitz  # PyMuPDF

def detect_pdf_type(pdf_path: str) -> str:
    """
    Detect PDF type: born-digital, scanned, or mixed.
    
    Returns:
        'born-digital' - Has extractable text layer
        'scanned' - Image-based, no text layer
        'mixed' - Some pages have text, some don't
    """
    doc = fitz.open(pdf_path)
    
    pages_with_text = 0
    total_pages = len(doc)
    
    for page in doc:
        text = page.get_text().strip()
        if len(text) > 50:  # Threshold for "has text"
            pages_with_text += 1
    
    doc.close()
    
    ratio = pages_with_text / total_pages if total_pages > 0 else 0
    
    if ratio > 0.9:
        return "born-digital"
    elif ratio < 0.1:
        return "scanned"
    else:
        return "mixed"

def detect_pdf_type_per_page(pdf_path: str) -> dict:
    """Returns type for each page - useful for mixed documents"""
    doc = fitz.open(pdf_path)
    
    results = {"overall": None, "pages": []}
    
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        page_type = "born-digital" if len(text) > 50 else "scanned"
        results["pages"].append({"page": i + 1, "type": page_type})
    
    types = [p["type"] for p in results["pages"]]
    if all(t == "born-digital" for t in types):
        results["overall"] = "born-digital"
    elif all(t == "scanned" for t in types):
        results["overall"] = "scanned"
    else:
        results["overall"] = "mixed"
    
    doc.close()
    return results
```

---

## Enhancement #5: Batch Processing

**Goal:** Process multiple PDFs asynchronously via Google Cloud Storage.

**Source:** [GoogleCloudPlatform/document-ai-samples](https://github.com/GoogleCloudPlatform/document-ai-samples)

**Code Snippet:**
```python
from google.cloud import documentai_v1 as documentai
from google.api_core.operation import Operation

def batch_process_documents(
    client: documentai.DocumentProcessorServiceClient,
    processor_name: str,
    gcs_input_uri: str,
    gcs_output_uri: str,
) -> Operation:
    """
    Process multiple documents from GCS bucket.
    
    Args:
        gcs_input_uri: gs://bucket/input_folder/
        gcs_output_uri: gs://bucket/output_folder/
    """
    gcs_documents = documentai.GcsDocuments(
        documents=[
            documentai.GcsDocument(
                gcs_uri=gcs_input_uri,
                mime_type="application/pdf"
            )
        ]
    )
    
    input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)
    output_config = documentai.DocumentOutputConfig(
        gcs_output_config=documentai.DocumentOutputConfig.GcsOutputConfig(
            gcs_uri=gcs_output_uri
        )
    )
    
    request = documentai.BatchProcessRequest(
        name=processor_name,
        input_documents=input_config,
        document_output_config=output_config,
    )
    
    operation = client.batch_process_documents(request)
    return operation
```

---

## Enhancement #6: Visualization/Debugging Tools

**Goal:** Draw bounding boxes on PDF pages for visual verification.

**Source:** [GoogleCloudPlatform/document-ai-samples](https://github.com/GoogleCloudPlatform/document-ai-samples)

**Code Snippet:**
```python
from PIL import Image, ImageDraw
from typing import List, Dict

def visualize_blocks(
    page_image: Image.Image,
    blocks: List[Dict],
    color_map: Dict[str, str] = None
) -> Image.Image:
    """Draw bounding boxes on page image"""
    
    if color_map is None:
        color_map = {
            "paragraph": "blue",
            "table": "green",
            "image": "red",
            "heading": "purple",
            "list": "orange",
        }
    
    draw = ImageDraw.Draw(page_image)
    width, height = page_image.size
    
    for block in blocks:
        bbox = block.get("bbox", [])
        if len(bbox) == 4:
            x_min, y_min, x_max, y_max = bbox
            # Convert normalized to pixel coordinates
            coords = [
                x_min * width, y_min * height,
                x_max * width, y_max * height
            ]
            color = color_map.get(block.get("type", "unknown"), "gray")
            draw.rectangle(coords, outline=color, width=2)
    
    return page_image
```

---

## Enhancement #7: BigQuery Export

**Goal:** Export parsed documents directly to BigQuery for analytics.

**Source:** [GoogleCloudPlatform/document-ai-warehouse](https://github.com/GoogleCloudPlatform/document-ai-warehouse)

**Code Snippet:**
```python
from google.cloud import bigquery

def export_to_bigquery(
    parsed_result: Dict,
    project_id: str,
    dataset_id: str,
    table_id: str
):
    """Export parsed document metadata and text to BigQuery"""
    
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    # Flatten structure for BQ
    rows = []
    for block in flatten_blocks(parsed_result["structure"]):
        rows.append({
            "filename": parsed_result["metadata"]["filename"],
            "block_id": block["id"],
            "block_type": block["type"],
            "page": block["page"],
            "text": block.get("text", ""),
            "confidence": block.get("confidence"),
        })
    
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise Exception(f"BigQuery insert errors: {errors}")
```

---

## Enhancement #8: GCS Integration (File Watcher)

**Goal:** Automatically trigger processing when new files arrive in GCS bucket.

**Source:** [ypratap11/invoice-processing-ai](https://github.com/ypratap11/invoice-processing-ai)

**Code Snippet:**
```python
# Cloud Function trigger example
from google.cloud import storage

def gcs_trigger(event, context):
    """
    Cloud Function triggered by GCS file upload.
    Deploy with: gcloud functions deploy gcs_trigger --trigger-bucket=YOUR_BUCKET
    """
    bucket_name = event['bucket']
    file_name = event['name']
    
    if not file_name.endswith('.pdf'):
        return
    
    # Download and process
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    local_path = f"/tmp/{file_name}"
    blob.download_to_filename(local_path)
    
    # Process with Document AI
    # ... your processing logic
```

---

## Enhancement #9: Human-in-the-Loop (HITL) Workflow

**Goal:** Flag low-confidence extractions for manual human review.

**Source:** [GoogleCloudPlatform/document-ai-warehouse](https://github.com/GoogleCloudPlatform/document-ai-warehouse)

**What it does:** When Document AI extracts content with confidence below a threshold (e.g., 80%), it gets flagged for human review before being accepted into final output.

**Code Snippet:**
```python
def flag_for_review(
    parsed_result: Dict,
    confidence_threshold: float = 0.8
) -> List[Dict]:
    """Return blocks that need human review"""
    
    blocks_for_review = []
    
    def check_block(block, path=""):
        confidence = block.get("confidence")
        if confidence is not None and confidence < confidence_threshold:
            blocks_for_review.append({
                "path": path,
                "block": block,
                "confidence": confidence,
                "reason": "low_confidence"
            })
        
        for i, child in enumerate(block.get("children", [])):
            check_block(child, f"{path}/children[{i}]")
    
    for i, block in enumerate(parsed_result.get("structure", [])):
        check_block(block, f"structure[{i}]")
    
    return blocks_for_review
```

---

## Enhancement #10: RAG Pipeline Integration

**Goal:** Embed extracted text and store in vector database for semantic search.

**Source:** [cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex)

**Code Snippet:**
```python
from typing import List
import openai  # or google.generativeai for Gemini

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for embedding"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def embed_and_store(parsed_result: Dict, vector_db_client):
    """Embed text chunks and store for RAG"""
    
    all_text = extract_all_text(parsed_result)  # Helper to get all text
    chunks = chunk_text(all_text)
    
    for i, chunk in enumerate(chunks):
        # Get embedding (example with OpenAI)
        response = openai.Embedding.create(
            input=chunk,
            model="text-embedding-ada-002"
        )
        embedding = response['data'][0]['embedding']
        
        # Store in vector DB
        vector_db_client.upsert(
            id=f"{parsed_result['metadata']['filename']}_{i}",
            embedding=embedding,
            metadata={
                "filename": parsed_result['metadata']['filename'],
                "chunk_index": i,
                "text": chunk
            }
        )
```

---

## Enhancement #11: Extraction Diagnosis & Gap Detection

**Goal:** Identify text present in the PDF but missing from Document AI output, and provide visual evidence (cropped images) of where the missing text is located.

**Use Cases:**
- Quality assurance of Document AI extraction
- Debugging why certain text regions weren't extracted
- Compliance verification (ensuring 100% text capture)
- Identifying problematic regions (handwriting, poor scan quality, etc.)

**How it works:**
1. Extract ALL text from PDF using PyMuPDF (direct text layer extraction)
2. Get Document AI extracted text output
3. Compare and find text snippets NOT present in Document AI output
4. Locate the bounding boxes of missing text in the PDF
5. Crop and save images showing where the missing text appears

**Code Snippet:**
```python
import fitz  # PyMuPDF
from PIL import Image
from typing import Dict, List, Tuple
from difflib import SequenceMatcher
import io
import os

class ExtractionDiagnostics:
    """Diagnose Document AI extraction by finding missed text regions"""
    
    def __init__(self, pdf_path: str, docai_output: Dict, output_dir: str = "diagnosis_output"):
        self.pdf_path = pdf_path
        self.docai_output = docai_output
        self.output_dir = output_dir
        self.doc = fitz.open(pdf_path)
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_pdf_text_with_positions(self) -> List[Dict]:
        """
        Extract all text from PDF with bounding box positions.
        Returns list of text blocks with their locations.
        """
        all_blocks = []
        
        for page_num, page in enumerate(self.doc):
            # Get text blocks with positions: (x0, y0, x1, y1, "text", block_no, block_type)
            blocks = page.get_text("blocks")
            
            for block in blocks:
                if block[6] == 0:  # Type 0 = text block (not image)
                    all_blocks.append({
                        "page": page_num + 1,
                        "bbox": {
                            "x0": block[0],
                            "y0": block[1],
                            "x1": block[2],
                            "y1": block[3]
                        },
                        "text": block[4].strip(),
                        "block_id": f"p{page_num + 1}_b{block[5]}"
                    })
        
        return all_blocks
    
    def get_docai_text(self) -> str:
        """Extract all text from Document AI output"""
        texts = []
        
        def collect_text(node):
            if "text" in node and node["text"]:
                texts.append(node["text"])
            for child in node.get("children", []):
                collect_text(child)
        
        for block in self.docai_output.get("structure", []):
            collect_text(block)
        
        return " ".join(texts)
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison (lowercase, remove extra whitespace)"""
        import re
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def find_missing_text(self, similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Find text blocks from PDF that are NOT in Document AI output.
        
        Args:
            similarity_threshold: Text similarity threshold (0-1). 
                                  Below this = considered missing.
        
        Returns:
            List of missing text blocks with their locations
        """
        pdf_blocks = self.extract_pdf_text_with_positions()
        docai_text = self.normalize_text(self.get_docai_text())
        
        missing_blocks = []
        
        for block in pdf_blocks:
            block_text = self.normalize_text(block["text"])
            
            # Skip very short text (likely noise)
            if len(block_text) < 5:
                continue
            
            # Check if this text appears in Document AI output
            found = False
            
            # Check for substring match first
            if block_text in docai_text:
                found = True
            else:
                # Check for fuzzy match (handles minor OCR differences)
                # Use sliding window for longer docai text
                window_size = len(block_text) + 50
                best_ratio = 0
                
                for i in range(0, len(docai_text) - len(block_text) + 1, 20):
                    window = docai_text[i:i + window_size]
                    ratio = SequenceMatcher(None, block_text, window).ratio()
                    best_ratio = max(best_ratio, ratio)
                    
                    if best_ratio >= similarity_threshold:
                        found = True
                        break
            
            if not found:
                missing_blocks.append({
                    **block,
                    "best_match_ratio": best_ratio if 'best_ratio' in dir() else 0
                })
        
        return missing_blocks
    
    def crop_missing_regions(self, missing_blocks: List[Dict], zoom: float = 2.0) -> List[Dict]:
        """
        Crop images of regions with missing text.
        
        Args:
            missing_blocks: List of missing text blocks
            zoom: Zoom factor for higher resolution crops
        
        Returns:
            List of missing blocks with added 'image_path' field
        """
        results = []
        
        for i, block in enumerate(missing_blocks):
            page_num = block["page"] - 1  # 0-indexed
            page = self.doc[page_num]
            
            # Get the bounding box with some padding
            bbox = block["bbox"]
            padding = 10
            rect = fitz.Rect(
                bbox["x0"] - padding,
                bbox["y0"] - padding,
                bbox["x1"] + padding,
                bbox["y1"] + padding
            )
            
            # Clip to page bounds
            rect = rect & page.rect
            
            # Create high-res image of the region
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, clip=rect)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Save the cropped image
            image_filename = f"missing_{i+1}_page{block['page']}.png"
            image_path = os.path.join(self.output_dir, image_filename)
            img.save(image_path)
            
            results.append({
                **block,
                "image_path": image_path
            })
        
        return results
    
    def generate_diagnosis_report(self, similarity_threshold: float = 0.8) -> Dict:
        """
        Generate complete diagnosis report.
        
        Returns:
            Dict with diagnosis summary, missing blocks, and image paths
        """
        # Find missing text
        missing_blocks = self.find_missing_text(similarity_threshold)
        
        # Crop images of missing regions
        if missing_blocks:
            missing_with_images = self.crop_missing_regions(missing_blocks)
        else:
            missing_with_images = []
        
        # Get statistics
        pdf_blocks = self.extract_pdf_text_with_positions()
        total_pdf_blocks = len([b for b in pdf_blocks if len(b["text"].strip()) >= 5])
        missing_count = len(missing_with_images)
        
        coverage = ((total_pdf_blocks - missing_count) / total_pdf_blocks * 100) if total_pdf_blocks > 0 else 100
        
        report = {
            "summary": {
                "pdf_file": self.pdf_path,
                "total_text_blocks": total_pdf_blocks,
                "missing_blocks": missing_count,
                "coverage_percentage": round(coverage, 2),
                "similarity_threshold": similarity_threshold,
                "diagnosis_status": "PASS" if coverage >= 95 else "REVIEW_NEEDED"
            },
            "missing_regions": missing_with_images,
            "output_directory": self.output_dir
        }
        
        # Save report as JSON
        import json
        report_path = os.path.join(self.output_dir, "diagnosis_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()


# Usage Example:
def diagnose_extraction(pdf_path: str, docai_output: Dict, output_dir: str = "diagnosis") -> Dict:
    """
    Run extraction diagnosis on a parsed document.
    
    Args:
        pdf_path: Path to the original PDF file
        docai_output: Output from UniversalParser.parse()
        output_dir: Directory to save diagnosis images and report
    
    Returns:
        Diagnosis report with missing text regions and their images
    """
    diagnostics = ExtractionDiagnostics(pdf_path, docai_output, output_dir)
    
    try:
        report = diagnostics.generate_diagnosis_report()
        
        print(f"\n📊 Extraction Diagnosis Report")
        print(f"=" * 50)
        print(f"PDF: {report['summary']['pdf_file']}")
        print(f"Total text blocks: {report['summary']['total_text_blocks']}")
        print(f"Missing blocks: {report['summary']['missing_blocks']}")
        print(f"Coverage: {report['summary']['coverage_percentage']}%")
        print(f"Status: {report['summary']['diagnosis_status']}")
        
        if report['missing_regions']:
            print(f"\n⚠️  Missing Text Regions:")
            for region in report['missing_regions']:
                print(f"  - Page {region['page']}: \"{region['text'][:50]}...\"")
                print(f"    Image: {region['image_path']}")
        
        return report
    
    finally:
        diagnostics.close()
```

**Integration with UniversalParser:**
```python
# Add to universal_parser.py
class UniversalParser:
    # ... existing code ...
    
    def parse_with_diagnosis(self, pdf_path: str, output_dir: str = None) -> Tuple[Dict, Dict]:
        """
        Parse document and run extraction diagnosis.
        
        Returns:
            Tuple of (parsed_result, diagnosis_report)
        """
        # Run normal parsing
        parsed_result = self.parse(pdf_path, output_dir)
        
        # Run diagnosis
        diag_output_dir = output_dir or "diagnosis_output"
        diagnosis = diagnose_extraction(pdf_path, parsed_result, diag_output_dir)
        
        return parsed_result, diagnosis
```

---

## Quick Reference: Source Repositories

| Repository | URL | Main Value |
|------------|-----|------------|
| GoogleCloudPlatform/document-ai-samples | [Link](https://github.com/GoogleCloudPlatform/document-ai-samples) | Official samples, batch processing |
| GoogleCloudPlatform/document-ai-warehouse | [Link](https://github.com/GoogleCloudPlatform/document-ai-warehouse) | Full architecture, HITL |
| GoogleCloudPlatform/professional-services | [Link](https://github.com/GoogleCloudPlatform/professional-services) | Enterprise patterns |
| cocoindex-io/cocoindex | [Link](https://github.com/cocoindex-io/cocoindex) | RAG pipeline |
| ypratap11/invoice-processing-ai | [Link](https://github.com/ypratap11/invoice-processing-ai) | CI/CD + GCS |
| Hegghammer/daiR | [Link](https://github.com/Hegghammer/daiR) | API patterns, DataFrame export |
| ocrmypdf/OCRmyPDF | [Link](https://github.com/ocrmypdf/OCRmyPDF) | PDF type detection patterns |

---

## Implementation Priority

| Priority | Enhancement | Effort |
|----------|-------------|--------|
| 🔴 P1 | Multi-Processor Support | Medium |
| 🔴 P1 | Confidence Scores | Low |
| 🔴 P1 | Extraction Diagnosis & Gap Detection | Medium |
| 🟡 P2 | Table to DataFrame | Low |
| 🟡 P2 | PDF Type Detection | Medium |
| 🟡 P2 | Visualization Tools | Medium |
| 🟢 P3 | Batch Processing | Medium |
| 🟢 P3 | BigQuery Export | Medium |
| 🟢 P3 | GCS Integration | Medium |
| 🔵 P4 | HITL Workflow | High |
| 🔵 P4 | RAG Pipeline | High |


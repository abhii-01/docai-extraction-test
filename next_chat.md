# Document AI Exploration - Session Context

## Project Purpose

Testing Google Document AI Layout Parser for PDF text extraction. Goal is to extract paragraphs, tables, and diagrams from academic PDFs (economics textbooks) for taxonomy matching.

## Current Status

**Date:** Dec 6, 2025

**Latest Update:** Implemented `UniversalParser` class for robust, hierarchical extraction.

Key features added:
- **Hierarchical Tree Output:** JSON structure mirrors document layout (Sections -> Children).
- **Structured Table Extraction:** Tables preserved as 2D grids (rows/cols) with cell spans, not flattened text.
- **Visual Content Extraction:** Images, charts, and diagrams are automatically cropped and saved to disk; file paths are linked in the JSON tree.

## Key Files

| File | Purpose |
|------|---------|
| `docai_exploration.ipynb` | Main working notebook - run in Google Colab |
| `test6_universal_parser.ipynb` | **NEW:** Tests the `UniversalParser` class |
| `utils/universal_parser.py` | **NEW:** The core logic for hierarchical extraction |
| `utils/` | Helper modules (docai_client, table_converter, vision_llm) |
| `output/` | JSON results from extractions |

## How to Run the Universal Parser

1. Open `test6_universal_parser.ipynb` in Google Colab.
2. Run Setup cells (installs dependencies, clones repo).
3. Upload credentials and test PDF.
4. Run the parser.
5. Download `universal_parsed_result.json` and `extracted_images.zip`.

## Required Configuration

```python
DOCAI_PROJECT_ID = "your-project-id"
DOCAI_PROCESSOR_ID = "your-layout-parser-processor-id"
DOCAI_LOCATION = "us"  # or eu, asia
```

Also need: Google Cloud service account JSON file with Document AI access.

## Layout Parser Response Structure

The Layout Parser processor returns data differently than Document OCR:

| Field | Layout Parser | Document OCR |
|-------|---------------|--------------|
| `document.text` | Empty | Full text |
| `document.pages` | Empty | Pages with paragraphs |
| `document.document_layout.blocks` | Hierarchical blocks | Empty |

**Block hierarchy:** Headings contain nested paragraph blocks. Use `extract_blocks_recursively()` function to get all content.

## Output JSON Structure (Universal Parser)

```json
{
  "metadata": { ... },
  "structure": [
    {
      "id": "block_1",
      "type": "heading",
      "text": "1. Introduction",
      "children": [
        {
          "type": "paragraph",
          "text": "This is the intro..."
        },
        {
          "type": "table",
          "data": { "simple_matrix": [["Header"], ["Value"]] }
        }
      ]
    }
  ]
}
```

## Immediate Next Steps

1. Run `test6_universal_parser.ipynb` on your target PDFs.
2. Verify table reconstruction accuracy.
3. Verify image cropping quality.

---

## Improvement Plan (Strategic Roadmap)

### 1. Extraction Quality
- **Recursive Blocks:** Already implemented. Verify it captures arbitrary nesting depths.
- **Context-Aware Chunking:** Tag each paragraph with its parent heading (e.g., "Section: Economics").
- **Table Enhancement:** Use Layout Parser's `table_row`/`table_cell` structure to handle merged cells, not just raw text grids.

### 2. Cost & Performance
- **Selective Vision LLM:** Only send actual diagrams to GPT-4o, filter out decorative images.
- **Token Limits:** Truncate large tables before LLM narrative conversion.
- **Caching:** Store raw API responses to avoid re-calling API when changing parsing logic.

### 3. Reliability
- **Fallback:** If Layout Parser returns empty, try Document OCR or flag as "scanned PDF."
- **Validation:** Pre-check PDFs (not encrypted, has pages, etc.) before processing.

### 4. Maintainability
- **Unified Document Class:** Abstract Google API specifics into a clean internal model.
- **Golden Master Tests:** Keep a "blessed" output JSON for regression testing.

### 5. Integration
- **Schema Definition:** Create Pydantic model matching Taxonomy Tagger's expected input format.

---

## Repository

- Remote: `https://github.com/abhii-01/docai-extraction-test.git`
- Branch: `main`

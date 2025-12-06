# Document AI Exploration - Session Context

## Project Purpose

Testing Google Document AI Layout Parser for PDF text extraction. Goal is to extract paragraphs, tables, and diagrams from academic PDFs (economics textbooks) for taxonomy matching.

## Current Status

**Date:** Dec 6, 2025

**Latest Update:** Added recursive block extraction to handle Layout Parser's hierarchical response structure.

Key findings:
- Layout Parser returns `document.document_layout.blocks` (NOT `document.text` or `document.pages`)
- Blocks are **hierarchical** - paragraphs are nested inside headings/sections
- Initial extraction only got 5 top-level blocks (headings)
- Recursive extraction now captures all nested content

## Key Files

| File | Purpose |
|------|---------|
| `docai_exploration.ipynb` | Main working notebook - run in Google Colab |
| `archive/` | Old test notebooks (test1-5) for reference |
| `utils/` | Helper modules (docai_client, table_converter, vision_llm) |
| `output/` | JSON results from extractions |

## How to Run

1. Open `docai_exploration.ipynb` in Google Colab
2. Run Section 1 cells to set up:
   - Install dependencies
   - Upload credentials JSON
   - Set project ID and processor ID
   - Initialize client and verify
   - Upload PDF
3. Run Section 2 to process document
4. Run Section 3 to explore what the API returns (includes recursive extraction)
5. Run Section 4 to save and download results

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

## Output JSON Structure

```json
{
  "pdf_file": "...",
  "stats": {
    "top_level_blocks": 5,
    "total_blocks_recursive": 150,
    "block_type_counts": {"paragraph": 120, "heading-1": 5, ...}
  },
  "all_blocks": [
    {"id": "1", "parent_id": null, "depth": 0, "type": "heading-1", "text": "..."},
    {"id": "2", "parent_id": "1", "depth": 1, "type": "paragraph", "text": "..."}
  ]
}
```

## Immediate Next Steps

1. Run updated `docai_exploration.ipynb` on test PDF
2. Verify recursive extraction captures all paragraph content
3. If content is complete, start building extraction pipeline
4. If content is still missing, investigate block structure further

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


# Document AI Exploration - Session Context

## Project Purpose

Testing Google Document AI Layout Parser for PDF text extraction. Goal is to extract paragraphs, tables, and diagrams from academic PDFs (economics textbooks) for taxonomy matching.

## Current Status

**Date:** Dec 6, 2025

Restructured the project to use an exploratory approach:
- Archived old test notebooks (test1-test5)
- Created new `docai_exploration.ipynb` for general extraction first
- Approach: Extract everything, examine output, then tune

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
4. Run Section 3 to explore what the API returns
5. Run Section 4 to save and download results

## Required Configuration

```python
DOCAI_PROJECT_ID = "your-project-id"
DOCAI_PROCESSOR_ID = "your-layout-parser-processor-id"
DOCAI_LOCATION = "us"  # or eu, asia
```

Also need: Google Cloud service account JSON file with Document AI access.

## Known Issue

Previous test1 output only showed headings (5 blocks), missing paragraph content. The exploration notebook now captures:
- `document.text` - full OCR text
- `document.pages[].paragraphs` - page-level paragraphs
- `document.document_layout.blocks` - layout-detected blocks

Need to compare these to find the best extraction method.

## Next Steps

1. Run `docai_exploration.ipynb` on a test PDF
2. Review `exploration_output.json` to see what data is available
3. Decide which extraction path gives complete text:
   - `document.text` (raw OCR)
   - `document.pages.paragraphs` (page-structured)
   - `document.document_layout.blocks` (layout-detected)
4. Update extraction logic based on findings

## Repository

- Remote: `https://github.com/abhii-01/docai-extraction-test.git`
- Branch: `main`


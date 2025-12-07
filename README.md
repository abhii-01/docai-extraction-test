# Document AI Layout Parser - PDF Extraction Test Environment

Testing Google Document AI Layout Parser for extracting structured content (paragraphs, tables, diagrams) from academic PDFs for taxonomy matching.

---

## Project Status

**Last Updated:** December 2025

**Current State:** `UniversalParser` class implemented with:
- **Hierarchical Tree Output:** JSON structure mirrors document layout (Sections → Children)
- **Structured Table Extraction:** Tables preserved as 2D grids with cell spans (not flattened text)
- **Visual Content Extraction:** Images/charts/diagrams auto-cropped and saved; file paths linked in JSON

---

## Repository Structure

```
docai-test/
├── README.md                          # This file - full project context
├── env_template.txt                   # Configuration template
├── download_test_samples.py           # Download sample PDFs for testing
│
├── Notebooks:
│   ├── docai_exploration.ipynb        # Main working notebook (run in Colab)
│   └── test6_universal_parser.ipynb   # Tests UniversalParser class
│
├── utils/
│   ├── universal_parser.py            # Core hierarchical extraction logic
│   ├── docai_client.py                # Document AI API wrapper
│   ├── table_converter.py             # Table → markdown/narrative conversion
│   └── vision_llm.py                  # Flowchart description via Vision LLM
│
├── archive/                           # Previous test notebooks (test1-test5)
│   ├── test1_basic_extraction.ipynb
│   ├── test2_structure_detection.ipynb
│   ├── test3_table_handling.ipynb
│   ├── test4_flowchart_detection.ipynb
│   └── test5_full_pipeline.ipynb
│
├── credentials/                       # (gitignored) GCP service account JSON
├── sample_pdfs/                       # (gitignored) Test PDF files
└── output/                            # (gitignored) Extraction results
```

---

## Quick Start (Google Colab)

### 1. Open Notebook in Colab

**Option A - GitHub Import:**
1. Go to [Google Colab](https://colab.research.google.com/)
2. File → Open Notebook → GitHub
3. Enter: `abhii-01/docai-extraction-test`
4. Select `test6_universal_parser.ipynb`

**Option B - Upload:**
1. Download notebook from this repo
2. Upload to Colab via File → Upload Notebook

### 2. Run Setup Cells

Each notebook includes setup cells that:
1. Install dependencies (`google-cloud-documentai`, `openai`, `anthropic`, etc.)
2. Prompt to upload credentials JSON
3. Configure project/processor IDs
4. Clone repo and import utils

### 3. Upload Test PDF & Run

1. Upload your credentials JSON when prompted
2. Upload a test PDF
3. Run all cells sequentially
4. Download results (`universal_parsed_result.json`, `extracted_images.zip`)

---

## Required Configuration

### Google Cloud (Required)

```python
DOCAI_PROJECT_ID = "your-project-id"              # From Google Cloud Console
DOCAI_PROCESSOR_ID = "your-layout-parser-id"      # MUST be Layout Parser processor
DOCAI_LOCATION = "us"                             # or "eu", "asia"
```

**Setup Steps:**
1. Create Google Cloud project with billing enabled
2. Enable Document AI API
3. Create **Layout Parser** processor (NOT Document OCR)
4. Create service account → Download credentials JSON
5. Grant service account "Document AI Editor" role

**Console Links:**
- Processors: https://console.cloud.google.com/ai/document-ai/processors
- IAM: https://console.cloud.google.com/iam-admin/iam

### LLM API Keys (For table/flowchart conversion)

```python
# OpenAI (recommended)
OPENAI_API_KEY = "sk-your-key"
LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-4o"

# OR Anthropic (alternative)
ANTHROPIC_API_KEY = "sk-ant-your-key"
LLM_PROVIDER = "anthropic"
```

---

## Layout Parser vs Document OCR

The Layout Parser processor returns data differently:

| Field | Layout Parser | Document OCR |
|-------|---------------|--------------|
| `document.text` | Empty | Full text |
| `document.pages` | Empty | Pages with paragraphs |
| `document.document_layout.blocks` | **Hierarchical blocks** | Empty |

**Key Insight:** Headings contain nested paragraph blocks. Use `extract_blocks_recursively()` to traverse.

---

## Output JSON Structure

```json
{
  "metadata": {
    "source_file": "economics.pdf",
    "processor": "layout-parser",
    "extracted_at": "2025-12-06T..."
  },
  "structure": [
    {
      "id": "block_1",
      "type": "heading",
      "text": "1. Introduction",
      "children": [
        {
          "type": "paragraph",
          "text": "This chapter covers..."
        },
        {
          "type": "table",
          "data": {
            "simple_matrix": [["Header1", "Header2"], ["Value1", "Value2"]],
            "row_spans": [...],
            "col_spans": [...]
          }
        },
        {
          "type": "image",
          "image_path": "extracted_images/page1_img0.png",
          "bounding_box": {...}
        }
      ]
    }
  ]
}
```

---

## Key Files Explained

### `utils/universal_parser.py`
Core extraction logic. Key functions:
- `UniversalParser.parse(document)` - Main entry point
- `extract_blocks_recursively()` - Traverses hierarchical Layout Parser response
- `extract_table_structure()` - Preserves 2D grid with spans
- `crop_and_save_image()` - Extracts visual content to disk

### `utils/docai_client.py`
Google Document AI API wrapper:
- `get_client_from_env()` - Creates authenticated client
- `process_document(pdf_path)` - Sends PDF to Layout Parser

### `utils/table_converter.py`
Table processing utilities:
- `table_to_markdown(table_data)` - Converts 2D list to markdown
- `detect_table_type(table_data)` - Heuristic: comparison/time-series/summary
- `table_to_narrative(markdown, method)` - LLM-based narrative generation

### `utils/vision_llm.py`
Vision LLM integration for diagrams:
- `describe_image(image_path)` - Sends image to GPT-4V/Claude
- `is_diagram(image)` - Filters decorative images vs actual diagrams

---

## Sample PDFs for Testing

### Research Papers (Tables + Diagrams)
- **DocLayNet Paper:** https://arxiv.org/pdf/2206.01062.pdf
- **LayoutParser Paper:** https://arxiv.org/pdf/2103.15348.pdf
- **Attention Is All You Need:** https://arxiv.org/pdf/1706.03762.pdf

### Financial Documents (Complex Tables)
- **Apple SEC 10-K:** https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230930.pdf
- **Google Annual Reports:** https://abc.xyz/investor/

### Medical/Health (Structured Content)
- **WHO Lab Testing Guide:** https://www.who.int/docs/default-source/coronaviruse/laboratory-testing-for-2019-ncov-in-suspected-human-cases.pdf

### Datasets
- **DocLayNet:** https://github.com/DS4SD/DocLayNet (80K+ annotated pages)
- **PubLayNet:** https://github.com/ibm-aur-nlp/PubLayNet (360K+ scientific papers)

**Quick Download:**
```bash
python download_test_samples.py
```

---

## Cost Estimates

| Operation | Cost |
|-----------|------|
| Layout Parser (first 1K pages/month) | **FREE** |
| Layout Parser (after free tier) | $0.001/page |
| GPT-4o (table narratives) | ~$0.003/table |
| GPT-4V (flowchart descriptions) | ~$0.01/image |

**Example - 10,000 pages:**
- Document AI: ~$9 (after free tier)
- OpenAI for tables/diagrams: ~$8
- **Total: ~$17**

---

## Archived Tests (test1-test5)

The `archive/` folder contains previous iteration notebooks:

| Notebook | Purpose |
|----------|---------|
| `test1_basic_extraction.ipynb` | Basic text extraction validation |
| `test2_structure_detection.ipynb` | Paragraph/table/image detection |
| `test3_table_handling.ipynb` | Table → narrative with LLM |
| `test4_flowchart_detection.ipynb` | Diagram description with Vision LLM |
| `test5_full_pipeline.ipynb` | Combined pipeline |

These were superseded by `test6_universal_parser.ipynb` which uses the improved `UniversalParser` class.

---

## Improvement Roadmap

### Extraction Quality
- [ ] Verify recursive block extraction handles arbitrary nesting depths
- [ ] Add context-aware chunking (tag paragraphs with parent heading)
- [ ] Handle merged table cells via `table_row`/`table_cell` structure

### Cost & Performance
- [ ] Filter decorative images before sending to Vision LLM
- [ ] Truncate large tables before LLM narrative conversion
- [ ] Cache raw API responses for iteration without re-calling API

### Reliability
- [ ] Fallback to Document OCR if Layout Parser returns empty
- [ ] Pre-validate PDFs (not encrypted, has pages)

### Integration
- [ ] Create Pydantic model matching Taxonomy Tagger's expected input
- [ ] Golden master tests for regression testing

---

## Paths Reference

### GitHub Repository
```
https://github.com/abhii-01/docai-extraction-test
```

### Local Development Path
```
/Users/aadarsh/Documents/code/docai-test
```

### Related Project (Main Taxonomy Tagger)
```
/Users/aadarsh/Documents/code/llm syllabus portal
```

---

## Troubleshooting

### "Credentials upload failed" (Colab)
- Ensure uploading `.json` file (service account key)
- File should contain `"type": "service_account"`

### "Processor not found"
- Verify `DOCAI_PROCESSOR_ID` is correct
- Confirm it's a **Layout Parser** processor (not Document OCR)
- Check processor location matches `DOCAI_LOCATION`

### "Empty extraction results"
- Layout Parser returns data in `document.document_layout.blocks`, not `document.text`
- Use `extract_blocks_recursively()` function

### "Permission denied"
- Service account needs "Document AI Editor" or "Document AI API User" role
- Check IAM at: https://console.cloud.google.com/iam-admin/iam

### "Module not found" (Colab)
- Re-run pip install cell
- Restart runtime: Runtime → Restart Runtime

---

## Dependencies

```
google-cloud-documentai>=2.20.0
python-dotenv>=1.0.0
openai>=1.0.0
anthropic>=0.5.0
pdf2image>=1.16.0
Pillow>=10.0.0
```

Install via:
```bash
pip install google-cloud-documentai python-dotenv openai anthropic pdf2image Pillow
```

---

## License

MIT (or as specified by project owner)



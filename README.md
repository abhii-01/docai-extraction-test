# Document AI Layout Parser - PDF Extraction

Extract structured content (paragraphs, tables, diagrams) from PDFs using Google Document AI Layout Parser.

**Purpose:** Feed extracted content to Taxonomy Tagger for classification.

> **Git Push Note:** Always use `git push --no-verify` to skip pre-push hooks.

---

## Repository Structure

```
docai-test/
├── universal_parser.ipynb        # Main notebook (run in Colab)
├── utils/
│   ├── universal_parser.py       # Core extraction logic
│   ├── docai_client.py           # Document AI API wrapper
│   ├── table_converter.py        # Table → markdown/narrative
│   └── vision_llm.py             # Image description via Vision LLM
│
├── integration_docs/             # ⚠️ Cross-project docs (skip unless specified)
│   ├── ENHANCEMENT_ROADMAP.md    # Future features
│   └── EXTRACTION_OUTPUT_HANDLING.md  # Chunking rules for downstream
│
├── archive/                      # Old test notebooks (test1-test6)
├── credentials/                  # (gitignored) GCP service account JSON
├── sample_pdfs/                  # (gitignored) Test PDFs
└── output/                       # (gitignored) Extraction results
```

---

## Quick Start (Google Colab)

1. Open [Google Colab](https://colab.research.google.com/)
2. File → Open Notebook → GitHub → `abhii-01/docai-extraction-test`
3. Select `universal_parser.ipynb`
4. Upload credentials JSON + test PDF when prompted
5. Run all cells → Download `universal_parsed_result.json`

---

## Required Configuration

```python
# Google Cloud (Required)
DOCAI_PROJECT_ID = "your-project-id"
DOCAI_PROCESSOR_ID = "your-layout-parser-id"  # Must be Layout Parser
DOCAI_LOCATION = "us"

# LLM API (For table/image conversion)
OPENAI_API_KEY = "sk-your-key"
```

**GCP Setup:**
1. Enable Document AI API
2. Create **Layout Parser** processor (not Document OCR)
3. Create service account → Download JSON credentials

---

## Output JSON Structure

```json
{
  "metadata": { "source_file": "doc.pdf", "page_count": 10 },
  "structure": [
    {
      "id": "1",
      "type": "heading-1",
      "text": "Chapter Title",
      "page": 1,
      "children": [
        { "type": "paragraph", "text": "Content..." },
        { "type": "table", "data": { "simple_matrix": [[...]] } }
      ]
    }
  ]
}
```

**Block Types:** `heading-1/2/3`, `paragraph`, `table`, `image`, `list`, `footer`, `header`

---

## Key Technical Notes

### Layout Parser vs Document OCR

| Field | Layout Parser | Document OCR |
|-------|---------------|--------------|
| `document.text` | Empty | Full text |
| `document.document_layout.blocks` | **Hierarchical blocks** | Empty |

### Table Text Location

Text is in `cell.blocks[].text_block.text`, NOT in `cell.layout.text_anchor`.

---

## Related Projects

| Project | Path | Role |
|---------|------|------|
| **docai-test** (this) | `/Users/aadarsh/Documents/code/docai-test` | PDF → JSON extraction |
| **Taxonomy Tagger** | `/Users/aadarsh/Documents/code/llm syllabus portal` | Consumes chunks for tagging |

**Integration docs:** See `integration_docs/EXTRACTION_OUTPUT_HANDLING.md` for chunking rules.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty extraction | Use `document.document_layout.blocks`, not `document.text` |
| Processor not found | Verify it's **Layout Parser** (not OCR), check location |
| Permission denied | Service account needs "Document AI Editor" role |
| Colab cache issues | Delete `utils/`, re-clone repo, restart runtime |

---

## Dependencies

```bash
pip install google-cloud-documentai python-dotenv openai anthropic pdf2image Pillow
```

---

## Links

- **GitHub:** https://github.com/abhii-01/docai-extraction-test
- **Document AI Console:** https://console.cloud.google.com/ai/document-ai/processors

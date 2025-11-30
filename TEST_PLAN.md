# Document AI Test Plan

Complete testing plan for evaluating Google Document AI for your PDF extraction pivot.

## Overview

This test environment validates your **12 architectural decisions** for replacing pdfplumber with Google Document AI.

### What Gets Tested

✅ **Decision 1**: Google Document AI as primary extraction tool  
✅ **Decision 4**: Table → narrative conversion (with user selection simulation)  
✅ **Decision 5**: Vision LLM for flowchart description  
✅ **Decision 6**: Structure type tagging  
✅ **Decision 9**: Cost estimation and optimization  
✅ **Decision 10**: Phased implementation approach  

---

## Test Phases

### Phase 1: Basic Extraction (Test 1)

**File**: `tests/test1_basic_extraction.py`

**Purpose**: Validate that Document AI works and extracts clean text

**What It Does**:
- Authenticates with Google Document AI
- Processes a simple PDF
- Extracts raw text by page
- Compares OCR quality to original

**Success Criteria**:
- ✅ API connection successful
- ✅ Text extracted from all pages
- ✅ OCR accuracy > 90% (manual inspection)
- ✅ No garbled characters

**Run**:
```bash
python tests/test1_basic_extraction.py --pdf sample_pdfs/pdf1_simple.pdf
```

**Output**: `output/test1_raw_text.json`

---

### Phase 2: Structure Detection (Test 2)

**File**: `tests/test2_structure_detection.py`

**Purpose**: Verify Document AI detects paragraphs, tables, and images

**What It Does**:
- Detects paragraph boundaries
- Identifies table regions
- Finds image/diagram locations
- Tags each element with bounding boxes

**Success Criteria**:
- ✅ Paragraphs correctly segmented
- ✅ All tables detected
- ✅ Images located accurately
- ✅ Bounding boxes align with visual inspection

**Run**:
```bash
python tests/test2_structure_detection.py --pdf sample_pdfs/pdf2_academic.pdf
```

**Output**: `output/test2_structured.json`

---

### Phase 3: Table Handling (Test 3)

**File**: `tests/test3_table_handling.py`

**Purpose**: Convert tables to readable narrative paragraphs

**What It Does**:
- Extracts table cells into structured data
- Converts to markdown format
- Detects table type (time-series, comparison, summary)
- Uses LLM to generate narrative paragraph
- Compares original vs narrative

**Success Criteria**:
- ✅ Table data extracted correctly
- ✅ Markdown rendering valid
- ✅ Narrative preserves key information
- ✅ Narrative is human-readable

**Run**:
```bash
python tests/test3_table_handling.py --pdf sample_pdfs/pdf2_academic.pdf
```

**Output**: `output/test3_tables.json`

**Note**: This simulates your **Decision 4** (interactive table conversion). In production, you'd add user confirmation UI.

---

### Phase 4: Flowchart Detection (Test 4)

**File**: `tests/test4_flowchart_detection.py`

**Purpose**: Detect and describe flowcharts/diagrams with Vision LLM

**What It Does**:
- Detects image regions in PDF
- Filters for diagrams (vs photos)
- Extracts image from PDF
- Sends to GPT-4 Vision or Claude 3.5 Sonnet
- Generates narrative description

**Success Criteria**:
- ✅ Flowcharts correctly identified
- ✅ Photos/decorations filtered out
- ✅ Description captures key flow steps
- ✅ Description is taxonomy-matchable text

**Run**:
```bash
python tests/test4_flowchart_detection.py --pdf sample_pdfs/pdf3_textbook.pdf
```

**Output**: `output/test4_flowcharts.json`

---

### Phase 5: Full Pipeline (Test 5)

**File**: `tests/test5_full_pipeline.py`

**Purpose**: End-to-end extraction matching all 12 decisions

**What It Does**:
- Processes entire PDF
- Extracts paragraphs with OCR
- Converts tables to narrative
- Describes flowcharts with Vision LLM
- Tags each chunk with structure type
- Outputs chunks ready for taxonomy matching

**Success Criteria**:
- ✅ All elements extracted and tagged
- ✅ Each chunk has `structure_type` field
- ✅ Text quality matches manual extraction
- ✅ Ready for integration with `match_hierarchically()`

**Run**:
```bash
python tests/test5_full_pipeline.py --pdf sample_pdfs/pdf3_textbook.pdf
```

**Output**: `output/test5_full_pipeline.json`

**Output Format** (matches your taxonomy tagger needs):
```json
{
  "chunks": [
    {
      "chunk_id": "chunk_0001",
      "structure_type": "paragraph",
      "page": 1,
      "text": "Planning is an essential process...",
      "metadata": {
        "extraction_method": "document_ai_ocr"
      }
    },
    {
      "chunk_id": "chunk_0002",
      "structure_type": "table",
      "page": 2,
      "text": "The economic indicators show...",
      "metadata": {
        "extraction_method": "document_ai_table_detection",
        "conversion_method": "llm_narrative",
        "table_type": "time-series"
      }
    },
    {
      "chunk_id": "chunk_0003",
      "structure_type": "flowchart",
      "page": 3,
      "text": "This flowchart illustrates the planning process...",
      "metadata": {
        "extraction_method": "vision_llm"
      }
    }
  ]
}
```

---

## Running All Tests

```bash
# Activate environment
cd /Users/aadarsh/Documents/code/docai-test
source venv/bin/activate

# Run tests in sequence
python tests/test1_basic_extraction.py --pdf sample_pdfs/pdf1_simple.pdf
python tests/test2_structure_detection.py --pdf sample_pdfs/pdf2_academic.pdf
python tests/test3_table_handling.py --pdf sample_pdfs/pdf2_academic.pdf
python tests/test4_flowchart_detection.py --pdf sample_pdfs/pdf3_textbook.pdf
python tests/test5_full_pipeline.py --pdf sample_pdfs/pdf3_textbook.pdf
```

**Total Time**: ~5-10 minutes (depending on PDF size and LLM API speed)

---

## Quality Assessment Checklist

After running all tests, evaluate:

### OCR Quality
- [ ] Text accuracy > 90% (compare to original PDF)
- [ ] No major garbled sections
- [ ] Handles scanned text well
- [ ] Preserves formatting (paragraphs, line breaks)

### Table Detection
- [ ] All tables found
- [ ] Table boundaries correct
- [ ] Cell data extracted accurately
- [ ] Narrative preserves key information

### Flowchart Handling
- [ ] Diagrams detected (not photos)
- [ ] Descriptions capture main flow
- [ ] Descriptions are useful for taxonomy matching

### Structure Tagging
- [ ] Each chunk tagged correctly
- [ ] Bounding boxes accurate
- [ ] Metadata useful for debugging

### Cost
- [ ] Estimated cost for 10K pages acceptable
- [ ] No unexpected API charges
- [ ] Within budget projections

---

## Expected Results

### Test 1: Basic Extraction
- **Input**: 1-2 page simple PDF
- **Output**: Full text with ~95% accuracy
- **Time**: ~5 seconds
- **Cost**: ~$0.003

### Test 2: Structure Detection
- **Input**: 10-15 page academic paper
- **Output**: 50-100 paragraphs, 3-5 tables, 2-3 images
- **Time**: ~15 seconds
- **Cost**: ~$0.02

### Test 3: Table Handling
- **Input**: Same academic paper
- **Output**: 3-5 tables → narrative paragraphs
- **Time**: ~30 seconds (LLM calls)
- **Cost**: ~$0.03 (Document AI + GPT-4)

### Test 4: Flowchart Detection
- **Input**: 20-30 page textbook chapter
- **Output**: 2-5 diagrams → descriptions
- **Time**: ~45 seconds (Vision LLM calls)
- **Cost**: ~$0.05 (Document AI + GPT-4 Vision)

### Test 5: Full Pipeline
- **Input**: 20-30 page textbook
- **Output**: 100-200 chunks (paragraphs + tables + flowcharts)
- **Time**: ~2 minutes
- **Cost**: ~$0.08

**Total Testing Cost**: < $0.20

---

## Decision Validation

After testing, validate each of your 12 decisions:

| Decision | Test | Status | Notes |
|----------|------|--------|-------|
| 1. Google Document AI | All | ✅ | Quality acceptable? |
| 2. Reject LlamaParse | Test 1 | ✅ | Document AI better? |
| 3. Single-tool + post-process | Test 5 | ✅ | Pipeline works? |
| 4. Table → narrative | Test 3 | ✅ | Quality good? |
| 5. Vision LLM for flowcharts | Test 4 | ✅ | Descriptions useful? |
| 6. Structure tagging | Test 5 | ✅ | Tags correct? |
| 7. Document type detection | Test 2 | ✅ | Auto-detection works? |
| 8. Use pre-built processor | All | ✅ | Or need custom training? |
| 9. Cost budget | All | ✅ | Within $15-20/10K pages? |
| 10. Phased rollout | Tests 1-5 | ✅ | Each phase works? |
| 11. Minimal taxonomy changes | Test 5 | ✅ | Chunks compatible? |
| 12. Reliability > Cost | All | ✅ | Quality worth cost? |

---

## Integration Plan

If tests pass, integrate into main project:

### Step 1: Copy Utilities
```bash
cp -r /Users/aadarsh/Documents/code/docai-test/utils/* \
      "/Users/aadarsh/Documents/code/llm syllabus portal/utils/"
```

### Step 2: Update Notebook
Replace pdfplumber extraction in `pdf_taxonomy_tagger.ipynb` Cell 16:

**Old**:
```python
def extract_paragraphs_from_pdf(pdf_path: str):
    with pdfplumber.open(pdf_path) as pdf:
        # Simple extraction
```

**New**:
```python
def extract_paragraphs_from_pdf(pdf_path: str):
    from utils.docai_client import get_client_from_env
    client = get_client_from_env()
    document = client.process_document(pdf_path)
    # Use full pipeline from test5
```

### Step 3: Update Config
Add Document AI credentials to `secrets.json`:
```json
{
  "openai_api_key": "sk-...",
  "docai_project_id": "...",
  "docai_processor_id": "...",
  "docai_credentials": "credentials/docai-credentials.json"
}
```

### Step 4: Test on Real Data
Run on one of your economics textbooks:
```python
pdf_path = "economics1.pdf"
results = process_pdf(pdf_path, MATCHING_CONFIG, TAXONOMY)
```

### Step 5: Compare Results
Compare pdfplumber vs Document AI:
- Extraction quality
- Taxonomy match rates
- Processing time
- Cost

---

## Troubleshooting

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed troubleshooting.

Common issues:
- **"Credentials not found"**: Check .env file
- **"Processor not accessible"**: Verify IAM permissions
- **"Table extraction empty"**: PDF may not have actual tables
- **"Vision LLM failed"**: Check OpenAI/Anthropic API key

---

## Next Steps

1. ✅ Complete Google Cloud setup
2. ✅ Run all 5 tests
3. ✅ Review quality of results
4. ✅ Validate cost projections
5. ✅ Decide: Integrate or iterate
6. ✅ If integrating: Follow integration plan above
7. ✅ If iterating: Adjust prompts/settings and re-test

---

## Success Metrics

**Minimum viable quality**:
- OCR accuracy > 90%
- Table detection > 80%
- Flowchart descriptions usable
- Cost < $25 per 10K pages
- Pipeline completes without errors

**Ideal quality**:
- OCR accuracy > 95%
- Table detection > 95%
- Flowchart descriptions excellent
- Cost < $20 per 10K pages
- Ready for production integration

---

Good luck with testing! 🚀


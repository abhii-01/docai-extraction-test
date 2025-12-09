# Image Detection & JSON Insertion Task

> **Purpose:** This file summarizes a discussion about fixing image detection in the Document AI pipeline. Use this as context for continuing the task.
> 
> **Last Updated:** Dec 2024 (Debug session completed)

---

## Problem Statement

**Goal:** Detect images/diagrams in PDFs, extract them, send to Vision LLM, and insert the LLM description back into the JSON at the correct position (preserving reading order).

**Current Issue:** Images are NOT appearing in the parsed JSON output (`universal_parsed_result.json`), even though the PDFs contain diagrams and charts.

---

## Debug Session Results (Dec 2024)

We added debug cells to `universal_parser.ipynb` and ran them against a test PDF. Here are the critical findings:

### Debug Output Summary

| Check | Result |
|-------|--------|
| `raw_doc.pages` | **EMPTY** (0 pages) |
| `raw_doc.pages[i].visual_elements` | Cannot check - pages array is empty |
| `raw_doc.pages[i].blocks` | Cannot check - pages array is empty |
| `raw_doc.pages[i].image` | Cannot check - pages array is empty |
| `raw_doc.document_layout.blocks` | 5 blocks (1 header, 4 heading-1) |
| Image blocks (`image_block`) found | **NONE** |

### Key Discovery: Layout Parser vs Enterprise OCR

The **Layout Parser processor** behaves DIFFERENTLY from Enterprise Document OCR:

| Field | Layout Parser (Current) | Enterprise OCR |
|-------|-------------------------|----------------|
| `doc.pages` | **EMPTY** | Populated with page data |
| `doc.pages[i].visual_elements` | N/A (no pages) | Contains images/figures |
| `doc.document_layout.blocks` | Hierarchical structure | Empty |
| `doc.text` | Empty | Full document text |

**ROOT CAUSE:** The Layout Parser processor does NOT populate the `pages` array. It only populates `document_layout.blocks`. This means:
- `visual_elements` cannot be accessed (it lives under `pages`)
- No bounding boxes for images are available
- Images in the PDF are being OCR'd as text fragments instead of detected as image blocks

### Evidence of Image-as-Text Problem

In the JSON output, we see fragmented text that clearly came from infographics/charts:
- Page 8: `"6 PILLARS OF PMJDY"`, `"BANK ΞΞΞ"`, `"00"`, `"$"`, `"盘"` (infographic text)
- Page 6: `"31000"`, `"100"`, `"10000"`, `"Scan QR code for"` (advertisement/chart text)

The Layout Parser is extracting TEXT from images but not detecting them AS images.

---

## Key Findings (Updated)

### 1. Poppler Dependency Issue (Partial Cause)
- **Warning observed:** `Unable to get page count. Is poppler installed and in PATH?`
- **Impact:** `pdf2image` fails → `_save_crop()` cannot extract image files → images may be skipped in output.
- **Status:** Needs to be installed, but this is only for *cropping* the image, not for *detecting* it.

### 2. Layout Parser Does NOT Return Image Bounding Boxes
- **Original assumption:** Images would be in `doc.pages[i].visual_elements`
- **Reality:** Layout Parser returns `doc.pages` as EMPTY
- **Implication:** Cannot use `visual_elements` approach with Layout Parser

### 3. No `image_block` in document_layout.blocks
- We checked `document_layout.blocks` for any blocks with `image_block` attribute
- Result: **Zero image blocks found**
- All content is being returned as text blocks (header, heading-1, paragraph, table)

---

## Files to Read

| File | Purpose |
|------|---------|
| `utils/universal_parser.py` | Core parsing logic — needs update |
| `utils/docai_client.py` | Document AI API wrapper |
| `utils/vision_llm.py` | Vision LLM integration (already exists) |
| `universal_parser.ipynb` | **Contains debug cells** (cells 10-16) for inspecting raw API response |

---

## Sample JSON Outputs (For Reference)

Located in user's Downloads folder:
- `universal_parsed_result (5).json` — No images detected
- `universal_parsed_result (6).json` — No images detected, Poppler warning
- `universal_parsed_result (7).json` — Latest test, confirms no image blocks

---

## Possible Solutions (To Investigate)

### Option A: Switch to Enterprise Document OCR Processor
- Create a new processor of type "Enterprise Document OCR" in GCP Console
- This processor DOES populate `doc.pages` with `visual_elements`
- Downside: May lose hierarchical structure from Layout Parser

### Option B: Use Both Processors (Hybrid Approach)
1. Use Layout Parser for hierarchical text structure
2. Use Enterprise OCR for image detection
3. Merge results by matching page numbers and positions

### Option C: Add Nested Block Inspection
- The current debug only checks top-level `document_layout.blocks`
- Images might be nested INSIDE text blocks
- Need recursive inspection of all nested blocks for `image_block` attribute

### Option D: Use pdf2image + Computer Vision
- Bypass Document AI for image detection
- Use pdf2image to render each page as image
- Use a separate CV model to detect image regions
- Then crop and send to Vision LLM

---

## Next Steps (Revised)

### Step 1: Add Recursive Block Inspection
Add debug cell to recursively check ALL nested blocks in `document_layout.blocks`:
```python
def find_image_blocks(blocks, depth=0):
    for block in blocks:
        if getattr(block, 'image_block', None):
            print(f"{'  '*depth}FOUND IMAGE_BLOCK!")
        # Check nested blocks in text_block
        text_block = getattr(block, 'text_block', None)
        if text_block:
            nested = getattr(text_block, 'blocks', [])
            if nested:
                find_image_blocks(nested, depth+1)
```

### Step 2: Test with Enterprise OCR Processor
- Create new processor in GCP Console (type: Enterprise Document OCR)
- Update `DOCAI_PROCESSOR_ID` in notebook
- Re-run debug cells to see if `pages` is populated

### Step 3: Document Processor Comparison
- Compare outputs from Layout Parser vs Enterprise OCR
- Determine if hybrid approach is needed

---

## Configuration

```python
DOCAI_PROJECT_ID = "vudr0311"
DOCAI_PROCESSOR_ID = "91f4e596a0b1c39d"  # Layout Parser
DOCAI_LOCATION = "us"
```

---

## Expected Output Structure (After Fix)

```json
{
  "id": "img_001",
  "type": "image",
  "page": 2,
  "bbox": [0.1, 0.3, 0.5, 0.7],
  "file_path": "output/images/img_001.png",
  "description": "This flowchart shows the process of..."  // From Vision LLM
}
```

---

## Two-Pass Workflow Design

1. **Pass 1 (Extraction):**
   - Parse PDF with Document AI
   - Detect images (method TBD based on processor choice)
   - Save cropped images to disk using pdf2image
   - Output JSON with image placeholders (no description yet)

2. **Pass 2 (LLM Integration):**
   - Read image files
   - Send to Vision LLM for descriptions
   - Merge descriptions back into JSON

---

## Related Context

- **Repository:** `/Users/aadarsh/Documents/code/docai-test`
- **Main Entry Point:** `universal_parser.ipynb` (Google Colab)
- **Downstream Consumer:** Taxonomy Tagger at `/Users/aadarsh/Documents/code/llm syllabus portal`
- **Git Push:** Always use `git push --no-verify`

---

## Debug Cells in Notebook

The following debug cells were added to `universal_parser.ipynb` (cells 10-16):

1. **Cell 10** - Markdown header for debug section
2. **Cell 11** - Capture raw Document AI response
3. **Cell 12** - List all top-level document attributes  
4. **Cell 13** - Check `doc.pages[i].visual_elements`
5. **Cell 14** - Check `doc.pages[i].blocks`
6. **Cell 15** - Check `doc.pages[i].image`
7. **Cell 16** - Analyze `document_layout.blocks` type distribution

These cells remain in the notebook for future debugging.


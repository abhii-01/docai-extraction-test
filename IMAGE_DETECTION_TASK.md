# Image Detection & JSON Insertion Task

> **Purpose:** This file summarizes a discussion about fixing image detection in the Document AI pipeline. Use this as context for continuing the task.

---

## Problem Statement

**Goal:** Detect images/diagrams in PDFs, extract them, send to Vision LLM, and insert the LLM description back into the JSON at the correct position (preserving reading order).

**Current Issue:** Images are NOT appearing in the parsed JSON output (`universal_parsed_result.json`), even though the PDFs contain diagrams and charts.

---

## Key Findings

### 1. Poppler Dependency Issue (Partial Cause)
- **Warning observed:** `Unable to get page count. Is poppler installed and in PATH?`
- **Impact:** `pdf2image` fails → `_save_crop()` cannot extract image files → images may be skipped in output.
- **Status:** Needs to be installed, but this is only for *cropping* the image, not for *detecting* it.

### 2. Google Document AI DOES Detect Images (Clarification)
- **What it provides:** Bounding box coordinates (location) of images.
- **What it does NOT provide:** The actual image file (pixels). That's why we use `pdf2image` to crop.

### 3. Likely Root Cause: Wrong Location in API Response
The current parser only looks at:
```python
doc.document_layout.blocks
```

But Google Document AI often returns images in a **different location**:
```python
doc.pages[i].visual_elements  # <-- Images/diagrams often here
```

**Action Required:** Update `universal_parser.py` to also check `visual_elements`.

---

## Files to Read

| File | Purpose |
|------|---------|
| `utils/universal_parser.py` | Core parsing logic — needs update to check `visual_elements` |
| `utils/docai_client.py` | Document AI API wrapper — add logging to inspect raw response |
| `utils/vision_llm.py` | Vision LLM integration (already exists, use for descriptions) |
| `integration_docs/EXTRACTION_OUTPUT_HANDLING.md` | Chunking rules for downstream (context on JSON structure) |

---

## Sample JSON Outputs (For Reference)

Located in user's Downloads folder:
- `universal_parsed_result (5).json` — No images detected
- `universal_parsed_result (6).json` — No images detected, Poppler warning was shown

---

## Next Steps (Action Items)

### Step 1: Install Poppler (macOS)
```bash
brew install poppler
```
Then verify: `pdftoppm -v`

### Step 2: Add Debug Logging to See Raw API Response
In `utils/docai_client.py`, after processing, log:
- `doc.document_layout.blocks` (current location)
- `doc.pages[i].visual_elements` (likely image location)
- `doc.pages[i].image` (alternative location)

### Step 3: Update Parser to Extract Images from `visual_elements`
Modify `utils/universal_parser.py`:
1. After parsing `document_layout.blocks`, also iterate through `doc.pages`.
2. For each page, check `visual_elements` for image/figure types.
3. Extract bbox, page number, and create image nodes.

### Step 4: Create JSON Merger Utility
Create `utils/json_merger.py`:
1. Accept parsed JSON + list of image descriptions (from Vision LLM).
2. Match descriptions to images by ID.
3. Insert description nodes at correct positions in the JSON hierarchy.

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
   - Detect images from `visual_elements`
   - Save cropped images to disk
   - Output JSON with image placeholders (no description yet)

2. **Pass 2 (LLM Integration):**
   - Read image files
   - Send to Vision LLM for descriptions
   - Merge descriptions back into JSON using `json_merger.py`

---

## Related Context

- **Repository:** `/Users/aadarsh/Documents/code/docai-test`
- **Main Entry Point:** `universal_parser.ipynb` (Google Colab)
- **Downstream Consumer:** Taxonomy Tagger at `/Users/aadarsh/Documents/code/llm syllabus portal`


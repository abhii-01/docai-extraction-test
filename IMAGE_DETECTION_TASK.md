# Image Detection & JSON Insertion Task

> **Purpose:** This file summarizes the image detection problem and solution attempts. Use this as context for continuing the task.
> 
> **Last Updated:** Dec 11, 2024 (Session 2)

---

## Current Status: ✅ PARTIALLY SOLVED

| Component | Status | Notes |
|-----------|--------|-------|
| Embedded images (photos, scans) | ✅ Working | PyMuPDF extracts with exact boundaries |
| Vector graphics (charts, diagrams) | ❌ Blocked | LayoutParser/Detectron2 fails in Colab |
| Image descriptions | ✅ Working | GPT-4o describes extracted images |
| Standalone pipeline | ✅ Created | `image_extractor.ipynb` |
| Merge with universal_parser | ⏳ Pending | To be implemented |

### What Works Right Now
```python
extractor = ImageExtractor(
    use_layoutparser=False,      # ← Must be False (Detectron2 broken)
    generate_descriptions=True   # ← Works with OpenAI API key
)
```
- ✅ Extracts all embedded images (JPG/PNG/etc stored in PDF)
- ✅ Gets exact bounding boxes from PDF metadata
- ✅ Generates descriptions via GPT-4o
- ❌ Cannot detect vector charts/infographics (needs LayoutParser)

---

## Problem Statement

**Goal:** Detect images/diagrams in PDFs, extract them, send to Vision LLM, and insert the LLM description back into the JSON at the correct position.

**Original Issue:** Google Doc AI Layout Parser does NOT detect images. They get OCR'd as text fragments instead.

---

## Solution Journey

### Option C: Recursive Block Inspection - ❌ FAILED

**Tested:** Dec 11, 2024

Added comprehensive debug cell to `universal_parser.ipynb` (Cell 17) that recursively inspects all 400 blocks across 3 nesting levels.

**Result:**
```
🎯 IMAGE_BLOCK found: 0
🎯 Visual-type blocks found: 0
Blocks with valid bbox: 0/400
```

**Conclusion:** Layout Parser genuinely does NOT detect images at any level. Moving to Option D.

---

### Option D: pdf2image + Vision LLM - ⚠️ EVOLVED

**Initial Attempt:** Send full page to GPT-4o, ask it to return bounding boxes.

**Problem:** GPT-4o's bounding box estimates were inaccurate — crops cut images incorrectly, losing information.

**Revised Approach:** Hybrid detection pipeline:
1. **PyMuPDF** - Extract embedded images (exact boundaries, FREE)
2. **LayoutParser** - Detect figure regions (vector charts, FREE)
3. **GPT-4o** - Describe ONLY extracted images (cost-efficient)

---

## Current Implementation

### New File: `image_extractor.ipynb`

Standalone notebook with hybrid detection:

```
PDF
 │
 ├─→ PyMuPDF ─────────────→ Embedded images (exact boundaries)
 │
 ├─→ LayoutParser ────────→ Figure regions (vector charts)
 │
 └─→ Deduplicate ─────────→ Remove overlapping duplicates
          │
          ↓
      GPT-4o Vision ────────→ Descriptions (per image, not per page)
          │
          ↓
      image_extractions.json
```

### Key Features

| Feature | Description |
|---------|-------------|
| PyMuPDF extraction | Extracts actual embedded images with exact coordinates |
| LayoutParser detection | Detects "Figure" type regions (requires Detectron2) |
| Deduplication | Removes duplicates with >50% IoU overlap |
| Cost-efficient LLM | Only sends extracted images, not full pages |
| Configurable | Can disable LayoutParser or descriptions |

### Output JSON Structure

```json
{
  "metadata": {
    "source_file": "document.pdf",
    "page_count": 10,
    "images_found": 5,
    "methods_used": {
      "pymupdf": true,
      "layoutparser": false,
      "descriptions": true
    }
  },
  "images": [
    {
      "id": "img_001",
      "page": 1,
      "type": "embedded",
      "source": "pymupdf",
      "bbox": [0.1, 0.2, 0.6, 0.8],
      "file_path": "image_output/images/page1_img_001.png",
      "description": "Bar chart showing GDP growth 2010-2024"
    }
  ]
}
```

---

## Known Issues

### LayoutParser/Detectron2 in Colab

**Problem:** LayoutParser requires Detectron2, which has compatibility issues with Colab's Python 3.12 environment.

**Error:**
```
⚠️ Could not load LayoutParser model: module layoutparser has no attribute Detectron2LayoutModel
```

**Workaround:** Set `use_layoutparser=False` — PyMuPDF still extracts embedded images.

**Impact:** Without LayoutParser, vector graphics (charts made with shapes/lines) may be missed. Only actual embedded images (JPG/PNG stored in PDF) are extracted.

---

## Files Reference

| File | Purpose |
|------|---------|
| `image_extractor.ipynb` | **NEW** - Standalone image extraction pipeline |
| `universal_parser.ipynb` | Text extraction (contains debug cells 10-17) |
| `utils/universal_parser.py` | Core text parsing logic |
| `utils/vision_llm.py` | Vision LLM integration |

---

## Priority Order for Future Work

1. ~~**Option C** - Recursive block inspection~~ ❌ Tested, failed
2. **Option D** - PyMuPDF + LayoutParser ✅ Implemented (LayoutParser has issues)
3. **Option B** - Hybrid with Enterprise OCR (if needed, costs more)

---

## Next Steps

### Immediate
1. **Fix LayoutParser** - Try alternative detection models or wait for Colab update
2. **Test with more PDFs** - Verify PyMuPDF extraction works consistently

### Future
1. **Merge pipelines** - Combine `image_extractor.ipynb` output with `universal_parser.ipynb` output
2. **Position matching** - Insert images at correct positions in document structure (currently page-level only)

---

## Configuration

### image_extractor.ipynb

```python
extractor = ImageExtractor(
    output_dir="image_output",
    use_layoutparser=False,      # Disable if Detectron2 fails
    generate_descriptions=True   # Set False to skip LLM costs
)
```

### universal_parser.ipynb

```python
DOCAI_PROJECT_ID = "vudr0311"
DOCAI_PROCESSOR_ID = "91f4e596a0b1c39d"  # Layout Parser
DOCAI_LOCATION = "us"
```

---

## Related Context

- **Repository:** `/Users/aadarsh/Documents/code/docai-test`
- **GitHub:** https://github.com/abhii-01/docai-extraction-test
- **Downstream Consumer:** Taxonomy Tagger at `/Users/aadarsh/Documents/code/llm syllabus portal`
- **Git Push:** Always use `git push --no-verify`

---

## Debug Cells in universal_parser.ipynb

| Cell | Purpose |
|------|---------|
| Cell 10-16 | Original debug cells for inspecting Document AI response |
| Cell 17 | **NEW** - Comprehensive image detection diagnosis |

Cell 17 provides:
- Basic document stats
- Sample block attributes
- Recursive block inspection (Option C test)
- Pages array check
- Image indicators in text
- Summary with recommendation

---

## Cost Analysis

| Approach | What Goes to LLM | Cost (10-page PDF) |
|----------|-----------------|-------------------|
| Old (full page to GPT-4o) | Every page | ~$0.30 |
| New (images only) | Only 5 images | ~$0.05 |

---

## Changelog

### Dec 11, 2024 (Session 2)
- Tested `image_extractor.ipynb` with `test_doc_ai (2).pdf`
- LayoutParser/Detectron2 still fails in Colab (Python 3.12 compatibility)
- Tried multiple Detectron2 installation methods - all failed
- **PyMuPDF extraction confirmed working** - extracts embedded images correctly
- Recommendation: Use `use_layoutparser=False` until Detectron2 is fixed

### Dec 11, 2024 (Session 1)
- Tested Option C (recursive inspection) - FAILED
- Implemented Option D (pdf2image + Vision)
- Discovered GPT-4o bbox estimation is inaccurate
- Pivoted to PyMuPDF + LayoutParser hybrid approach
- Created `image_extractor.ipynb`
- Encountered LayoutParser/Detectron2 Colab compatibility issues
- Documented current state and next steps

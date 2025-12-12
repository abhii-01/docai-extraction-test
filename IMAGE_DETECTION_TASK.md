# Image Detection & Extraction Task

> **Status:** ✅ COMPLETED  
> **Last Updated:** Dec 12, 2025

---

## Summary

Implemented a two-tier image extraction pipeline in `image_extractor.ipynb` that detects **both** embedded raster images and vector figures from PDFs.

| Tier | Tool | What It Detects | Status |
|------|------|-----------------|--------|
| **1** | PyMuPDF | Embedded images (JPG/PNG stored in PDF) | ✅ Working |
| **2** | PaddleOCR PP-Structure | Vector figures (charts, diagrams, flowcharts) | ✅ Working |
| **3** | GPT-4o Vision | Image descriptions | ✅ Working |

---

## Why Two Tiers?

**PyMuPDF** and **PaddleOCR** detect fundamentally different things:

| Aspect | PyMuPDF | PaddleOCR |
|--------|---------|-----------|
| **How it works** | Extracts actual image files stored inside PDF | Renders page as screenshot, uses ML to find figures |
| **Detects** | Photos, scans, logos (embedded files) | Charts, diagrams, flowcharts (vector graphics) |
| **Quality** | Original quality | Limited by render DPI (150) |
| **Speed** | Very fast (no ML) | Slower (~2-3s per page) |
| **Misses** | Vector graphics (drawn with lines) | Nothing, but may have false positives |

**Both are needed** - PyMuPDF gives original quality for embedded images, PaddleOCR catches everything else.

---

## Implementation

### Files
| File | Purpose |
|------|---------|
| `image_extractor.ipynb` | Main extraction pipeline (run in Colab) |
| `universal_parser.ipynb` | Text/table extraction - DO NOT TOUCH |

### Dependencies (Cell 2)
```python
%pip install -q pymupdf pdf2image openai Pillow
%pip install -q "numpy<2.0" paddlepaddle==2.6.2 paddleocr==2.8.1
```

### Pipeline Flow
1. **PyMuPDF** extracts embedded images with bounding boxes
2. **PaddleOCR** renders pages and detects figure regions
3. **Deduplication** removes overlaps (IoU > 0.5)
4. **GPT-4o Vision** generates descriptions for unique images

---

## Key Caveats & Fixes

### 1. PaddleOCR Version Pinning (CRITICAL)
```python
# ❌ DON'T USE (broken)
%pip install paddleocr

# ✅ USE THIS (stable)
%pip install -q "numpy<2.0" paddlepaddle==2.6.2 paddleocr==2.8.1
```

**Why:** PaddleOCR 3.x has PaddleX dependency with singleton initialization issues. Version 2.8.1 is stable.

### 2. NumPy Compatibility
```python
%pip install -q "numpy<2.0"
```

**Why:** PaddlePaddle 2.6.2 requires NumPy 1.x. NumPy 2.0 breaks with `ModuleNotFoundError: No module named 'numpy.strings'`.

### 3. Colab Runtime Restart
After installing dependencies in Cell 2, **restart the runtime** before running other cells.

### 4. Poppler Requirement
`pdf2image` requires `poppler-utils` system package:
```python
# Installed automatically in Colab
!apt-get install -y -qq poppler-utils
```

---

## Tested Results

### Test 1: PDF with Embedded Images
- PyMuPDF: 7 images ✅
- PaddleOCR: 0 figures (correct - no vector graphics)

### Test 2: PDF with Vector Charts Only
- PyMuPDF: 0 images (correct - no embedded files)
- PaddleOCR: 4 figures ✅ (bar chart, flowchart, pie chart, line chart)

---

## What Was Tried & Failed

| Approach | Issue |
|----------|-------|
| **Surya** | `ModuleNotFoundError: No module named 'surya.model'` - API broke between versions |
| **LayoutParser/Detectron2** | Broken on Python 3.12, complex CUDA dependencies |
| **PaddleOCR 3.x** | `RuntimeError: PDX has already been initialized` - singleton pattern issue |
| **NumPy 2.0** | `ModuleNotFoundError: No module named 'numpy.strings'` with PaddlePaddle |

---

## Output JSON Structure

```json
{
  "metadata": {
    "source_file": "document.pdf",
    "page_count": 10,
    "images_found": 7,
    "methods_used": { "pymupdf": true, "paddleocr": true, "descriptions": true },
    "stats": {
      "pymupdf_images": 4,
      "paddleocr_figures": 5,
      "duplicates_removed": 2
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
      "description": "Photograph of laboratory equipment"
    }
  ]
}
```

---

## Quick Start

1. Open `image_extractor.ipynb` in [Google Colab](https://colab.research.google.com/)
2. Run Cell 2 (dependencies) → **Restart runtime**
3. Set `OPENAI_API_KEY` in Cell 3
4. Upload PDF in Cell 4
5. Run remaining cells

---

## Related

- **Repository:** https://github.com/abhii-01/docai-extraction-test
- **Git push:** Always use `git push --no-verify`
- **Text/Tables:** Handled by `universal_parser.ipynb` (Google Layout Processor)

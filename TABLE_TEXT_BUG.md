# Table Text Extraction Bug

## Status: 🔴 UNRESOLVED

## Problem Summary

Tables are being **detected** by Document AI Layout Parser, but the **text content inside table cells is not being extracted**.

### Evidence

**From `docai_exploration.ipynb`:**
```
TABLES
============================================================
Total tables found: 0
```
(Even after fix to check `document.document_layout.blocks`, tables may still show 0 if they're nested)

**From `test6_universal_parser.ipynb` (`universal_parsed_result.json`):**
- Tables ARE detected (5 tables found with structure)
- But `simple_matrix` contains empty strings:
```json
{
  "type": "table",
  "data": {
    "simple_matrix": [
      ["", "", ""],
      ["", "", ""]
    ]
  }
}
```

---

## Root Cause Analysis

### Why `document.text` is Empty

The Layout Parser processor returns text in a **different location** than expected:
- **Expected:** `document.text` contains all OCR text, and `text_anchor` indices point into it
- **Actual:** `document.text` is **empty** (0 characters), but text exists in `block.text_block.text`

### Why Table Cells Have No Text

1. **Standard Method Failed:** 
   - `_extract_table_grid()` tries to use `cell.layout.text_anchor` to get text from `document.text`
   - Since `document.text` is empty, this returns nothing

2. **Fallback Method (Spatial Matching) - Attempted but Unclear if Working:**
   - Added fallback to find child `text_block.blocks` inside table cells by bounding box
   - **Problem:** Table blocks may not have `text_block.blocks` children - the text might be stored differently

---

## What Was Attempted

### Attempt 1: Text Fallback in `_visit_block()`
**File:** `utils/universal_parser.py`

```python
# In _visit_block(), for text blocks:
extracted_text = self._get_text(text_anchor, full_text)

# Fallback to block.text_block.text if anchor extraction failed
if not extracted_text:
    extracted_text = getattr(text_block, 'text', "") or ""
```

**Result:** ✅ Works for paragraphs/headings, ❌ Does NOT help tables

### Attempt 2: Spatial Matching for Table Cells
**File:** `utils/universal_parser.py`

```python
# In _extract_table_grid(), if standard extraction fails:
if not cell_text and child_text_blocks and cell_layout:
    cell_bbox = getattr(cell_layout, 'bounding_poly', None)
    if cell_bbox:
        cell_rect = self._normalize_bbox(cell_bbox)
        for child in child_text_blocks:
            child_rect = self._normalize_bbox(child_layout.bounding_poly)
            if self._is_contained(child_rect, cell_rect):
                matched_texts.append(child_tb.text)
        cell_text = " ".join(matched_texts)
```

**Result:** ❌ Not working - likely because `block.text_block.blocks` is empty for table blocks

### Attempt 3: Updated Table Detection in `docai_exploration.ipynb`
**Cell 35:** Added check for `document.document_layout.blocks` with `table_block` attribute

**Result:** ⚠️ Partially helps detection count, but doesn't solve text extraction

---

## Hypotheses to Investigate

### Hypothesis 1: Table Text is in Different Location
The text for table cells might be stored in:
- `table_block.body_rows[].cells[].blocks[]` (nested blocks inside cells)
- A separate text layer not connected to the table structure
- Only in `document.text` for **non-Layout Parser** processors (Form Parser, OCR)

### Hypothesis 2: Layout Parser Doesn't Extract Table Text
The Layout Parser might be designed for **structure detection** only, and a different processor (Form Parser) is needed for table content extraction.

### Hypothesis 3: Need to Use `page.tables` Instead
For table text, might need to use the legacy `document.pages[].tables[]` structure instead of `document.document_layout.blocks[]`.

---

## Next Steps to Debug

### Step 1: Raw API Inspection
Add this debug code to `docai_exploration.ipynb` to inspect table block structure:

```python
# Find table blocks and inspect their full structure
for block in doc_layout.blocks:
    if hasattr(block, 'table_block') and block.table_block:
        print(f"Table Block ID: {block.block_id}")
        print(f"  Has text_block: {hasattr(block, 'text_block') and block.text_block is not None}")
        
        tb = block.table_block
        print(f"  Header rows: {len(tb.header_rows) if tb.header_rows else 0}")
        print(f"  Body rows: {len(tb.body_rows) if tb.body_rows else 0}")
        
        # Inspect first cell
        if tb.body_rows:
            first_row = tb.body_rows[0]
            if first_row.cells:
                cell = first_row.cells[0]
                print(f"  First cell attributes: {[a for a in dir(cell) if not a.startswith('_')]}")
                if hasattr(cell, 'layout') and cell.layout:
                    print(f"    Cell layout.text_anchor: {cell.layout.text_anchor}")
                if hasattr(cell, 'blocks') and cell.blocks:
                    print(f"    Cell has nested blocks: {len(cell.blocks)}")
```

### Step 2: Try Form Parser
Test with a **Form Parser** processor instead of Layout Parser to see if table text extraction works differently.

### Step 3: Check `page.tables` Structure
```python
# Check if page-level tables have text
if document.pages:
    for page in document.pages:
        if page.tables:
            for table in page.tables:
                # Check header rows
                for row in (table.header_rows or []):
                    for cell in (row.cells or []):
                        # Try to get text from cell
                        if cell.layout and cell.layout.text_anchor:
                            # This needs document.text to work
                            pass
```

---

## Files Modified (For Reference)

| File | Changes Made |
|------|--------------|
| `utils/universal_parser.py` | Added text fallback, spatial matching for tables, `_is_contained()` method |
| `docai_exploration.ipynb` | Updated Cell 35 to check `document.document_layout.blocks` for tables |

---

## Related Links

- [Document AI Layout Parser Docs](https://cloud.google.com/document-ai/docs/processors-list#processor_layout-parser)
- [Document AI Table Extraction](https://cloud.google.com/document-ai/docs/handle-response#tables)
- Enhancement Roadmap: `ENHANCEMENT_ROADMAP.md` (Enhancement #11: Extraction Diagnosis)

---

*Last Updated: Dec 7, 2025*


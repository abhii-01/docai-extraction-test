# Table Text Extraction Bug

## Status: 🟢 RESOLVED (Dec 8, 2025)

---

## TL;DR

| Issue | Table cells detected but text was empty |
|-------|----------------------------------------|
| Root Cause | Code looked for text in `cell.layout.text_anchor` but Layout Parser stores it in `cell.blocks[].text_block.text` |
| Fix | Read text from `cell.blocks` instead |
| Commit | `2f3231e` on `main` |

---

## The Problem

Layout Parser returns:
- `document.text` = **empty** (0 chars)
- `cell.layout` = **None**
- `cell.blocks[].text_block.text` = **actual text** ✅

Old code tried Method 1 (text_anchor) which failed because `document.text` is empty.

---

## The Fix

**File:** `utils/universal_parser.py` → `_extract_table_grid()`

```python
# Method 2: Direct cell.blocks extraction (THE FIX)
if not cell_text:
    cell_blocks = list(getattr(cell, 'blocks', []) or [])
    block_texts = []
    for child_block in cell_blocks:
        child_tb = getattr(child_block, 'text_block', None)
        if child_tb:
            text = getattr(child_tb, 'text', '') or ''
            if text:
                block_texts.append(text.strip())
    cell_text = " ".join(block_texts)
```

---

## Key Insight: Layout Parser vs Form Parser

| Processor | `document.text` | Text Location |
|-----------|-----------------|---------------|
| **Form Parser / OCR** | Populated | `text_anchor` points into `document.text` |
| **Layout Parser** | **Empty** | Text stored hierarchically in `block.text_block.text` |

Layout Parser is designed for **hierarchical structure**, not flat text extraction. This is intentional, not a bug.

---

## Debug Code (For Future Issues)

Run this in notebook to inspect raw table structure:

```python
raw_doc = parser.client.process_document(pdf_filename)
print(f"document.text length: {len(raw_doc.text)}")

for block in raw_doc.document_layout.blocks:
    if hasattr(block, 'table_block') and block.table_block:
        tb = block.table_block
        row = tb.body_rows[0] if tb.body_rows else None
        if row and row.cells:
            cell = row.cells[0]
            print(f"cell.layout: {getattr(cell, 'layout', None)}")
            print(f"cell.blocks: {list(getattr(cell, 'blocks', []))}")
            for child in getattr(cell, 'blocks', []):
                print(f"  -> text: {getattr(child.text_block, 'text', '')}")
        break
```

---

## Caveats & Gotchas

### 1. Colab Caching Issue
**Problem:** Colab caches `utils/` folder. Even after GitHub update, old code runs.

**Solution:** Force re-clone before running:
```python
!rm -rf utils temp_repo
!git clone https://github.com/abhii-01/docai-extraction-test.git temp_repo
!mv temp_repo/utils .
!rm -rf temp_repo
```

Then: **Runtime → Restart runtime**

### 2. Other Processors Behave Differently
- **Form Parser:** `document.text` populated, `text_anchor` works
- **Layout Parser:** `document.text` empty, use `block.text_block.text`

Don't assume one processor's behavior applies to others.

### 3. Cell Structure
Table cells have:
- `cell.blocks[]` - nested content blocks (paragraphs inside cell)
- `cell.row_span`, `cell.col_span` - merge info
- `cell.layout` - **often None** for Layout Parser

---

## Files Changed

| File | Change |
|------|--------|
| `utils/universal_parser.py` | Added `cell.blocks` extraction in `_extract_table_grid()` |

---

## Related Links

- [Layout Parser Docs](https://cloud.google.com/document-ai/docs/processors-list#processor_layout-parser)
- [Table Extraction Guide](https://cloud.google.com/document-ai/docs/handle-response#tables)

---

*Resolved: Dec 8, 2025*

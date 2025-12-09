# Extraction Output Handling

> ⚠️ **Scope:** This folder contains cross-project integration docs. Skip unless specifically working on integration features.

---

## Overview

**Input:** Hierarchical JSON from Document AI (`universal_parsed_result.json`)

**Output:** Text chunks for Taxonomy Tagger pipeline

**Flow:**
```
JSON → Confidence Check → Chunking Rules → Chunks (with dual metadata) → Taxonomy Tagger
```

---

## Pre-Processing: Confidence Check (TOP PRIORITY)

**Before chunking, check extraction confidence:**

- Document AI returns confidence scores for extracted text
- If confidence is **too low** → route to **expensive pipeline** (better OCR, manual review)
- This check happens BEFORE any chunking logic

```python
def check_confidence(document_result, threshold=0.7):
    """Route low-confidence extractions to expensive pipeline"""
    avg_confidence = calculate_avg_confidence(document_result)
    if avg_confidence < threshold:
        return "expensive_pipeline"
    return "standard_pipeline"
```

**Note:** Threshold TBD based on testing.

---

## Chunking Rules

### Rule 1: Text Chunks — Basic Flow

| Property | Value |
|----------|-------|
| Target size | TBD (configurable range, e.g., 500-600 chars) |
| Hard max | Range-based, not strict ceiling |
| Atomic unit | `"text"` field |
| Overlap | Minimum threshold (TBD, e.g., 100+ chars) |

**Heading Text:** Included as content (combined with paragraphs), not metadata-only.

**Algorithm:**
1. Traverse JSON in **linear/DFS order**
2. Collect all `"text"` fields — **including heading text**
3. Filter out noise (Rule 5)
4. Combine texts until target char range reached
5. Overlap: next chunk starts with enough previous texts to meet **minimum overlap threshold**

**Overlap Detail:**
- Current: "Start with last text of previous chunk"
- Enhanced: Ensure overlap meets minimum char threshold (exact value TBD)
- If last text is too short, include more texts from previous chunk

**Empty Chunks:** Should not happen — human involved in noise filtering ensures valid content exists.

**Reading Order:** Trust Document AI's extraction order.

---

### Rule 2: Long Text Handling

**Problem:** Single `"text"` field exceeds target range

**Solution:** Split at sentence boundaries (`.` or `\n`)
- Each split piece keeps the **same metadata**
- Split pieces become separate atomic units for chunking

```python
def split_long_text(text, max_chars=600):
    """Split at sentence boundaries, preserve metadata"""
    if len(text) <= max_chars:
        return [text]
    
    sentences = re.split(r'(?<=[.!?\n])\s+', text)
    chunks = []
    current = ""
    
    for sentence in sentences:
        if len(current) + len(sentence) > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current += " " + sentence
    
    if current.strip():
        chunks.append(current.strip())
    
    return chunks
```

---

### Rule 3: Metadata Selection — Majority by Char Count

**Problem:** A chunk combines texts from different pages/paths

**Solution:** Use metadata from source with **highest total char count**

**Store TWO metadata values:**
- `metadata_1st`: Source with most characters in chunk
- `metadata_2nd`: Source with second-most characters in chunk

**Parent Path Format:** Store as **array** (not string with `>` separator)
- Avoids ambiguity when heading text contains `>`
- Example: `["3.2. GIG ECONOMY", "Key Features"]` not `"3.2. GIG ECONOMY > Key Features"`

```python
chunk = {
    "text": "Combined content from multiple sources...",
    "char_count": 547,
    "metadata_1st": {
        "parent_path": ["3.2. GIG ECONOMY", "Key Features"],  # Array format
        "page": 2,
        "char_contribution": 350,
        "bbox": [0.1, 0.15, 0.9, 0.45]  # Preserved from source
    },
    "metadata_2nd": {
        "parent_path": ["3.2. GIG ECONOMY", "Factsheet"],
        "page": 3,
        "char_contribution": 197,
        "bbox": [0.1, 0.05, 0.9, 0.35]
    },
    "source_file": "economics.pdf",
    "text_ids": ["63", "64", "65", "66"]
}
```

**Why dual metadata?**
- Preserves context when chunks span sections
- Taxonomy tagger can use both for better tagging
- No context loss at section boundaries

**Deep Paths:** Keep full path — do not truncate regardless of depth.

---

### Rule 4: Table Chunks

| Property | Value |
|----------|-------|
| Pipeline | Separate (convert to narrative first) |
| Size limit | None (whole table = 1 chunk) |
| Metadata | Full metadata transfers to narrative |
| Validation | Trust LLM output for table-to-narrative |

**Algorithm:**
1. Detect `"type": "table"` blocks
2. Convert `simple_matrix` to paragraph/narrative (LLM)
3. Output as single chunk with **same metadata as original table block**
4. Never merge with text chunks
5. Never split tables

```python
table_chunk = {
    "text": "Narrative version of table content...",
    "type": "table",
    "metadata_1st": {
        "parent_path": ["3.2. GIG ECONOMY", "Benefits"],
        "page": 2,
        "bbox": [0.1, 0.3, 0.9, 0.7]
    },
    "source_file": "economics.pdf",
    "original_table_id": "81"
}
```

---

### Rule 5: Noise Filtering

#### Quick Filters (No LLM)

```python
import re

NOISE_EXACT = {"•", "○", "☑", "✓", "▪", "►"}

NOISE_PATTERNS = [
    r"^Vision IAS\s+AHMEDABAD",
    r"visionias\.in",
    r"^\d{1,3}$",
    r"^[\u2022\u2611\u039f\s]+$",
]

def is_noise(text: str, block_type: str = None) -> bool:
    text = text.strip()
    
    if block_type in ("footer", "header"):
        return True
    if len(text) < 3:
        return True
    if text in NOISE_EXACT:
        return True
    
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.3:
        return True
    
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False
```

#### LLM-Assisted Noise Discovery (New Document Types)

**5-Step Pipeline:**

1. **Sample Extraction** — Extract JSON from few representative pages
2. **LLM Identification** — High-end LLM lists noise patterns with reasons
3. **Human Verification** — Confirm/reject each identified pattern
4. **LLM Code Generation** — Generate regex/exact strings for filter
5. **Integration** — Insert into `NOISE_PATTERNS` and `NOISE_EXACT`

**Footnotes/References:** Defer to this pipeline — LLM + human decides if noise or content.

---

### Rule 6: Images/Charts

**Decision:** Flag for separate pipeline

- `"type": "image"` blocks are **not processed** in text chunking
- Route to vision LLM pipeline separately
- Image chunks (if created) follow same metadata structure

---

### Rule 7: Duplicates

**Decision:** Keep duplicates — do NOT dedupe

**Rationale:** Not losing data > Cleaning data

- Duplicates may get same tags anyway
- Deduping risks losing legitimate repeated content

---

### Rule 8: Empty Sections (Headings Without Paragraphs)

**Decision:** Include heading text in linear flow

```json
{
  "type": "heading-1",
  "text": "3. TAXATION",
  "children": [
    { "type": "heading-2", "text": "3.1 Direct Tax", "children": [...] }
  ]
}
```

- `"3. TAXATION"` text is included as content (part of chunks)
- Helps preserve document structure
- Heading text is content, not just metadata

---

### Rule 9: List Items

**Treatment:** Same as regular text with majority rule

- List items are atomic units
- If same-metadata list exceeds target → split into chunks with same metadata
- If mixed metadata → use char count majority (Rule 3)

---

### Rule 10: Bounding Box (Bbox) Preservation

**Decision:** Preserve bbox in chunk metadata

**Available in JSON:** `"bbox": [x_min, y_min, x_max, y_max]`

**Potential Uses:**
- Detect multi-column layout issues
- Identify sidebars/callouts vs main content
- Debug reading order problems
- Spatial analysis for document understanding

**Implementation:** Include bbox of primary source in `metadata_1st` and `metadata_2nd`.

---

### Rule 11: Chunk Unique IDs

**Decision:** Case-based — not decided now

**Options to consider:**
- Sequential: `chunk_001`, `chunk_002`
- Hash-based: `hash(text + source_file)`
- Composite: `{source_file}_{page}_{index}`

**Needed for:** tracking, debugging, retrieval linking

**Note:** Decide based on specific pipeline requirements.

---

## Chunk Output Schema

```python
{
    # Content
    "text": str,                    # Combined text content
    "char_count": int,              # Character count
    "type": str,                    # "text" | "table"
    
    # Dual Metadata (by char count majority)
    "metadata_1st": {
        "parent_path": list[str],   # Array format: ["Section", "Subsection"]
        "page": int,
        "char_contribution": int,
        "bbox": list[float]         # [x_min, y_min, x_max, y_max]
    },
    "metadata_2nd": {               # None if only one source
        "parent_path": list[str],
        "page": int,
        "char_contribution": int,
        "bbox": list[float]
    },
    
    # Source Tracking
    "source_file": str,             # Original PDF filename
    "text_ids": list[str]           # IDs of texts combined (debugging)
}
```

---

## Configurable Parameters (TBD)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TARGET_CHUNK_SIZE` | Target character count | TBD (~500-600) |
| `CHUNK_SIZE_TOLERANCE` | Acceptable range around target | TBD |
| `MIN_OVERLAP_CHARS` | Minimum overlap between chunks | TBD (~100) |
| `CONFIDENCE_THRESHOLD` | Below this → expensive pipeline | TBD (~0.7) |

These values will be determined through testing.

---

## Analyzing New JSON Outputs

When a new sample JSON is provided, check:

### Structure
- [ ] Block types present?
- [ ] Nesting depth?
- [ ] Orphan blocks at root?

### Text Quality
- [ ] New noise patterns?
- [ ] Long texts (> target)?
- [ ] Empty/symbol-only texts?

### Tables
- [ ] `simple_matrix` populated?
- [ ] Merged cells?

### Edge Cases
- [ ] Cross-page content?
- [ ] Mixed metadata chunks?
- [ ] Confidence scores available?
- [ ] Deep heading paths?
- [ ] Special characters in headings?

---

## Related Projects

| Project | Path | Role |
|---------|------|------|
| docai-test | `/Users/aadarsh/Documents/code/docai-test` | Produces JSON |
| Taxonomy Tagger | `/Users/aadarsh/Documents/code/llm syllabus portal` | Consumes chunks |

---

## Decision Summary

| Topic | Decision |
|-------|----------|
| Heading text | **Include as content** (not metadata-only) |
| Long text (>target) | Split at sentence boundary, same metadata |
| Metadata selection | **Char count majority** |
| Dual metadata | Store `metadata_1st` + `metadata_2nd` |
| Parent path format | **Array** (not string with separator) |
| Deep paths | Keep full path (no truncation) |
| Overlap | Minimum threshold (TBD) |
| Chunk size | Range-based (not hard ceiling) |
| Bbox | **Preserve in metadata** |
| Tables | Full metadata → narrative, trust LLM |
| Images | Separate pipeline |
| Duplicates | Keep (don't dedupe) |
| Empty headings | Include in flow |
| Confidence | TOP priority — low → expensive pipeline |
| Footnotes | Defer to LLM + human |
| Reading order | Trust Document AI |
| Chunk IDs | Case-based (TBD) |
| Empty chunks | Shouldn't happen (human involved) |

---

## Changelog

| Date | Change |
|------|--------|
| Dec 2025 | Initial chunking rules |
| Dec 2025 | Added dual metadata (1st + 2nd by char count) |
| Dec 2025 | Confidence check as top priority |
| Dec 2025 | Long text splitting at sentence boundaries |
| Dec 2025 | Keep duplicates decision |
| Dec 2025 | Heading text included as content |
| Dec 2025 | Parent path as array format |
| Dec 2025 | Bbox preservation in metadata |
| Dec 2025 | Minimum overlap threshold (TBD) |
| Dec 2025 | Range-based chunk size (not hard max) |

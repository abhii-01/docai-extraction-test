# Sample Files for Document AI Testing

This document contains links to sample files with **tables** and **flowcharts** for testing Google Document AI Layout Parser.

## Quick Download Sources

### 1. Documents with Tables

#### Financial Documents
- **Apple SEC 10-K Filing**: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K
  - Contains extensive financial tables
  - Real-world complex layouts
  
- **Google Annual Report**: https://abc.xyz/investor/
  - Professional tables and charts
  - Multi-column layouts

#### Research Papers with Tables
- **DocLayNet Dataset Paper**: https://arxiv.org/pdf/2206.01062.pdf
  - Academic paper about document layout analysis
  - Multiple tables and figures

- **LayoutParser Paper**: https://arxiv.org/pdf/2103.15348.pdf
  - Contains comparison tables and architecture diagrams

### 2. Documents with Flowcharts

#### Free Flowchart Templates (Download as PDF)
- **BreezeTree Templates**: https://www.breezetree.com/articles/flowchart-templates
  - 100+ free flowchart templates
  - Various formats available

- **ConceptDraw Examples**: https://www.conceptdraw.com/examples/flowchart-easy-sample
  - Business process flowcharts
  - Cross-functional flowcharts

#### Technical Documentation with Diagrams
- **AWS Architecture Diagrams**: https://aws.amazon.com/architecture/
  - System architecture flowcharts
  - Complex diagrams

### 3. Specialized Datasets

#### DocLayNet Dataset
- **Website**: https://github.com/DS4SD/DocLayNet
- **Paper**: https://arxiv.org/abs/2206.01062
- **Content**: 80,863 pages with human-annotated layouts
- **Includes**: Tables, figures, complex layouts

#### PubLayNet Dataset
- **Website**: https://github.com/ibm-aur-nlp/PubLayNet
- **Content**: 360,000+ document images
- **Includes**: Scientific papers with tables and figures

#### GitHub Repositories with Samples

1. **Documents Parsing Lab**
   - URL: https://github.com/AdemBoukhris457/Documents-Parsing-Lab
   - Contains sample documents for OCR and parsing

2. **PDF.Flow.Examples**
   - URL: https://github.com/gehtsoft-usa/PDF.Flow.Examples
   - Medical reports and complex tables

## Manual Download Instructions

### Option 1: Create Your Own Test Files
You can create custom PDFs with:
- **Microsoft Word**: Create flowcharts and tables, export as PDF
- **Google Docs**: Use drawing tools and tables, download as PDF
- **Lucidchart**: Create flowcharts, export as PDF
- **Draw.io**: Free online diagramming tool

### Option 2: Use Sample Documents from Google

Google provides sample documents for Document AI testing:
- **OCR Processor samples**: https://cloud.google.com/document-ai/docs/samples
- **Form Parser samples**: https://cloud.google.com/document-ai/docs/form-parser

## Recommended Test Files

For comprehensive testing, I recommend using:

1. **Simple Table** (Invoice or single-page report)
2. **Complex Multi-page Tables** (Financial statements)
3. **Simple Flowchart** (Basic process flow)
4. **Complex Flowchart** (System architecture diagram)
5. **Mixed Content** (Research paper with both tables and diagrams)

## Quick Start

To download sample files, use the provided script:

```bash
bash download_sample_files.sh
```

Or manually download from the links above and place them in the `sample_pdfs/` directory.

## Testing Tips

1. **Start Simple**: Test with basic tables and flowcharts first
2. **Increase Complexity**: Move to multi-page documents
3. **Test Edge Cases**: 
   - Rotated tables
   - Multi-column layouts
   - Nested flowcharts
   - Mixed orientations (portrait/landscape)

4. **File Formats**: 
   - PDF is preferred for Document AI
   - Ensure good quality (300+ DPI for scanned documents)

## Public Domain Sample Documents

- **Project Gutenberg**: https://www.gutenberg.org/ (older documents)
- **arXiv**: https://arxiv.org/ (academic papers - free to use)
- **SEC EDGAR**: https://www.sec.gov/edgar.shtml (financial filings)
- **WHO Publications**: https://www.who.int/publications (medical/health documents)

---

Last updated: November 30, 2025


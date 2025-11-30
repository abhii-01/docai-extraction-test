# Quick Start Guide - Google Colab Edition

Get started with Google Document AI Layout Parser testing in Google Colab.

## Prerequisites Checklist

- [ ] Google account (for Colab)
- [ ] Google Cloud account with billing enabled
- [ ] Layout Parser processor created in Document AI
- [ ] Service account JSON credentials downloaded
- [ ] OpenAI or Anthropic API key (for table/flowchart conversion)

## Step-by-Step Setup

### 1. Set Up Google Cloud (15 minutes)

Follow the detailed guide: **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)**

Quick summary:
1. Create Google Cloud project
2. Enable billing (free $300 credit for new users)
3. Enable Document AI API
4. **Create Layout Parser processor** (not basic OCR)
5. Create service account & download credentials JSON
6. Keep credentials JSON file ready for upload to Colab

### 2. Open in Google Colab (1 minute)

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File > Upload Notebook**
3. Upload one of the test notebooks from this repository

Or use GitHub import:
1. In Colab: **File > Open Notebook > GitHub**
2. Enter: `abhii-01/docai-extraction-test`
3. Select a test notebook (test1-test5.ipynb)

### 3. Run Setup Cells in Colab (2 minutes)

Each notebook includes setup cells that will:
1. Install required dependencies
2. Prompt you to upload credentials JSON
3. Configure your project ID and processor ID

**Important Configuration:**
```python
DOCAI_PROJECT_ID = "your-project-id-here"  # Update this
DOCAI_PROCESSOR_ID = "your-layout-parser-processor-id"  # Update this
DOCAI_LOCATION = "us"  # or "eu" or "asia"

OPENAI_API_KEY = "sk-your-key-here"  # For table/flowchart conversion
```

### 4. Upload Test PDF to Colab (1 minute)

When you run the notebook, you'll be prompted to upload:
1. Your credentials JSON file
2. A PDF file to test

You can use:
- Your economics textbook PDF
- Any academic paper PDF
- Sample PDFs from arXiv or similar sources

### 5. Run Notebook Cells (2-5 minutes)

Simply run each cell in sequence:
1. Setup cells (dependencies, credentials, config)
2. Processing cells (document analysis)
3. Results cells (view output, download JSON)

The notebook will show progress and results inline!

### 6. Download Results

Each notebook automatically downloads the JSON results file at the end.
You can also manually download from Colab's file browser.

---

## All Tests Overview (Jupyter Notebooks for Colab)

| Test | Notebook | What It Tests |
|------|----------|---------------|
| **Test 1** | `test1_basic_extraction.ipynb` | Basic text extraction with Layout Parser |
| **Test 2** | `test2_structure_detection.ipynb` | Paragraph/table/image detection |
| **Test 3** | `test3_table_handling.ipynb` | Table → narrative conversion with LLM |
| **Test 4** | `test4_flowchart_detection.ipynb` | Diagram description with Vision LLM |
| **Test 5** | `test5_full_pipeline.ipynb` | Complete pipeline (all features) |

---

## Run All Tests in Google Colab

**Recommended Order:**

1. **Start with Test 1** - Verify Layout Parser works with basic extraction
2. **Test 2** - Confirm structure detection (use PDF with tables)
3. **Test 3** - Test table-to-narrative conversion
4. **Test 4** - Test flowchart detection (use PDF with diagrams)
5. **Test 5** - Run complete pipeline on complex textbook PDF

**How to Run:**
- Open each notebook in Colab
- Run all cells from top to bottom
- Upload your PDF when prompted
- Download results JSON at the end

---

## Troubleshooting

### "Credentials upload failed" (Colab)
- Make sure you're uploading the `.json` file (not .txt or other format)
- File should contain your service account key from Google Cloud

### "Processor not found"
- Check your `DOCAI_PROCESSOR_ID` is correct
- Go to: https://console.cloud.google.com/ai/document-ai/processors
- Verify you created a **Layout Parser** processor (not Document OCR)
- Copy the correct processor ID

### "API key invalid" (for LLM)
- Check your `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- Verify key is active: https://platform.openai.com/api-keys
- Make sure you have credits/billing enabled

### "Module not found" errors
- Re-run the pip install cell: `%pip install -q google-cloud-documentai ...`
- Restart runtime if needed: Runtime > Restart Runtime

### "Permission denied" errors
- Verify service account has "Document AI API User" role
- Go to: https://console.cloud.google.com/iam-admin/iam
- Service account should have "Document AI Editor" or "Owner" role

---

## Expected Costs

**Layout Parser Pricing** (as of November 2024):
- First 1,000 pages/month: FREE
- After that: $0.001 per page ($1.00 per 1,000 pages)

Testing with ~50 pages total:
- Document AI Layout Parser: **FREE** (under 1,000 pages)
- OpenAI GPT-4 Vision (5-10 images): ~$0.05
- **Total: ~$0.05**

For your full project (10,000 pages):
- Document AI Layout Parser: $9.00 (after free tier)
- OpenAI GPT-4o for tables: ~$3.00
- Vision LLM (500 flowcharts): ~$5.00
- **Total: ~$17.00**

---

## Next Steps After Testing

Once you've validated Google Document AI quality:

1. **Compare Results**
   - Review JSON outputs in `output/` folder
   - Compare extracted text to original PDFs
   - Check table narrative quality
   - Verify flowchart descriptions

2. **Assess Quality**
   - OCR accuracy (should be 95%+)
   - Table detection rate
   - Diagram description quality

3. **Integration Decision**
   - If quality is good → integrate into main project
   - If quality needs work → adjust prompts/settings
   - If quality is poor → reconsider approach

4. **Read Integration Guide**
   - Copy successful code patterns to main project
   - Adapt for your taxonomy matching workflow
   - Update your `pdf_taxonomy_tagger.ipynb`

---

## File Structure Reference

```
docai-test/
├── README.md                        # Project overview
├── SETUP_INSTRUCTIONS.md            # Detailed Google Cloud setup
├── QUICKSTART.md                    # This file
│
├── Jupyter Notebooks (for Google Colab):
│   ├── test1_basic_extraction.ipynb      # Test 1: Basic extraction
│   ├── test2_structure_detection.ipynb   # Test 2: Structure detection
│   ├── test3_table_handling.ipynb        # Test 3: Table conversion
│   ├── test4_flowchart_detection.ipynb   # Test 4: Flowchart description
│   └── test5_full_pipeline.ipynb         # Test 5: Complete pipeline
│
├── utils/
│   ├── docai_client.py              # Document AI Layout Parser wrapper
│   ├── table_converter.py           # Table → narrative conversion
│   └── vision_llm.py                # Flowchart description with Vision LLM
│
├── credentials/                     # (For local use only)
│   └── docai-credentials.json       # Google Cloud credentials
│
└── output/                          # Results downloaded from Colab
    ├── test1_raw_text.json
    ├── test2_structured.json
    ├── test3_tables.json
    ├── test4_flowcharts.json
    └── test5_full_pipeline.json
```

---

## Getting Help

1. Check troubleshooting section above
2. Review SETUP_INSTRUCTIONS.md
3. Check Google Cloud Console for errors
4. Review Document AI docs: https://cloud.google.com/document-ai/docs

---

**Ready to start?** 

1. Open `test1_basic_extraction.ipynb` in Google Colab
2. Run all cells to verify your Layout Parser setup
3. Upload your PDF and see the results!

**Next Steps:**
- Upload notebooks to your Google Drive for easy access
- Create a Layout Parser processor if you haven't already
- Have your credentials JSON and OpenAI API key ready


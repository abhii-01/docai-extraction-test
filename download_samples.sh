#!/bin/bash

# Script to download sample PDFs for testing
# Run: chmod +x download_samples.sh && ./download_samples.sh

echo "=================================================="
echo "  Sample PDF Downloader for Document AI Testing"
echo "=================================================="
echo ""

cd sample_pdfs/ || exit 1

# PDF 1: Simple baseline test
echo "📄 Downloading PDF 1: Simple baseline..."
curl -o pdf1_simple.pdf https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf 2>/dev/null
if [ -f "pdf1_simple.pdf" ]; then
    echo "   ✅ PDF 1 downloaded"
else
    echo "   ⚠️  PDF 1 download failed"
fi

echo ""

# PDF 2: Academic paper with tables
echo "📄 Downloading PDF 2: Academic paper with tables..."
curl -L -o pdf2_academic.pdf "https://arxiv.org/pdf/2303.05325.pdf" 2>/dev/null
if [ -f "pdf2_academic.pdf" ]; then
    echo "   ✅ PDF 2 downloaded"
else
    echo "   ⚠️  PDF 2 download failed"
fi

echo ""

# PDF 3: Try to copy from main project
echo "📄 Setting up PDF 3: Textbook (from main project)..."
MAIN_PROJECT_PDF="../llm syllabus portal/sample_pdfs/economics1.pdf"
if [ -f "$MAIN_PROJECT_PDF" ]; then
    cp "$MAIN_PROJECT_PDF" pdf3_textbook.pdf
    echo "   ✅ PDF 3 copied from main project"
elif [ -f "../../llm syllabus portal/sample_pdfs/economics1.pdf" ]; then
    cp "../../llm syllabus portal/sample_pdfs/economics1.pdf" pdf3_textbook.pdf
    echo "   ✅ PDF 3 copied from main project"
else
    echo "   ⚠️  Economics textbook not found in main project"
    echo "      Download manually from: https://openstax.org/subjects/science"
fi

echo ""
echo "=================================================="
echo "  Download Summary"
echo "=================================================="
echo ""

ls -lh *.pdf 2>/dev/null

echo ""
echo "📝 Manual steps required:"
echo "   - PDF 4 (Mixed/Handwritten): Create by scanning a document"
echo "   - PDF 5 (Poor Quality): Create by scanning with poor lighting"
echo ""
echo "📖 See SAMPLE_PDFS.md for detailed instructions"
echo ""
echo "✅ Ready to test! Run: python tests/test1_basic_extraction.py"


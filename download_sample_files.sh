#!/bin/bash

# Script to download sample PDF files with tables and flowcharts for Document AI testing

SAMPLE_DIR="sample_pdfs"
mkdir -p "$SAMPLE_DIR"

echo "Downloading sample files with tables and flowcharts..."

# Sample 1: Business Process Flowchart
echo "1. Downloading business process flowchart..."
curl -L -o "$SAMPLE_DIR/flowchart_example.pdf" \
  "https://www.conceptdraw.com/samples/resource/images/solutions/flowcharts/FlowChart-Cross-Functional-Flowchart-example.png" \
  || echo "Failed to download flowchart example"

# Sample 2: Financial Report with Tables (SEC filing sample)
echo "2. Downloading financial document with tables..."
curl -L -o "$SAMPLE_DIR/financial_tables.pdf" \
  "https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230930.pdf" \
  || echo "Failed to download financial tables"

# Sample 3: Research Paper with Diagrams and Tables (arXiv)
echo "3. Downloading research paper with tables and diagrams..."
curl -L -o "$SAMPLE_DIR/research_paper.pdf" \
  "https://arxiv.org/pdf/2206.01062.pdf" \
  || echo "Failed to download research paper"

# Sample 4: Medical Lab Report Template
echo "4. Downloading medical report with tables..."
curl -L -o "$SAMPLE_DIR/medical_report.pdf" \
  "https://www.who.int/docs/default-source/coronaviruse/laboratory-testing-for-2019-ncov-in-suspected-human-cases.pdf" \
  || echo "Failed to download medical report"

# Sample 5: Invoice with tables
echo "5. Downloading invoice sample..."
curl -L -o "$SAMPLE_DIR/invoice_sample.pdf" \
  "https://templates.invoicehome.com/invoice-template-us-neat-750px.png" \
  || echo "Failed to download invoice"

echo ""
echo "Download complete! Files saved to $SAMPLE_DIR/"
echo ""
echo "Note: Some URLs may change. If downloads fail, check the manual download list below."


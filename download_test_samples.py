#!/usr/bin/env python3
"""
Download sample PDF files with tables and flowcharts for Document AI testing.
"""

import os
import urllib.request
from pathlib import Path

SAMPLE_DIR = Path("sample_pdfs")
SAMPLE_DIR.mkdir(exist_ok=True)

# Sample files to download
SAMPLES = {
    "research_paper_with_tables.pdf": {
        "url": "https://arxiv.org/pdf/2206.01062.pdf",
        "description": "DocLayNet paper - contains tables and figures"
    },
    "layoutparser_paper.pdf": {
        "url": "https://arxiv.org/pdf/2103.15348.pdf",
        "description": "LayoutParser paper - contains architecture diagrams and tables"
    },
    "apple_sec_filing.pdf": {
        "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230930.pdf",
        "description": "Apple SEC 10-K - extensive financial tables"
    },
    "who_laboratory_testing.pdf": {
        "url": "https://www.who.int/docs/default-source/coronaviruse/laboratory-testing-for-2019-ncov-in-suspected-human-cases.pdf",
        "description": "WHO document - tables and structured content"
    },
    "transformer_paper.pdf": {
        "url": "https://arxiv.org/pdf/1706.03762.pdf",
        "description": "Attention Is All You Need - contains architecture diagrams and tables"
    }
}

def download_file(url: str, filepath: Path, description: str) -> bool:
    """Download a file from URL to filepath."""
    try:
        print(f"Downloading: {description}")
        print(f"  URL: {url}")
        print(f"  Saving to: {filepath}")
        
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
        
        file_size = filepath.stat().st_size
        print(f"  ✓ Downloaded successfully ({file_size:,} bytes)\n")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to download: {str(e)}\n")
        return False

def main():
    print("=" * 70)
    print("Downloading Sample PDFs for Document AI Testing")
    print("=" * 70)
    print()
    
    success_count = 0
    total_count = len(SAMPLES)
    
    for filename, info in SAMPLES.items():
        filepath = SAMPLE_DIR / filename
        
        # Skip if already exists
        if filepath.exists():
            print(f"Skipping {filename} (already exists)")
            print()
            success_count += 1
            continue
        
        # Download the file
        if download_file(info["url"], filepath, info["description"]):
            success_count += 1
    
    print("=" * 70)
    print(f"Download Summary: {success_count}/{total_count} files downloaded successfully")
    print("=" * 70)
    print()
    
    if success_count > 0:
        print("Sample files are ready in the 'sample_pdfs/' directory!")
        print()
        print("Next steps:")
        print("1. Review the files in sample_pdfs/")
        print("2. Run the test notebooks (test3_table_handling.ipynb, test4_flowchart_detection.ipynb)")
        print("3. Use these files with Google Document AI Layout Parser")
    else:
        print("No files were downloaded. Check your internet connection and try again.")
        print("See SAMPLE_SOURCES.md for manual download links.")

if __name__ == "__main__":
    main()


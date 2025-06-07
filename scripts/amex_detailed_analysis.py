#!/usr/bin/env python3
"""
Detailed AmEx merchant analysis for better categorization.
"""

import sys
sys.path.append('.')
from scripts.process_spending_data import SpendingProcessor
from PyPDF2 import PdfReader
import re
from pathlib import Path

def analyze_amex_merchants():
    spese_dir = Path("Spese")
    pdf_files = list(spese_dir.glob("*.pdf"))
    
    all_merchants = []
    
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        text_content = "".join(page.extract_text() or "" for page in reader.pages)
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Match transaction pattern: Date Date Merchant Location
            match = re.match(r'(?:CR)?(\d{2}\.\d{2}\.\d{2})\s+(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+([A-Z\s,\.]+)$', line)
            if match:
                merchant = match.group(3).strip()
                location = match.group(4).strip()
                all_merchants.append((merchant, location))
    
    print("🏪 UNIQUE AMEX MERCHANTS FOUND:")
    print("=" * 50)
    unique_merchants = list(set(all_merchants))
    for merchant, location in sorted(unique_merchants):
        print(f"• {merchant:<30} | {location}")
    
    # Now categorize them manually
    processor = SpendingProcessor()
    print("\n🏷️  CATEGORIZATION:")
    print("=" * 30)
    categories = {}
    for merchant, location in unique_merchants:
        category = processor.classify_merchant(merchant)
        if category not in categories:
            categories[category] = []
        categories[category].append(f"{merchant} ({location})")
    
    for category, merchants in categories.items():
        print(f"\n{category}:")
        for merchant in merchants:
            print(f"  - {merchant}")

if __name__ == "__main__":
    analyze_amex_merchants() 
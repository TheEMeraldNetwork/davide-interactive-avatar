#!/usr/bin/env python3
"""
Generate spending summary for Knowledge Base with improved categorization.
"""

import sys
sys.path.append('.')
from scripts.process_spending_data import SpendingProcessor
from collections import defaultdict

def improve_amex_categorization():
    """Manually improve categorization based on discovered merchants."""
    
    # Enhanced category mapping based on real data
    enhanced_categories = {
        # Travel & Hotels
        'hotel': 'Travel', 'chalet': 'Travel', 'booking': 'Travel', 
        'meridien': 'Travel', 'hyatt': 'Travel', 'airways': 'Travel',
        
        # Dining & Food
        'ristorante': 'Dining', 'tombon': 'Dining', 'bisteccheria': 'Dining',
        'fratellini': 'Dining', 'food hall': 'Dining', 'pizza': 'Dining',
        'convivium': 'Dining', 'diavolo': 'Dining', 'porteno': 'Dining',
        'marecrudo': 'Dining', 'sale grosso': 'Dining',
        
        # Tech & Subscriptions  
        'cursor': 'Tech/AI', 'claude': 'Tech/AI', 'aws': 'Tech/AI', 
        'perplexity': 'Tech/AI', 'd-id': 'Tech/AI', 'twilio': 'Tech/AI',
        'finnhub': 'Tech/AI', 'prime video': 'Entertainment',
        
        # Shopping & Retail
        'amazon': 'Online/Retail', 'apple': 'Online/Retail', 
        'media world': 'Online/Retail', 'jordan': 'Fashion/Retail',
        'buscemi': 'Online/Retail', 'mountain shop': 'Sports/Retail',
        
        # Transport & Fuel
        'eni': 'Fuel/Transport', 'pedaggi': 'Transport', 'carte italiane': 'Transport',
        
        # Services
        'mamaclean': 'Services', 'portrait': 'Services',
        
        # Entertainment & Leisure  
        'nautilus': 'Entertainment', 'beach': 'Entertainment',
        'gruppouna': 'Entertainment', 'versilia': 'Entertainment',
        
        # Fees & Bills
        'quota associativa': 'Fees/Bills', 'imposta bollo': 'Fees/Bills',
        'addebito': 'Banking',
    }
    
    return enhanced_categories

def categorize_merchant_enhanced(merchant_name: str) -> str:
    """Enhanced merchant categorization."""
    merchant_lower = merchant_name.lower()
    enhanced_map = improve_amex_categorization()
    
    # Try enhanced mapping first
    for keyword, category in enhanced_map.items():
        if keyword in merchant_lower:
            return category
    
    # Fallback to original logic
    processor = SpendingProcessor()
    return processor.classify_merchant(merchant_name)

def generate_enhanced_summary():
    """Generate enhanced spending summary."""
    print("💰 ENHANCED SPENDING ANALYSIS")
    print("=" * 50)
    
    # Process AmEx with enhanced categorization
    processor = SpendingProcessor()
    amex_totals = defaultdict(float)
    
    # Get AmEx data with enhanced categories
    amex_data = processor.process_amex_pdfs()
    
    # Recategorize using enhanced logic
    from scripts.amex_detailed_analysis import analyze_amex_merchants
    from PyPDF2 import PdfReader
    import re
    from pathlib import Path
    
    spese_dir = Path("Spese")
    pdf_files = list(spese_dir.glob("*.pdf"))
    
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        text_content = "".join(page.extract_text() or "" for page in reader.pages)
        lines = text_content.split('\n')
        
        # Find amounts
        amounts = []
        for i, line in enumerate(lines):
            line = line.strip()
            euro_match = re.search(r'(\d{1,3}(?:,\d{2}))$', line)
            if euro_match:
                try:
                    amount = processor._parse_italian_amount(euro_match.group(1))
                    if amount > 0:
                        amounts.append((i, amount))
                except ValueError:
                    continue
        
        # Match with merchants
        for i, line in enumerate(lines):
            line = line.strip()
            match = re.match(r'(?:CR)?(\d{2}\.\d{2}\.\d{2})\s+(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+([A-Z\s,\.]+)$', line)
            if match:
                merchant = match.group(3).strip()
                
                # Find corresponding amount
                for amt_line, amount in amounts:
                    if abs(amt_line - i) <= 10:
                        category = categorize_merchant_enhanced(merchant)
                        amex_totals[category] += amount
                        amounts.remove((amt_line, amount))
                        break
    
    # Get bank data
    bank_data = processor.process_bank_csv()
    
    # Filter out investment-heavy categories for consumer spending focus
    consumer_bank_categories = {}
    for category, amount in bank_data.items():
        if category not in ['Investments', 'Transfers', 'Other Banking']:
            consumer_bank_categories[category] = amount
    
    # Combine AmEx + Consumer Banking
    all_consumer_totals = defaultdict(float)
    for category, amount in amex_totals.items():
        all_consumer_totals[category] += amount
    for category, amount in consumer_bank_categories.items():
        all_consumer_totals[category] += amount
    
    # Calculate percentages
    total_consumer = sum(all_consumer_totals.values())
    total_all = sum(bank_data.values()) + sum(amex_totals.values())
    
    print(f"Total Consumer Spending: €{total_consumer:,.2f}")
    print(f"Total All Spending: €{total_all:,.2f}")
    print(f"AmEx Portion: €{sum(amex_totals.values()):,.2f}")
    print()
    
    # Sort and display
    sorted_consumer = sorted(all_consumer_totals.items(), key=lambda x: x[1], reverse=True)
    
    print("🛍️  CONSUMER SPENDING BREAKDOWN:")
    kb_parts = []
    for category, amount in sorted_consumer[:8]:  # Top 8
        percentage = (amount / total_consumer) * 100 if total_consumer > 0 else 0
        print(f"• {category}: €{amount:,.2f} ({percentage:.1f}%)")
        if percentage >= 5:  # Only include significant categories in KB
            kb_parts.append(f"{category} ~{percentage:.0f}%")
    
    print(f"\n📝 KNOWLEDGE BASE FORMAT:")
    print(f"- **Category Mix (2024-2025)**: {', '.join(kb_parts)}.")
    
    print(f"\n💳 AMEX DETAILED BREAKDOWN:")
    amex_total = sum(amex_totals.values())
    for category, amount in sorted(amex_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / amex_total) * 100 if amex_total > 0 else 0
        if percentage >= 5:
            print(f"• {category}: €{amount:.2f} ({percentage:.1f}%)")

if __name__ == "__main__":
    generate_enhanced_summary() 
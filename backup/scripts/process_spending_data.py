#!/usr/bin/env python3
"""
Comprehensive spending data processor for Davide Consiglio's financial data.
Processes both AmEx PDF statements and bank CSV movements.
Outputs category summaries for Knowledge Base integration.
"""

import os
import sys
import csv
import re
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfReader
except ImportError:
    logger.error("PyPDF2 required. Install: pip install PyPDF2")
    sys.exit(1)

class SpendingProcessor:
    def __init__(self, spese_dir: str = "Spese"):
        self.spese_dir = Path(spese_dir)
        self.category_totals = defaultdict(float)
        
        # AmEx PDF transaction patterns  
        self.amex_patterns = [
            # Standard transaction: Date Merchant Amount
            re.compile(r'(\d{2}/\d{2})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})'),
            # Alternative: Merchant on separate line
            re.compile(r'^([A-Z][A-Z0-9\s\-&\.]{5,})\s*$'),
        ]
        
        # Category mapping for merchant classification
        self.category_map = {
            # Travel
            'hotel': 'Travel', 'booking': 'Travel', 'expedia': 'Travel', 'ryanair': 'Travel',
            'alitalia': 'Travel', 'lufthansa': 'Travel', 'trenitalia': 'Travel', 'italo': 'Travel',
            'uber': 'Travel', 'taxi': 'Travel', 'noleggio': 'Travel', 'rent': 'Travel',
            'aeroporto': 'Travel', 'airport': 'Travel', 'hertz': 'Travel', 'avis': 'Travel',
            
            # Dining & Entertainment  
            'ristorante': 'Dining', 'restaurant': 'Dining', 'bar': 'Dining', 'cafe': 'Dining',
            'pizzeria': 'Dining', 'trattoria': 'Dining', 'osteria': 'Dining', 'pub': 'Dining',
            'mcdonald': 'Dining', 'burger': 'Dining', 'wine': 'Dining', 'vino': 'Dining',
            
            # Groceries
            'coop': 'Groceries', 'conad': 'Groceries', 'carrefour': 'Groceries', 'esselunga': 'Groceries',
            'supermarket': 'Groceries', 'supermercato': 'Groceries', 'iper': 'Groceries',
            
            # Online & Retail
            'amazon': 'Online/Retail', 'ebay': 'Online/Retail', 'zalando': 'Online/Retail',
            'mediaworld': 'Online/Retail', 'unieuro': 'Online/Retail', 'apple': 'Online/Retail',
            
            # Entertainment & Subscriptions
            'netflix': 'Entertainment', 'spotify': 'Entertainment', 'sky': 'Entertainment',
            'cinema': 'Entertainment', 'teatro': 'Entertainment', 'museo': 'Entertainment',
            'kindle': 'Entertainment', 'itunes': 'Entertainment',
            
            # Health & Services
            'farmacia': 'Health/Services', 'ospedale': 'Health/Services', 'clinica': 'Health/Services',
            'medico': 'Health/Services', 'dentista': 'Health/Services', 'palestra': 'Health/Services',
            
            # Utilities & Bills
            'enel': 'Utilities', 'eni': 'Utilities', 'telecom': 'Utilities', 'tim': 'Utilities',
            'vodafone': 'Utilities', 'wind': 'Utilities', 'fastweb': 'Utilities',
        }

    def classify_merchant(self, merchant: str) -> str:
        """Classify merchant into spending category."""
        merchant_lower = merchant.lower().strip()
        
        # Direct matching
        for keyword, category in self.category_map.items():
            if keyword in merchant_lower:
                return category
        
        # Additional heuristics
        if any(word in merchant_lower for word in ['hotel', 'resort', 'airlines', 'aereo']):
            return 'Travel'
        elif any(word in merchant_lower for word in ['rist', 'food', 'drink']):
            return 'Dining'
        elif 'paypal' in merchant_lower or 'pay pal' in merchant_lower:
            return 'Online/Retail'
        elif any(word in merchant_lower for word in ['gas', 'benzina', 'esso', 'agip']):
            return 'Fuel/Transport'
        else:
            return 'Other'

    def process_amex_pdfs(self) -> Dict[str, float]:
        """Process AmEx PDF statements."""
        amex_totals = defaultdict(float)
        pdf_files = list(self.spese_dir.glob("*.pdf"))
        
        logger.info(f"Processing {len(pdf_files)} AmEx PDF files...")
        
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                text_content = ""
                
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text_content += page_text + "\n"
                
                # Extract transactions
                transactions = self._extract_amex_transactions(text_content)
                logger.info(f"{pdf_file.name}: Found {len(transactions)} transactions")
                
                for merchant, amount in transactions:
                    category = self.classify_merchant(merchant)
                    amex_totals[category] += amount
                    
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
        
        return dict(amex_totals)

    def _extract_amex_transactions(self, text: str) -> List[Tuple[str, float]]:
        """Extract transactions from AmEx PDF text."""
        transactions = []
        lines = text.split('\n')
        
        # Look for amount lines first, then find corresponding merchant
        amounts = []
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Match Euro amounts at end of lines (like "189,08", "69,98", etc.)
            euro_match = re.search(r'(\d{1,3}(?:,\d{2}))$', line)
            if euro_match:
                try:
                    amount = self._parse_italian_amount(euro_match.group(1))
                    if amount > 0:
                        amounts.append((i, amount))
                except ValueError:
                    continue
        
        # Now look for transaction descriptions
        for i, line in enumerate(lines):
            line = line.strip()
            
            # AmEx format: Date Date Merchant Location
            # Examples: "CR29.12.24 29.12.24 CURSOR, AI POWERED IDE  NEW YORK"
            date_merchant_match = re.match(r'(?:CR)?(\d{2}\.\d{2}\.\d{2})\s+(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+([A-Z\s,\.]+)$', line)
            if date_merchant_match:
                merchant = date_merchant_match.group(3).strip()
                
                # Find corresponding amount (usually a few lines later)
                corresponding_amount = None
                for amt_line, amount in amounts:
                    if abs(amt_line - i) <= 10:  # Within 10 lines
                        corresponding_amount = amount
                        amounts.remove((amt_line, amount))  # Remove to avoid double counting
                        break
                
                if corresponding_amount and merchant:
                    transactions.append((merchant, corresponding_amount))
        
        # Fallback: extract simple patterns
        for line in lines:
            line = line.strip()
            # Simple pattern for merchants with clear amounts
            simple_match = re.search(r'([A-Z][A-Z0-9\s\-&\.]{3,})\s+(\d{1,3}(?:,\d{2}))$', line)
            if simple_match:
                merchant = simple_match.group(1).strip()
                amount = self._parse_italian_amount(simple_match.group(2))
                if amount > 0:
                    transactions.append((merchant, amount))
        
        return transactions

    def process_bank_csv(self) -> Dict[str, float]:
        """Process bank movements CSV."""
        csv_file = self.spese_dir / "movements_20250607 2.csv"
        bank_totals = defaultdict(float)
        
        if not csv_file.exists():
            logger.warning(f"CSV file not found: {csv_file}")
            return {}
        
        logger.info(f"Processing bank CSV: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Skip header lines until we find the column headers
                header_found = False
                transaction_count = 0
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('Conto Corrente:') or line.startswith('Intestazione'):
                        continue
                    
                    if line.startswith('Data;Entrate;Uscite;Descrizione'):
                        header_found = True
                        continue
                    
                    if not header_found:
                        continue
                    
                    # Parse CSV line: Data;Entrate;Uscite;Descrizione;Descrizione_Completa;Stato;
                    parts = line.split(';')
                    if len(parts) >= 4:
                        date_str = parts[0].strip()
                        entrate = parts[1].strip()
                        uscite = parts[2].strip()
                        descrizione = parts[3].strip()
                        
                        # Process outgoing transactions (uscite)
                        if uscite and uscite != '-' and uscite.replace('-', '').replace(',', '.').replace('.', '', 1).isdigit():
                            amount = abs(self._parse_italian_amount(uscite))
                            if amount > 0 and descrizione:
                                category = self._classify_bank_transaction(descrizione)
                                bank_totals[category] += amount
                                transaction_count += 1
                
                logger.info(f"Processed {transaction_count} bank transactions")
                
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
        
        return dict(bank_totals)

    def _classify_bank_transaction(self, description: str) -> str:
        """Classify bank transaction description."""
        desc_lower = description.lower()
        
        # Bank-specific classifications
        if 'carta di credito' in desc_lower or 'bancomat' in desc_lower:
            return 'Card Payments'
        elif 'bonifico' in desc_lower:
            return 'Transfers'  
        elif 'sepa' in desc_lower or 'addebito' in desc_lower:
            return 'Direct Debits'
        elif 'prelievo' in desc_lower:
            return 'Cash Withdrawals'
        elif 'mutuo' in desc_lower or 'rata' in desc_lower:
            return 'Mortgage/Loans'
        elif 'compravendita' in desc_lower or 'titoli' in desc_lower:
            return 'Investments'
        elif 'telepass' in desc_lower:
            return 'Transport'
        else:
            return 'Other Banking'

    def _parse_italian_amount(self, amount_str: str) -> float:
        """Parse Italian-formatted amount (e.g., '1.234,56')."""
        if not amount_str or amount_str == '-':
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[€$\s]', '', amount_str.strip())
        
        # Handle negative amounts
        is_negative = cleaned.startswith('-')
        if is_negative:
            cleaned = cleaned[1:]
        
        # Convert Italian format to float
        if ',' in cleaned:
            # Replace dots (thousands) and comma (decimal)
            parts = cleaned.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                cleaned = f"{integer_part}.{decimal_part}"
        
        try:
            result = float(cleaned)
            return -result if is_negative else result
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0

    def generate_summary(self) -> Dict:
        """Generate spending summary for Knowledge Base."""
        # Process both data sources
        amex_data = self.process_amex_pdfs()
        bank_data = self.process_bank_csv()
        
        # Combine data
        all_totals = defaultdict(float)
        for category, amount in amex_data.items():
            all_totals[category] += amount
        for category, amount in bank_data.items():
            all_totals[category] += amount
        
        # Calculate percentages
        total_spending = sum(all_totals.values())
        if total_spending == 0:
            return {"error": "No spending data found"}
        
        category_percentages = {}
        for category, amount in all_totals.items():
            percentage = (amount / total_spending) * 100
            category_percentages[category] = {
                'amount': amount,
                'percentage': round(percentage, 1)
            }
        
        # Sort by percentage
        sorted_categories = sorted(
            category_percentages.items(), 
            key=lambda x: x[1]['percentage'], 
            reverse=True
        )
        
        return {
            'total_spending': total_spending,
            'categories': dict(sorted_categories),
            'amex_total': sum(amex_data.values()),
            'bank_total': sum(bank_data.values()),
            'top_5': sorted_categories[:5]
        }

def main():
    processor = SpendingProcessor()
    summary = processor.generate_summary()
    
    if 'error' not in summary:
        print("🏦 SPENDING ANALYSIS SUMMARY")
        print("=" * 40)
        print(f"Total Spending Analyzed: €{summary['total_spending']:,.2f}")
        print(f"AmEx Portion: €{summary['amex_total']:,.2f}")
        print(f"Bank Portion: €{summary['bank_total']:,.2f}")
        print("\n📊 TOP CATEGORIES:")
        
        for category, data in summary['top_5']:
            print(f"• {category}: {data['percentage']}% (€{data['amount']:,.2f})")
        
        # Generate KB format
        print("\n📝 KNOWLEDGE BASE FORMAT:")
        print("- **Category Mix (Analyzed Period)**: ", end="")
        kb_parts = []
        for category, data in summary['top_5']:
            kb_parts.append(f"{category} ~{data['percentage']}%")
        print(", ".join(kb_parts) + ".")
        
    else:
        print(f"❌ Error: {summary['error']}")

if __name__ == "__main__":
    main() 
import re, glob, os, collections, json, sys
from typing import Dict

try:
    from PyPDF2 import PdfReader
except ImportError:  # fallback
    print('PyPDF2 required. Install via pip if missing.', file=sys.stderr)
    sys.exit(1)

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'Spese')

CATEGORY_MAP: Dict[str, str] = {
    'hotel': 'Travel',
    'ryanair': 'Travel',
    'airlines': 'Travel',
    'italotreno': 'Travel',
    'train': 'Travel',
    'uber': 'Travel',
    'taxi': 'Travel',
    'rist': 'Dining',
    'restaurant': 'Dining',
    'ristorante': 'Dining',
    'cafe': 'Dining',
    'bar': 'Dining',
    'supermarket': 'Groceries',
    'coop': 'Groceries',
    'conad': 'Groceries',
    'carrefour': 'Groceries',
    'amazon': 'Online',
    'netflix': 'Entertainment',
    'itunes': 'Entertainment',
    'spotify': 'Entertainment',
    # default will be Other
}

line_pattern = re.compile(r'^(?P<merchant>.+?)\s+(?P<amount>[0-9]+,[0-9]{2})$')

def parse_pdf(path: str, counter: collections.Counter):
    reader = PdfReader(path)
    for page in reader.pages:
        text = page.extract_text() or ''
        for line in text.split('\n'):
            m = line_pattern.match(line.strip())
            if not m:
                continue
            amt = float(m.group('amount').replace(',', '.'))
            merchant = m.group('merchant').lower().strip()
            category = 'Other'
            for kw, cat in CATEGORY_MAP.items():
                if kw in merchant:
                    category = cat
                    break
            counter[category] += amt


def main():
    files = glob.glob(os.path.join(BASE_DIR, '*.pdf'))
    if not files:
        print('No PDF files found in Spese/', file=sys.stderr)
        sys.exit(1)
    totals = collections.Counter()
    for pdf in files:
        try:
            parse_pdf(pdf, totals)
        except Exception as e:
            print(f'Error parsing {pdf}: {e}', file=sys.stderr)
    overall = sum(totals.values()) or 1.0
    percentages = {cat: round(amount * 100 / overall, 1) for cat, amount in totals.items()}
    summary = {
        'totals': totals,
        'percentages': percentages,
        'overall': round(overall, 2)
    }
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main() 
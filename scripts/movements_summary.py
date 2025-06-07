import csv, os, sys, re, collections, json, pathlib

CSV_PATH = 'Spese/movements_20250607 2.csv'

if not pathlib.Path(CSV_PATH).exists():
    print('CSV file not found', file=sys.stderr)
    sys.exit(1)

CATEGORY_MAP = {
    'Compravendita Titoli': 'Investimenti',
    'Utilizzo carta di credito': 'Carta di credito',
    'Pagamento Bancomat': 'Carta di credito',
    'Bonifico SEPA Italia': 'Bonifici',
    'Bonifico SEPA Estero': 'Bonifici',
    'Bonifico Istantaneo': 'Bonifici',
    'SEPA Direct Debit': 'Utenze & abbonamenti',
    'Telepass': 'Utenze & abbonamenti',
    'Pagamento Bollettino': 'Utenze & abbonamenti',
    'Ricarica Conto Under18': 'Famiglia',
    'Cambio valuta': 'Investimenti',
    'Prelievo Bancomat': 'Contanti',
    'Maxiprelievo': 'Contanti',
    'Mutuo': 'Casa / Mutuo',
    'Affitto': 'Casa / Mutuo',
}

def classify(description: str) -> str:
    for key, cat in CATEGORY_MAP.items():
        if key.lower() in description.lower():
            return cat
    return 'Altro'

totals = collections.Counter()
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        out = row.get('Uscite', '').strip().replace('.', '').replace(',', '.')
        if not out:
            continue
        try:
            amount = float(out)
        except ValueError:
            continue
        desc = row.get('Descrizione', '') + ' ' + row.get('Descrizione_Completa', '')
        cat = classify(desc)
        totals[cat] += amount

overall = sum(totals.values()) or 1.0
perc = {cat: round(amt*100/overall, 1) for cat, amt in totals.items()}
print(json.dumps({'percentages': perc, 'overall_outflows': round(overall,2)}, indent=2, ensure_ascii=False)) 
from PyPDF2 import PdfReader
import re, glob
line_pattern = re.compile(r'^(?P<merchant>.+?)\s+(?P<amount>[0-9]+,[0-9]{2})$')
for pdf in glob.glob('Spese/*.pdf'):
    print('\n---', pdf)
    count=0
    for page in PdfReader(pdf).pages:
        txt = page.extract_text() or ''
        for line in txt.split('\n'):
            m = line_pattern.match(line.strip())
            if m:
                print(m.group('merchant'))
                count += 1
                if count >= 20:
                    break
        if count >= 20:
            break 
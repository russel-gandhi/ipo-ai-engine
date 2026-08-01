import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
data = json.load(open('backend/src/data/live_ipos.json', encoding='utf-8'))
print('Last updated:', data['last_updated'])
print('Total IPOs:', len(data['ipos']))
print()
for ipo in data['ipos']:
    ab = ipo.get('about') or ''
    name = ipo['name']
    sector = str(ipo.get('sector'))
    lot = ipo.get('lot_size')
    fin = 'yes' if ipo.get('financials') else 'no'
    about_start = ab[:60]
    print(f"{name[:30]:30s} | sector={sector[:18]:18s} | lot={str(lot):6s} | fin={fin} | about={about_start!r}")

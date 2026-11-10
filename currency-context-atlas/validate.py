import csv,json,math
from pathlib import Path
root=Path(__file__).parent
with (root/'exchange-rates.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==78 and len({(r['iso3'],r['year']) for r in rows})==78
for r in rows:
 if r['local_currency_per_usd_annual_average']:
  assert float(r['local_currency_per_usd_annual_average'])>0
  assert abs(float(r['index_2019_100'])-float(r['local_currency_per_usd_annual_average'])/float(r['base_2019_rate'])*100)<0.000001
  if r['year']=='2019':assert float(r['index_2019_100'])==100
snapshot=json.loads((root/'source-snapshot.json').read_text())['PA.NUS.FCRF']['observations']
raw={(r['countryiso3code'],r['date']):r['value'] for r in snapshot}
assert all(float(r['local_currency_per_usd_annual_average'])==raw[(r['iso3'],r['year'])] for r in rows if r['local_currency_per_usd_annual_average'])
print('PASS:78 original FX values, unique country/year keys and2019-base arithmetic')

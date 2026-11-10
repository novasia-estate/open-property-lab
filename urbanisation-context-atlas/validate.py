import csv,json
from pathlib import Path
r=Path(__file__).parent
with (r/'urbanisation.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==78 and len({(x['iso3'],x['year']) for x in rows})==78
snapshot=json.loads((r/'source-snapshot.json').read_text())
for col,code in [('urban_share_pct','SP.URB.TOTL.IN.ZS'),('urban_population','SP.URB.TOTL'),('total_population','SP.POP.TOTL')]:
 raw={(x['countryiso3code'],x['date']):x['value'] for x in snapshot[code]['observations']}
 for row in rows:
  expected=raw[(row['iso3'],row['year'])]
  assert (row[col]=='') if expected is None else float(row[col])==expected
  if col=='urban_share_pct' and row[col]:assert 0<=float(row[col])<=100
print('PASS:234 original urban/population values, unique country/year keys, shares0–100')

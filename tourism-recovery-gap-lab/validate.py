import csv,json
from pathlib import Path
r=Path(__file__).parent
with (r/'arrivals.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==78 and len({(x['iso3'],x['year']) for x in rows})==78
raw={(x['countryiso3code'],x['date']):x['value'] for x in json.loads((r/'source-snapshot.json').read_text())['ST.INT.ARVL']['observations']}
for x in rows:
 expected=raw[(x['iso3'],x['year'])]
 assert (x['international_arrivals']=='') if expected is None else float(x['international_arrivals'])==expected
 assert bool(x['international_arrivals'])==(x['status']=='reported')
 if x['recovery_2019_100']:assert abs(float(x['recovery_2019_100'])-float(x['international_arrivals'])/float(x['baseline_2019'])*100)<0.000001
print('PASS:78 source keys, missingness preserved,2019 baseline arithmetic')

import csv,json,math
from pathlib import Path
r=Path(__file__).parent
with (r/'routes.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
raw={x['case_id']:x['response'] for x in json.loads((r/'route-responses.json').read_text())}
assert len(rows)==12 and len({x['case_id'] for x in rows})==12
for x in rows:
 if x['road_m']:
  assert float(x['road_m'])==raw[x['case_id']]['routes'][0]['distance']
  assert abs(float(x['road_over_straight'])-float(x['road_m'])/float(x['queried_straight_m']))<0.000051
  assert float(x['start_snap_m'])>=0 and float(x['end_snap_m'])>=0
print('PASS:12 route inputs, cached road distances, ratios and explicit snapping fields')

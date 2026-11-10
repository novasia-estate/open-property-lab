import unittest,json,copy
from pathlib import Path
from fractions import Fraction as F
from topology import analyse,ring
EXAMPLES=json.loads((Path(__file__).parent/'examples.json').read_text())
class TopologyChecks(unittest.TestCase):
 def test_clean_partition(self):
  r=analyse(EXAMPLES['clean_partition']);self.assertEqual((r['envelope_area'],r['uncovered_area'],r['multiply_covered_area']),('96','0','0'));self.assertEqual(r['exclusive_interfaces'],[{'regions':['left','right'],'length':'8'}])
 def test_gap_exact(self):self.assertEqual(analyse(EXAMPLES['narrow_gap'])['uncovered_area'],'8/5')
 def test_overlap_is_union_area_not_sum_of_pairs(self):
  r=analyse(EXAMPLES['overlapping_regions']);self.assertEqual(r['multiply_covered_area'],'16/5');self.assertEqual(r['covered_union_area'],'96');self.assertEqual(r['exclusive_interfaces'],[])
 def test_triple_overlap_counted_once(self):
  d=copy.deepcopy(EXAMPLES['clean_partition']);d['regions']=[{'id':str(i),'polygon':d['envelope']} for i in range(3)];r=analyse(d);self.assertEqual(r['multiply_covered_area'],'96')
 def test_l_shape(self):
  r=analyse(EXAMPLES['l_shaped_partition']);self.assertEqual(r['uncovered_area'],'0');self.assertEqual(r['exclusive_interfaces'][0]['length'],'10')
 def test_outside_region_reported(self):self.assertEqual(analyse(EXAMPLES['outside_envelope'])['outside_envelope_area']['overshoot'],'8')
 def test_winding_invariance(self):
  d=copy.deepcopy(EXAMPLES['l_shaped_partition']);expected=analyse(d);d['envelope'].reverse()
  for r in d['regions']:r['polygon'].reverse()
  self.assertEqual(analyse(d),expected)
 def test_translation_preserves_areas(self):
  d=copy.deepcopy(EXAMPLES['clean_partition'])
  for pts in [d['envelope']]+[r['polygon'] for r in d['regions']]:
   for p in pts:p[0]+=17;p[1]-=23
  r=analyse(d);self.assertEqual(r['envelope_area'],'96');self.assertEqual(r['uncovered_area'],'0')
 def test_conservation(self):
  for d in EXAMPLES.values():
   r=analyse(d);self.assertEqual(F(r['covered_union_area'])+F(r['uncovered_area']),F(r['envelope_area']))
 def test_diagonal_rejected(self):
  with self.assertRaises(ValueError):ring([[0,0],[2,0],[3,2],[0,2]])
 def test_self_intersection_rejected(self):
  with self.assertRaises(ValueError):ring([[0,0],[4,0],[4,4],[1,4],[1,-1],[3,-1],[3,3],[0,3]])
 def test_float_coordinates_rejected(self):
  with self.assertRaises(ValueError):ring([[0.1,0],[2,0],[2,2],[0,2]])
 def test_duplicate_ids_rejected(self):
  d=copy.deepcopy(EXAMPLES['clean_partition']);d['regions'][1]['id']='left'
  with self.assertRaises(ValueError):analyse(d)
 def test_no_input_mutation(self):
  before=copy.deepcopy(EXAMPLES);[analyse(d) for d in EXAMPLES.values()];self.assertEqual(EXAMPLES,before)
if __name__=='__main__':unittest.main()

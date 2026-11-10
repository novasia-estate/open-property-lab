import unittest,math,copy
from pathlib import Path
from search_eval import metrics,tokens,eligible,load,evaluate,constrained_rank
ROOT=Path(__file__).parent
class SearchChecks(unittest.TestCase):
 def test_perfect_order(self):
  r=metrics(['a','b','c'],{'a':2,'b':1,'c':0});self.assertEqual(r['ndcg_at_k'],1);self.assertEqual(r['recall_at_k'],1);self.assertAlmostEqual(r['precision_at_k'],2/3)
 def test_known_dcg(self):
  r=metrics(['c','a','b'],{'a':2,'b':1,'c':0});expected=(3/math.log2(3)+1/math.log2(4))/(3+1/math.log2(3));self.assertAlmostEqual(r['ndcg_at_k'],expected);self.assertEqual(r['reciprocal_rank_at_k'],.5)
 def test_missing_results_reduce_precision(self):self.assertAlmostEqual(metrics(['a'],{'a':2,'b':1},3)['precision_at_k'],1/3)
 def test_empty_answerable(self):self.assertEqual(metrics([],{'a':1})['recall_at_k'],0)
 def test_unanswerable_is_distinguished(self):self.assertEqual(metrics([],{'a':0})['relevant_candidates'],0)
 def test_bad_rankings_rejected(self):
  for ranking in [['a','a'],['missing']]:
   with self.subTest(ranking=ranking),self.assertRaises(ValueError):metrics(ranking,{'a':1})
 def test_grades_and_k_rejected(self):
  for grades,k in [({'a':True},3),({'a':-1},3),({'a':4},3),({'a':1},0)]:
   with self.subTest(grades=grades,k=k),self.assertRaises(ValueError):metrics([],grades,k)
 def test_unicode_normalisation(self):self.assertEqual(tokens('МЕТРО Ａ'),tokens('метро a'))
 def test_unknown_is_not_allowed(self):
  row=load(ROOT)[0][4];self.assertEqual(row['pets'],'unknown');self.assertFalse(eligible(row,{'pets':'allowed'}));self.assertTrue(eligible(row,{'pets':'unknown'}))
 def test_boundaries_and_negation_are_structured(self):
  corpus,queries,_=load(ROOT);q=next(q for q in queries if q['id']=='pets-metro-en');ranked=constrained_rank(q,corpus);self.assertEqual(set(ranked),{'amber','dune','fern'});self.assertNotIn('birch',ranked)
 def test_empty_results_for_authored_no_match_case(self):
  corpus,queries,_=load(ROOT);q=next(q for q in queries if q['id']=='no-match-en');self.assertEqual(constrained_rank(q,corpus),[])
 def test_filters_reject_unsupported_or_contradictory(self):
  row=load(ROOT)[0][0]
  for c in [{'pets':'guess'},{'min_bedrooms':4,'max_bedrooms':1},{'min_bedrooms':True},{'unverified_field':1}]:
   with self.subTest(c=c),self.assertRaises(ValueError):eligible(row,c)
 def test_all_candidates_judged(self):
  corpus,queries,qrels=load(ROOT);self.assertEqual(len(corpus),8);self.assertEqual(len(queries),14);self.assertEqual(sum(len(x) for x in qrels.values()),112)
 def test_language_pairs_share_intent_not_text(self):
  _,queries,qrels=load(ROOT)
  for a,b in zip(queries[::2],queries[1::2]):self.assertEqual(a['criteria'],b['criteria']);self.assertEqual(qrels[a['id']],qrels[b['id']]);self.assertNotEqual(a['text'],b['text'])
 def test_evaluation_does_not_mutate_inputs(self):
  before=load(ROOT);evaluate(ROOT);self.assertEqual(load(ROOT),before)
if __name__=='__main__':unittest.main()

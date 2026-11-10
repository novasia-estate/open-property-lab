import json
import tempfile
import unittest
from pathlib import Path
from build_fixtures import build
from reading_order import evaluate, scoped_regions, validate_regions, global_lists


class AssociationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.manifest = build(cls.root)
        cls.report = {x['case']: x for x in evaluate(cls.root)['cases']}

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_positive_control(self):
        self.assertEqual(self.report['ordered']['global_correct_associations'], 3)

    def test_same_count_price_permutation_is_detectably_wrong(self):
        r = self.report['reverse-price-stream']
        self.assertEqual((r['global_associated'], r['global_correct_associations']), (3, 1))

    def test_area_permutation(self):
        self.assertEqual(self.report['reverse-area-stream']['global_correct_associations'], 1)

    def test_both_permutations(self):
        self.assertEqual(self.report['mixed-stream']['global_correct_associations'], 0)

    def test_footer_causes_count_guard_to_abstain(self):
        self.assertEqual(self.report['distractor-footer']['global_status'], 'abstain')

    def test_repeated_ref_needs_page_scope(self):
        r = self.report['repeated-ref-across-pages']
        self.assertEqual(r['global_status'], 'abstain')
        self.assertEqual(r['region_decisions_correct'], 4)

    def test_ambiguous_area_not_guessed(self):
        r = self.report['ambiguous-area']['details']['reviewed_regions'][0]
        self.assertEqual(r['status'], 'abstain')
        self.assertNotIn('fields', r)

    def test_all_explicit_region_decisions_match_annotations(self):
        for r in self.report.values():
            with self.subTest(case=r['case']):
                self.assertEqual(r['region_decisions_correct'], r['expected_regions'])

    def test_sha_tracks_real_pdf_bytes(self):
        import hashlib
        for case in self.manifest:
            actual = self.report[case['name']]['details']['source_sha256']
            self.assertEqual(actual, hashlib.sha256((self.root/'fixtures'/case['file']).read_bytes()).hexdigest())

    def test_invalid_regions_rejected(self):
        samples = [[-1,0,50,50], [0,0,0,50], [0,0,101,50], [0,0,float('nan'),50]]
        for box in samples:
            with self.subTest(box=box), self.assertRaises(ValueError):
                validate_regions([{'key':'a','page':1,'bbox':box}],{1:(100,100)})

    def test_overlapping_and_duplicate_regions_rejected(self):
        for second in [{'key':'b','page':1,'bbox':[10,10,40,40]}, {'key':'a','page':2,'bbox':[0,0,50,50]}]:
            with self.subTest(second=second), self.assertRaises(ValueError):
                validate_regions([{'key':'a','page':1,'bbox':[0,0,50,50]},second],{1:(100,100),2:(100,100)})

    def test_partial_word_abstains(self):
        words=[{'text':'REF:A101','page':1,'x0':5,'top':10,'x1':70,'bottom':20},
               {'text':'AREA:41.00','page':1,'x0':15,'top':30,'x1':80,'bottom':40},
               {'text':'PRICE:2100000','page':1,'x0':15,'top':50,'x1':85,'bottom':60}]
        result=scoped_regions(words,[{'key':'a','page':1,'bbox':[10,0,90,90]}],{1:(100,100)})
        self.assertEqual(result[0]['status'],'abstain')

    def test_unrelated_words_are_not_fields(self):
        self.assertEqual(global_lists([{'text':'REF:A101x'}])['status'],'abstain')


if __name__ == '__main__': unittest.main()

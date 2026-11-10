import io,json,unittest,zipfile
from recovery import recover_pdf,edited_table,csv_bytes,bundle

class RecoveryChecks(unittest.TestCase):
 def setUp(self):self.table={'table_id':'p1-t1','page':1,'bbox':[1,2,3,4],'rows':[['Ref','Price'],['A','=1+1']],'column_count':2,'flags':[]}
 def test_csv_formula_safety_and_json_preservation(self):
  safe=csv_bytes(self.table).decode('utf-8-sig');self.assertIn("'=1+1",safe);self.assertEqual(self.table['rows'][1][1],'=1+1')
 def test_manual_edits_keep_original(self):
  x=edited_table(self.table,[['Ref','Price'],['A','100']]);self.assertEqual(x['original_rows'],self.table['rows']);self.assertTrue(x['user_edited'])
 def test_wrong_width_and_type_rejected(self):
  for rows in [[['x']],[['x',123]],[]]:
   with self.assertRaises(ValueError):edited_table(self.table,rows)
 def test_bundle_is_portable(self):
  with zipfile.ZipFile(io.BytesIO(bundle({'source_sha256':'example'},self.table))) as z:
   self.assertEqual(set(z.namelist()),{'table.csv','provenance.json','README.txt'});self.assertEqual(json.loads(z.read('provenance.json'))['selected_table']['page'],1)
 def test_rejects_oversize_and_non_pdf(self):
  for data in [b'',b'not pdf',b'%PDF-'+b'0'*(10*1024*1024)]:
   with self.assertRaises(ValueError):recover_pdf(data)
 def test_real_digital_table(self):
  try:from reportlab.pdfgen.canvas import Canvas
  except ImportError:self.skipTest('Optional reportlab test fixture builder not installed')
  output=io.BytesIO();c=Canvas(output,pagesize=(300,300))
  for y in [250,220,190]:c.line(20,y,280,y)
  for x in [20,150,280]:c.line(x,190,x,250)
  for x,y,text in [(30,230,'Ref'),(160,230,'Area'),(30,200,'demo-unit'),(160,200,'50')]:c.drawString(x,y,text)
  c.save();raw=output.getvalue();r=recover_pdf(raw)
  self.assertEqual(r['tables'][0]['rows'],[['Ref','Area'],['demo-unit','50']]);self.assertEqual(r['tables'][0]['page'],1);self.assertEqual(len(r['tables'][0]['bbox']),4)

if __name__=='__main__':unittest.main()

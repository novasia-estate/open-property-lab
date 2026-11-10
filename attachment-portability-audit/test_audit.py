import io,stat,tempfile,unittest,zipfile
from pathlib import Path
from audit import audit

class ArchiveChecks(unittest.TestCase):
    def run_case(self,names):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'case.zip'
            with zipfile.ZipFile(p,'w') as z:
                for n in names:z.writestr(n,b'not executed')
            before=p.read_bytes();r=audit(p);self.assertEqual(before,p.read_bytes());return r
    def test_clean_utf8(self):self.assertEqual(self.run_case(['plans/room-a.svg','docs/คำอธิบาย.txt'])['findings'],[])
    def test_path_traversal(self):self.assertIn('unsafe_path',{x['code'] for x in self.run_case(['../outside','C:/secret','/root'])['findings']})
    def test_case_collision(self):self.assertIn('portable_name_collision',{x['code'] for x in self.run_case(['Photo.JPG','photo.jpg'])['findings']})
    def test_unicode_normalization_collision(self):self.assertIn('portable_name_collision',{x['code'] for x in self.run_case(['café.txt','cafe\u0301.txt'])['findings']})
    def test_reserved_and_stream(self):self.assertEqual({x['code'] for x in self.run_case(['CON.txt','report:stream','photo.'])['findings']},{'windows_reserved_name','windows_invalid_character','trailing_dot_or_space'})
    def test_file_directory_conflict(self):self.assertIn('file_directory_conflict',{x['code'] for x in self.run_case(['a','a/b.txt'])['findings']})
    def test_symlink_not_followed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'links.zip';i=zipfile.ZipInfo('link');i.create_system=3;i.external_attr=(stat.S_IFLNK|0o777)<<16
            with zipfile.ZipFile(p,'w') as z:z.writestr(i,'../../private')
            self.assertEqual(audit(p)['findings'][0]['code'],'symlink')
    def test_inspection_limits_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'limit.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr('a',b'abc')
            with self.assertRaises(ValueError):audit(p,max_members=0)
            with self.assertRaises(ValueError):audit(p,max_total_bytes=2)

if __name__=='__main__':unittest.main()

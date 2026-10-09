import pathlib,re,unittest
class DocsTests(unittest.TestCase):
    def test_persian_chapters_present(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        self.assertEqual(len(list((root/'docs/fa').glob('[0-9][0-9]-*.md'))),16)
    def test_local_links(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        count=0
        for p in (root/'docs/fa').glob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
                count+=1
                if link.startswith(('http:','https:','#','mailto:')):continue
                with self.subTest(file=p.name,link=link):self.assertTrue((p.parent/link.split('#')[0]).exists())
        self.assertGreater(count,30)

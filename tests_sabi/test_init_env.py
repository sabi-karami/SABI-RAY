import importlib.util,pathlib,tempfile,unittest,os
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sabi_init_env',ROOT/'scripts/init-env.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
class InitEnvTests(unittest.TestCase):
    def test_private_creation_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            filename=str(pathlib.Path(tmp)/'scripts/init-env.py')
            with patch.object(helper,'__file__',filename),patch('builtins.input',side_effect=['panel.example.com','owner']),patch.object(helper.getpass,'getpass',return_value='Test-Only-Password-11!'),patch('builtins.print'):
                helper.main()
            path=pathlib.Path(tmp)/'.env';self.assertEqual(path.stat().st_mode&0o777,0o600)
            self.assertIn("SABI_INITIAL_PASSWORD='",path.read_text())
            with patch.object(helper,'__file__',filename),self.assertRaises(ValueError):helper.main()
    def test_mismatch_no_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            filename=str(pathlib.Path(tmp)/'scripts/init-env.py')
            with patch.object(helper,'__file__',filename),patch('builtins.input',side_effect=['panel.example.com','owner']),patch.object(helper.getpass,'getpass',side_effect=['Test-Only-Password-11!','Mismatch-Password-22!']),self.assertRaises(ValueError):helper.main()
            self.assertFalse((pathlib.Path(tmp)/'.env').exists())

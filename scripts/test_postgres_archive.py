"""Maintenance regression checks only; not the Unit 4 application test report."""
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import unittest

sys.path.insert(0,str(Path(__file__).parent))
from postgres_archive import extract_runtime

class ArchiveFixChecks(unittest.TestCase):
    def fixture(self,archive,root='pgsql/',extra=None,omit=()):
        with ZipFile(archive,'w') as z:
            for p in ['bin/pg_ctl.exe','bin/initdb.exe','bin/postgres.exe','bin/libpq.dll','lib/example.dll','share/postgresql.conf.sample']:
                if p not in omit:z.writestr(root+p,b'runtime')
            for p in extra or []:z.writestr(root+p,b'excluded')
    def test_excludes_pgadmin_long_paths_and_preserves_runtime(self):
        with TemporaryDirectory() as d:
            p=Path(d);self.fixture(p/'pg.zip',extra=['pgAdmin 4/'+('x/'*180)+'file.js','doc/manual.txt'])
            with ZipFile(p/'pg.zip') as z:extract_runtime(z,p/'runtime')
            self.assertEqual((p/'runtime/bin/libpq.dll').read_bytes(),b'runtime')
            self.assertTrue((p/'runtime/share/postgresql.conf.sample').exists())
            self.assertFalse((p/'runtime/pgAdmin 4').exists())
            self.assertFalse((p/'runtime/doc').exists())
    def test_unwrapped_archive(self):
        with TemporaryDirectory() as d:
            p=Path(d);self.fixture(p/'pg.zip',root='')
            with ZipFile(p/'pg.zip') as z:extract_runtime(z,p/'runtime')
            self.assertTrue((p/'runtime/bin/pg_ctl.exe').exists())
    def test_missing_server_executable_rejected(self):
        with TemporaryDirectory() as d:
            p=Path(d);self.fixture(p/'pg.zip',omit=['bin/postgres.exe'])
            with ZipFile(p/'pg.zip') as z:
                with self.assertRaises(OSError):extract_runtime(z,p/'runtime')
    def test_traversal_rejected_before_writing(self):
        with TemporaryDirectory() as d:
            p=Path(d);self.fixture(p/'pg.zip',extra=['bin/../../escape.txt'])
            with ZipFile(p/'pg.zip') as z:
                with self.assertRaises(OSError):extract_runtime(z,p/'runtime')
            self.assertFalse((p/'escape.txt').exists())
            self.assertFalse((p/'runtime').exists())
    def test_missing_control_executable_rejected(self):
        with TemporaryDirectory() as d:
            p=Path(d);self.fixture(p/'pg.zip',omit=['bin/pg_ctl.exe'])
            with ZipFile(p/'pg.zip') as z:
                with self.assertRaises(OSError):extract_runtime(z,p/'runtime')

if __name__=='__main__':unittest.main(verbosity=2)

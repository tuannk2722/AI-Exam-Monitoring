from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from ai_exam_monitoring.training.colab_launcher import (
    committed_state,
    export_metadata,
    extract_bundle,
    sha256,
)


class ColabBootstrapTests(unittest.TestCase):
    def test_bootstrap_imports_from_zip_without_host_ML_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=Path(__file__).resolve().parents[1]/'src'
            archive=root/'host-bootstrap.zip'
            with zipfile.ZipFile(archive,'w') as z:
                for name in ('ai_exam_monitoring/__init__.py',
                             'ai_exam_monitoring/training/__init__.py',
                             'ai_exam_monitoring/training/colab_launcher.py'):
                    z.write(source/name,'src/'+name)
            script="""
import importlib.abc,sys
class BlockML(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'torch','torchvision','numpy','PIL'}:
            raise AssertionError('Host bootstrap imported ML: '+fullname)
sys.meta_path.insert(0,BlockML())
from ai_exam_monitoring.training import colab_launcher
assert 'host-bootstrap.zip' in colab_launcher.__file__
print('PASS')
"""
            env={**os.environ,'PYTHONPATH':str(archive)+'/src'}
            result=subprocess.run([sys.executable,'-c',script],cwd=root,env=env,
                                  capture_output=True,text=True,check=True)
            self.assertIn('PASS',result.stdout)

    def archive(self, root, files):
        p=root/'bundle.zip'
        with zipfile.ZipFile(p,'w') as z:
            for name,data in files.items():
                z.writestr(name,data)
            z.writestr('bundle-manifest.json',json.dumps({
                'schema_version':'private-colab-bundle-v1',
                'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()}}))
        return p

    def test_exact_bundle_and_resumed_extraction_preserve_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            p=self.archive(root,{'src/code.py':b'print(1)\n','data/crop.bin':b'pixels'})
            target=root/'workspace'
            extract_bundle(p,sha256(p),target)
            self.assertEqual((target/'data/crop.bin').read_bytes(),b'pixels')
            extract_bundle(p,sha256(p),target)
            (target/'src/code.py').write_bytes(b'changed')
            with self.assertRaises(RuntimeError):
                extract_bundle(p,sha256(p),target)
            self.assertEqual((target/'src/code.py').read_bytes(),b'changed')

    def test_bad_sha_path_and_unlisted_member_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            p=self.archive(root,{'../escape':b'unsafe'})
            with self.assertRaises(RuntimeError):
                extract_bundle(p,sha256(p),root/'workspace')
            self.assertFalse((root/'escape').exists())
            p.unlink()
            p=self.archive(root,{'code.py':b'ok'})
            with self.assertRaises(RuntimeError):
                extract_bundle(p,'0'*64,root/'other')
            with zipfile.ZipFile(p,'a') as z:
                z.writestr('unlisted.txt','extra')
            with self.assertRaises(RuntimeError):
                extract_bundle(p,sha256(p),root/'other')

    def test_recovery_uses_committed_version_and_metadata_omits_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'runs').mkdir()
            (root/'versions').mkdir()
            old=b'{"started_at":123,"status":"RUNNING"}'
            digest=hashlib.sha256(old).hexdigest()
            (root/'versions'/digest).write_bytes(old)
            (root/'runs/campaign.json').write_text('uncommitted bytes')
            (root/'runs/best.pt').write_bytes(b'weights')
            (root/'mirror-manifest.json').write_text(json.dumps({'files':{
                'runs/campaign.json':{'sha256':digest,'bytes':len(old)},
                'runs/best.pt':{'sha256':sha256(root/'runs/best.pt'),'bytes':7}}}))
            self.assertEqual(committed_state(root)['started_at'],123)
            output=root/'metadata.zip'
            export_metadata(root,output,root/'bootstrap')
            with zipfile.ZipFile(output) as z:
                self.assertEqual(z.read('runs/campaign.json'),old)
                self.assertNotIn('runs/best.pt',z.namelist())

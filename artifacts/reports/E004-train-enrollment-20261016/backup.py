"""Local lossless snapshot, full verification and byte-exact restore drill."""
import json
import shutil
import subprocess
from pathlib import Path

from ai_exam_monitoring.common.history import create, restore, verify
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import write_json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
NAME = 'e004-c345-execution-20261016'
archive = ROOT / 'archive' / f'{NAME}.zip'
assert not archive.exists(), 'Do not reseal existing backup'
paths = set()
folders = [ROOT / 'src', ROOT / 'tests', ROOT / 'requirements',
           ROOT / 'configs/experiments/E004-C345-20261016', HERE,
           ROOT / 'outputs/E004-C345-W-H', ROOT / 'outputs/E004-C345-W-H-SMOKE',
           ROOT / 'outputs/E004-C345-W-H-reload', ROOT / 'outputs/E004-train-enrollment-20261016',
           ROOT / 'outputs/E004-C345-W-H-orphan-snapshot',
           ROOT / 'data/interim/E004-train-enrollment-20261016',
           ROOT / 'data/processed/pilot-b/pilot-b-20261016-v10',
           ROOT / 'data/processed/e004/E004-c345-development-20261016']
for folder in folders:
    assert folder.is_dir(), folder
    for path in folder.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            paths.add(path.relative_to(ROOT).as_posix())
accepted = json.loads((HERE.parent / 'E004-accepted-coverage-20261016/accepted-ledger.json').read_text(encoding='utf8'))
for row in accepted:
    paths.update((row['crop'], row['source']))
config = json.loads((ROOT / 'outputs/E004-C345-W-H/resolved-config.json').read_text(encoding='utf8'))
for field in ('weights', 'weights_license', 'head_initialization'):
    paths.add(config[field]['path'])
paths.add(config['head_provenance']['parent_checkpoint']['path'])
paths.update(['pyproject.toml', 'configs/datasets/E004-c345-20261016.json',
              'outputs/E004-C345-resume.stdout.log', 'outputs/E004-C345-resume.stderr.log',
              'docs/data.md', 'docs/training.md', 'docs/decisions.md', 'docs/status.md'])
manifest = create(ROOT, archive, paths, name=NAME, progress=lambda n: print('Archived', n, flush=True))
digest = sha256_file(archive)
verify(archive, expected_sha256=digest)
destination = Path('\\\\?\\' + str(ROOT / 'outputs/_scratch/c345-backup-restore'))
assert not destination.exists()
count = restore(archive, destination, expected_sha256=digest)
assert count == len(manifest.files)
for entry in manifest.files:
    assert sha256_file(destination / entry.path) == entry.sha256
assert destination.resolve().is_relative_to(Path('\\\\?\\' + str(ROOT / 'outputs/_scratch')).resolve())
shutil.rmtree(destination)
subprocess.run([str(ROOT / '.venv/Scripts/dvc.exe'), 'add', str(archive)], cwd=ROOT, check=True)
receipt = {'archive': archive.relative_to(ROOT).as_posix(), 'sha256': digest,
           'files': len(manifest.files), 'unique_blobs': len({r.sha256 for r in manifest.files}),
           'original_bytes': sum(r.size for r in manifest.files), 'archive_bytes': archive.stat().st_size,
           'byte_exact_restore': 'PASS', 'restored_files': count,
           'scope': 'local_only; same drive, no remote upload',
           'parent_source_archive': 'archive/e004-v9-consolidation-20261013.zip'}
write_json(HERE / 'backup-receipt.json', receipt)
index = ROOT / 'archive/index.json'
registry = json.loads(index.read_text(encoding='utf8'))
assert not any(row['name'] == NAME for row in registry['bundles'])
registry['bundles'].append({
    'name': NAME, 'path': receipt['archive'], 'sha256': digest, 'files': receipt['files'],
    'unique_blobs': receipt['unique_blobs'], 'original_bytes': receipt['original_bytes'],
    'archive_bytes': receipt['archive_bytes'], 'scope': 'local_only',
    'owner_authorization': 'Approved C345 enrollment/research lifecycle; local preservation only',
    'validation': {'byte_exact_restore': 'PASS', 'restored_files': count,
                   'receipt': (HERE / 'backup-receipt.json').relative_to(ROOT).as_posix()}})
write_json(index, registry)
print(json.dumps(receipt, indent=2), flush=True)

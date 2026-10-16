"""Rebuild the accepted packages and verify byte preservation without inference."""
import json
import shutil
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import verify_payload
from ai_exam_monitoring.data.pilot_package import build_pilot_package
from ai_exam_monitoring.data.pilot_schema import read_records
from ai_exam_monitoring.training.artifacts import code_identity, write_json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESTORE = Path('\\\\?\\' + str(ROOT / 'outputs/_scratch/c345-restore'))
PREFIX = 'outputs/_scratch/e004-v9-consolidation-20261013/sources'

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

accepted = read(HERE.parent / 'E004-accepted-coverage-20261016/accepted-ledger.json')
new = {r['id']: r for r in accepted}
result = {}
for info in read(HERE / 'package-pointers.json').values():
    package = ROOT / info['package']
    verify_payload(package)
    rows = read_records(package / 'review-ledger.jsonl')
    roots = {r.source.source_id: RESTORE / PREFIX / r.source.source_id for r in rows}
    for row in rows:
        if row.sample_id in new:
            entry = new[row.sample_id]
            roots[row.source.source_id] = (ROOT / entry['source']).parent.parent
            assert row.crop.crop_sha256 == sha256_file(ROOT / entry['crop'])
            assert (package / row.crop.crop_relpath).read_bytes() == (ROOT / entry['crop']).read_bytes()
    destination = ROOT / 'outputs/_scratch/c345-rebuild' / package.name
    assert not destination.exists(), 'Preserve existing rebuild until inspected'
    inputs = {r.sample_id: package / r.crop.crop_relpath for r in rows
              if r.crop and (package / r.crop.crop_relpath).is_file()}
    selection = [json.loads(line) for line in (package / 'selection.jsonl').read_text(encoding='utf8').splitlines()]
    build_pilot_package(rows, destination, roots, inputs, selection,
                        read(package / 'release.json'), [r.sample_id for r in rows])
    verify_payload(destination)
    assert (package / 'checksums.sha256').read_bytes() == (destination / 'checksums.sha256').read_bytes()
    result[package.name] = {'deterministic_rebuild': 'PASS', 'accepted_crop_exact_bytes': 345,
                            'payload_sha256': sha256_file(package / 'checksums.sha256')}
    assert destination.resolve().is_relative_to((ROOT / 'outputs/_scratch/c345-rebuild').resolve())
    shutil.rmtree(destination)
    print(package.name, 'rebuild PASS', flush=True)
baseline = read(ROOT / 'outputs/E004-RC1-W-H/code-provenance.json')['files']
current = code_identity()['files']
changed = [p for p in sorted(set(baseline) | set(current)) if baseline.get(p) != current.get(p)]
result['code_changes_since_baseline'] = changed
result['training_math_model_transform_unchanged'] = all(
    p in {'data/pilot_schema.py', 'data/pilot_package.py', 'training/data.py', 'data/crop_bundle_audit.py'}
    for p in changed)
assert result['training_math_model_transform_unchanged'], changed
write_json(HERE / 'package-validation.json', result)

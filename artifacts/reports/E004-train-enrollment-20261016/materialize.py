"""Bind the owner-approved data-only experiment to exact local artifacts."""
import copy
import json
import sys
from pathlib import Path

import yaml

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records, record_to_dict
from ai_exam_monitoring.training.adaptation_config import (
    config_from_dict,
    verify_adaptation_approval,
)
from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'configs/experiments/E004-C345-20261016'
OUT.mkdir(parents=True, exist_ok=True)
KIND = sys.argv[1]
assert KIND in ('smoke', 'research')

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def pin(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha256_file(path)}

def fresh(path, value):
    if path.exists():
        assert read(path) == value, f'Preserve pinned artifact: {path}'
    else:
        write_json(path, value)

approval_path = HERE / 'owner-enrollment-approval.json'
owner_pin = pin(approval_path)
baseline = read(ROOT / 'outputs/E004-RC1-W-H/resolved-config.json')
config = copy.deepcopy(baseline)
package = ROOT / 'data/processed/e004/E004-c345-development-20261016'
records = {r.sample_id: r for r in read_records(package / 'manifest.jsonl')}
new_ids = read(approval_path)['new_train_ids']
data = {'dataset': package.relative_to(ROOT).as_posix(), 'dataset_version': package.name,
        'split_version': 'E004-c345-preserved-20261016', 'encoding_version': 'pilot-b-targets-v1',
        'payload_sha256': sha256_file(package / 'checksums.sha256')}
for cohort in config['cohorts']:
    cohort['data'] = data.copy()
    if cohort['role'] == 'train':
        cohort['sample_ids'] = sorted(cohort['sample_ids'] + new_ids)
        assert len(cohort['sample_ids']) == 1061
protocol = read(ROOT / baseline['protocol']['path'])
protocol['decision_ref'] = owner_pin['path']
protocol['waiver_approval'] = owner_pin
for sample_id in new_ids:
    protocol['family_assignments'][sample_id] = {
        'family_id': 'E004-CROP-TRAIN-Q001', 'owner_accepted': True,
        'independence_verified': False, 'evidence_refs': [owner_pin['path']]}
for cohort in config['cohorts']:
    protocol['cohorts'][cohort['name']] = {
        'role': cohort['role'],
        'records_sha256': digest_json([record_to_dict(records[s]) for s in cohort['sample_ids']])}
fresh(OUT / 'protocol.json', protocol)
config['protocol'] = pin(OUT / 'protocol.json')
config['experiment_id'] = 'E004-C345-W-H' + ('-SMOKE' if KIND == 'smoke' else '')
config['hypothesis'] = 'Add 345 accepted training crops to RC1-W-H; same recipe, initialization and selection71; research only'
config['run_kind'] = KIND
config['approval_ref'] = (OUT / f'{KIND}-approval.json').relative_to(ROOT).as_posix()
evidence = [owner_pin, pin(HERE / 'package-pointers.json')]
if KIND == 'smoke':
    config['max_epochs'] = 1
    config['wall_time_seconds'] = 7200
else:
    smoke = ROOT / 'outputs/E004-C345-W-H-SMOKE'
    assert read(smoke / 'run.json')['status'] == 'FINISHED'
    evidence += [pin(smoke / 'run.json'), pin(smoke / 'checksums.json')]
ready = {'schema_version': 'adaptation-readiness-v2', 'status': 'approved',
         'owner': config['owner'], 'scope': KIND, 'protocol_sha256': config['protocol']['sha256'],
         'cohorts_sha256': digest_json(config['cohorts']), 'decision_ref': owner_pin['path'],
         'waiver_approval': owner_pin,
         'gates': {'G0': True, 'G1': True, 'G2': 'owner_waived', 'G3': 'owner_waived'},
         'evidence_pins': evidence}
fresh(OUT / f'{KIND}-readiness.json', ready)
config['readiness'] = pin(OUT / f'{KIND}-readiness.json')
parsed = config_from_dict(config)
authorization = {'status': 'approved', 'owner': config['owner'],
                 'scope': 'local_classifier_research', 'run_kind': KIND,
                 'configs': {config['experiment_id']: digest_json(parsed.to_dict())},
                 'config_signatures': {config['experiment_id']: parsed.match_signature()},
                 'code_sha256': code_identity()['sha256'], 'owner_authorization': owner_pin,
                 'final_test_inference_authorized': False}
fresh(OUT / f'{KIND}-approval.json', authorization)
path = OUT / f"{config['experiment_id']}.yaml"
if path.exists():
    assert yaml.safe_load(path.read_text(encoding='utf8')) == config
else:
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf8')
verify_adaptation_approval(parsed, ROOT)
cohorts, _ = prepare_cohorts(parsed, ROOT)
allowed = {'experiment_id', 'hypothesis', 'approval_ref', 'run_kind', 'cohorts', 'protocol', 'readiness'}
if KIND == 'smoke':
    allowed |= {'max_epochs', 'wall_time_seconds'}
changes = [key for key in config if config[key] != baseline[key]]
assert set(changes) <= allowed, changes
fresh(HERE / f'{KIND}-config-validation.json', {
    'status': 'PASS', 'baseline': pin(ROOT / 'outputs/E004-RC1-W-H/resolved-config.json'),
    'config': pin(path), 'code_sha256': code_identity()['sha256'],
    'changed_fields': changes, 'cohorts': {c.name: len(c.ids) for c in cohorts},
    'test_inference': False, 'recipe_preserved': KIND == 'research'})
print(path, 'PASS', flush=True)

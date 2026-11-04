"""Reproduce the metadata-only E008 audit; never load checkpoints or run inference."""
import hashlib
import json
import math
import shutil
import zipfile
from pathlib import Path, PurePosixPath

import torch
import yaml

from ai_exam_monitoring.training.artifacts import code_identity, digest_json
from ai_exam_monitoring.training.adaptation_train import runtime_signature
from ai_exam_monitoring.training.calibration import calibrate_exact, evaluate_pair
from ai_exam_monitoring.training.metrics import evaluate_scores
from ai_exam_monitoring.training.representation_campaign import champion_key

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
SOURCE = Path('C:/Users/OS/Downloads/E008-V14-results-metadata.zip')
DEST = ROOT / 'outputs/E008-V14-Colab-20261024/imported-metadata-20261025'
TARGETS = ['phone_use', 'looking_around']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, value):
    (REPORT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                        allow_nan=False) + '\n', encoding='utf-8')


def subset(actual, expected):
    if isinstance(actual, dict):
        for key, value in actual.items():
            subset(value, expected[key])
    elif isinstance(actual, float):
        assert math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10), (actual, expected)
    else:
        assert actual == expected, (actual, expected)


def main():
    with zipfile.ZipFile(SOURCE) as archive:
        entries = archive.infolist()
        assert len({x.filename for x in entries}) == len(entries)
        assert sum(x.file_size for x in entries) < 100_000_000
        for item in entries:
            path = PurePosixPath(item.filename)
            assert not path.is_absolute() and '..' not in path.parts
            assert '\\' not in item.filename and ':' not in item.filename
            assert path.suffix in {'.json', '.yaml', '.log', '.txt'}
            assert (item.external_attr >> 16) & 0o170000 != 0o120000
        data = {x.filename: archive.read(x) for x in entries}
    read = lambda name: json.loads(data[name])
    campaign = read('runs/campaign.json')
    smoke = read('smoke-receipt.json')
    handoff = json.loads((REPORT / 'handoff.json').read_text(encoding='utf-8'))
    design_path = ROOT / campaign['design']['path']
    design = json.loads(design_path.read_text(encoding='utf-8'))
    def verify_pins(value):
        if isinstance(value, dict):
            if set(value) == {'path', 'sha256'}:
                path = value['path']
                if '/materialized/' in path:
                    content = data['configs/' + path.split('/materialized/')[1]]
                elif path == design['smoke_receipt']:
                    content = data['smoke-receipt.json']
                else:
                    content = (ROOT / path).read_bytes()
                assert sha(content) == value['sha256'], path
            else:
                for child in value.values():
                    verify_pins(child)
        elif isinstance(value, list):
            for child in value:
                verify_pins(child)
    verify_pins(design)
    assert sha(design_path.read_bytes()) == campaign['design']['sha256'] == smoke['design_sha256']
    assert campaign['code_sha256'] == handoff['code_sha256'] == code_identity()['sha256']
    assert campaign['status'] == 'FINISHED' and smoke['status'] == 'PASS'
    assert campaign['elapsed_seconds'] < 14400 and smoke['elapsed_seconds'] < 1800
    assert smoke['checks'] == dict(resume='PASS', reload='PASS', stage_transition='PASS')
    assert runtime_signature(read('runs/runtime.json')) == smoke['runtime_sha256']
    assert campaign['final_test_inference_authorized'] is False
    assert campaign['smoke_runs'] == smoke['runs']
    manifest = [json.loads(line) for line in (ROOT / 'data/processed/pilot-b/pilot-b-20261024-v14/manifest.jsonl').read_text(encoding='utf-8').splitlines()]
    records = {r['sample_id']: r for r in manifest}
    inventory, missing, checks = {}, [], 0
    for name, content in data.items():
        inventory[name] = {'sha256': sha(content), 'bytes': len(content)}
        if name.endswith('/checksums.json'):
            for relative, expected in read(name).items():
                member = str(PurePosixPath(name).parent / relative)
                if member not in data:
                    missing.append({'path': member, 'sha256': expected})
                else:
                    assert sha(data[member]) == expected, member
                    checks += 1
    summaries, errors, ranking = [], {}, []
    for phase in ['smoke', 'research']:
        readiness = read('configs/' + phase + '/readiness.json')
        approval = read('configs/' + phase + '/approval.json')
        verify_pins(readiness)
        verify_pins(approval)
        assert readiness['protocol_sha256'] == sha(data['configs/' + phase + '/protocol.json'])
        assert approval['code_sha256'] == campaign['code_sha256']
        for item in campaign[phase + '_runs']:
            rid = item['id']
            base = 'runs/' + rid + '/'
            for key, name in [('config', 'configs/' + phase + '/' + rid + '.yaml'),
                              ('run', base + 'run.json'), ('metrics', base + 'metrics.json')]:
                assert sha(data[name]) == item[key]['sha256'], name
            run, config = read(base + 'run.json'), read(base + 'resolved-config.json')
            assert run['status'] == 'FINISHED' and run['error'] is None
            assert run['code_sha256'] == campaign['code_sha256']
            assert run['payload_sha256'] == smoke['payload_sha256'] == '51fe689b7161737ddce1b6e2845c887a58e9c91fbcd01bb1dc0768b13f351f5b'
            assert run['config_sha256'] == digest_json(config)
            assert approval['configs'][rid] == run['config_sha256']
            raw_config = yaml.safe_load(data['configs/' + phase + '/' + rid + '.yaml'])
            subset(raw_config, config)
            assert runtime_signature(run['environment']) == smoke['runtime_sha256']
            assert read(base + 'code-provenance.json') == code_identity()
            assert config['max_epochs'] == (5 if phase == 'smoke' else 24)
            assert config['pooling'] == {'G0': 'global_mean', 'G1': 'context_2x2', 'A1': 'person_2x2'}[item['arm']]
            metrics = read(base + 'metrics.json')
            calibration = read(base + 'calibration.json')
            history = read(base + 'history.json')
            assert len(history) == run['completed_epochs']
            chosen = min(history, key=lambda r: (-r['val_macro_ap'], r['val_loss'], r['epoch']))
            assert chosen['epoch'] == run['best_epoch']
            assert history[2]['stage'] == 'warmup_head_only'
            assert history[3]['stage'] == 'finetune_last_two_blocks'
            reload_base = 'runs/' + rid + '-reload/'
            reload = read(reload_base + 'evaluation.json')
            assert reload['status'] == 'FINISHED'
            assert reload['checkpoint_sha256'] == read(base + 'checksums.json')['best.pt'] == calibration['checkpoint_sha256']
            assert reload['config_sha256'] == run['config_sha256']
            assert reload['code_sha256'] == run['code_sha256']
            assert reload['protocol_sha256'] == sha(data['configs/' + phase + '/protocol.json'])
            assert read(reload_base + 'metrics.json') == {'selection': metrics['selection']}
            assert data[reload_base + 'predictions-selection.json'] == data[base + 'predictions-selection.json']
            for cohort, split, size in [('train', 'train', 1199), ('selection', 'val', 156)]:
                preds = read(base + 'predictions-' + cohort + '.json')
                ids = [r['sample_id'] for r in preds]
                assert len(ids) == len(set(ids)) == size
                assert set(ids) == {r['sample_id'] for r in manifest if r['split'] == split}
                for row in preds:
                    original = records[row['sample_id']]
                    assert row['split'] == split and row['target_order'] == TARGETS
                    assert row['group_id'] == original['group']['leakage_group_id']
                    for c, target in enumerate(TARGETS):
                        state = original[target]['state']
                        assert bool(row['mask'][c]) == (state != 'unknown')
                        if row['mask'][c]:
                            assert row['targets'][c] == int(state == 'positive')
                        assert row['decisions'][c] == (row['scores'][c] >= .5)
                        assert row['calibrated_decisions'][c] == (row['scores'][c] >= calibration['thresholds'][c])
                    assert row['calibrated_thresholds'] == calibration['thresholds']
                scores = torch.tensor([r['scores'] for r in preds], dtype=torch.float64)
                values = torch.tensor([[v if v is not None else 0 for v in r['targets']] for r in preds])
                masks = torch.tensor([r['mask'] for r in preds], dtype=torch.bool)
                subset(evaluate_scores(scores, values, masks, .5), metrics[cohort])
                calibrated = evaluate_pair(scores, values, masks, tuple(calibration['thresholds']), [r['group_id'] for r in preds])
                subset(calibrated, metrics[cohort]['calibrated_evaluation'])
                if cohort == 'selection':
                    assert digest_json(ids) == calibration['selection_ids_sha256']
                    assert list(calibrate_exact(scores, values, masks)) == calibration['thresholds']
                    if phase == 'research':
                        errors[rid] = {target: {
                            kind: [r['sample_id'] for r in preds if r['mask'][c] and
                                   r['targets'][c] == truth and r['calibrated_decisions'][c] == decision]
                            for kind, truth, decision in [('fp', 0, True), ('fn', 1, False)]}
                            for c, target in enumerate(TARGETS)}
            if phase == 'research':
                summaries.append({'id': rid, 'arm': item['arm'], 'seed': item['seed'],
                                  'best_epoch': run['best_epoch'], 'completed_epochs': run['completed_epochs'],
                                  'elapsed_seconds': run['elapsed_seconds'],
                                  'macro_ap': metrics['selection']['macro_ap'],
                                  'raw_targets': metrics['selection']['targets'],
                                  'calibrated': metrics['selection']['calibrated_evaluation'],
                                  'thresholds': calibration['thresholds']})
                if item['seed'] == design['screening_seed']:
                    ranking.append(champion_key(item['arm'], metrics['selection']))
    champion = min(ranking)[-1]
    assert champion == campaign['screening_champion'] == 'G0'
    assert {(r['arm'], r['seed']) for r in summaries} == {('G0', 20261023), ('G1', 20261023), ('A1', 20261023), ('G0', 20261024), ('G0', 20261025)}
    for arm in ['G0', 'A1']:
        for name in ['history.json', 'metrics.json', 'predictions-selection.json', 'predictions-train.json']:
            assert data[f'runs/E008-V14-SMOKE-{arm}-FULL/{name}'] == data[f'runs/E008-V14-SMOKE-{arm}-RESUME/{name}']
    init = [read('runs/E008-V14-' + arm + '-S20261023/initialization.json') for arm in ['G1', 'A1']]
    assert init[0]['head_tensor_sha256'] == init[1]['head_tensor_sha256']
    DEST.mkdir(parents=True, exist_ok=True)
    for name, content in data.items():
        path = DEST / name
        if path.exists():
            assert path.read_bytes() == content
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    zip_dest = DEST.parent / 'E008-V14-results-metadata.zip'
    if zip_dest.exists():
        assert sha(zip_dest.read_bytes()) == sha(SOURCE.read_bytes())
    else:
        shutil.copy2(SOURCE, zip_dest)
    common = {}
    g0 = [r['id'] for r in summaries if r['arm'] == 'G0']
    for target in TARGETS:
        common[target] = {kind: sorted(set.intersection(*(set(errors[r][target][kind]) for r in g0))) for kind in ['fp', 'fn']}
    save('results-audit-20261025.json', {
        'status': 'PASS_METADATA_AUDIT', 'checkpoint_bytes_verified_locally': False,
        'local_inference_performed': False, 'decision': 'Continue research; not Selected',
        'source_zip': {'path': zip_dest.relative_to(ROOT).as_posix(), 'sha256': sha(SOURCE.read_bytes()), 'bytes': SOURCE.stat().st_size},
        'import_root': DEST.relative_to(ROOT).as_posix(), 'inventory': inventory,
        'verified_artifact_checksums': checks, 'omitted_artifacts': missing,
        'checks': ['safe ZIP inventory', 'campaign/design/code/data/runtime pins', 'run/config/metrics SHA',
                   'same runtime across nine runs', 'train/val IDs, labels, masks, groups against V14',
                   'raw and calibrated confusion/AP/gates recomputed for train and val',
                   'exact calibration recomputed on val only', 'nine standalone reload metadata/prediction pairs',
                   'two smoke full/resume history and prediction pairs', 'G1/A1 shared head digest',
                   'champion ranking and exact approved five-run matrix'],
        'campaign_seconds': campaign['elapsed_seconds'], 'smoke_seconds': smoke['elapsed_seconds'],
        'runtime': read('runs/runtime.json'), 'screening_ranking': sorted(ranking),
        'runs': summaries, 'common_g0_errors_three_seeds': common})
    save('error-cohorts-20261025.json', {'operating_point': 'stored calibrated thresholds', 'runs': errors, 'common_g0_three_seeds': common})
    for row in summaries:
        print(row['id'], row['best_epoch'], row['completed_epochs'], row['macro_ap'], row['calibrated']['targets'])
    print('PASS', checks, 'artifact checksums;', len(missing), 'omitted artifacts; common errors:', common)


if __name__ == '__main__':
    main()

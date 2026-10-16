"""Compare verified cached scores on unchanged development membership."""
import json
from pathlib import Path

import torch

from ai_exam_monitoring.common.history import show
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import write_json
from ai_exam_monitoring.training.metrics import evaluate_scores

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def verified(run, name):
    assert sha256_file(run / name) == read(run / 'checksums.json')[name]
    return read(run / name)

def metrics(rows):
    scores = torch.tensor([r['scores'] for r in rows], dtype=torch.float64)
    values = torch.tensor([[v if v is not None else 0 for v in r['targets']] for r in rows], dtype=torch.float64)
    mask = torch.tensor([r['mask'] for r in rows], dtype=torch.bool)
    result = evaluate_scores(scores, values, mask, .5)
    loss = torch.nn.functional.binary_cross_entropy(scores, values, reduction='none')
    losses = [float(loss[:, i][mask[:, i]].mean()) for i in range(2) if mask[:, i].any()]
    result['macro_masked_bce'] = sum(losses) / 2 if len(losses) == 2 else None
    for target in result['targets'].values():
        target['fpr'] = target['fp'] / target['negative'] if target['negative'] else None
    return result

base = ROOT / 'outputs/E004-RC1-W-H'
candidate = ROOT / 'outputs/E004-C345-W-H'
reload_dir = ROOT / 'outputs/E004-C345-W-H-reload'
backup = read(HERE.parent / 'E004-RC1-execution-20261014/backup-receipt.json')
archived_checks = json.loads(show(ROOT / backup['archive'], 'outputs/E004-RC1-W-H/checksums.json',
                                 expected_sha256=backup['sha256']))
assert archived_checks == read(base / 'checksums.json'), 'Baseline checksum ledger differs from frozen archive'
assert verified(candidate, 'run.json')['status'] == 'FINISHED'
result = {'baseline': 'E004-RC1-W-H', 'candidate': 'E004-C345-W-H',
          'threshold': .5, 'M4_status': 'INCONCLUSIVE', 'test_inference': False,
          'cohorts': {}, 'family_selection': {}, 'changed_errors': []}
for cohort in ('selection', 'diagnostic49', 'comparator48', 'added35'):
    old = verified(base, f'predictions-{cohort}.json')
    new = verified(candidate, f'predictions-{cohort}.json')
    assert len(old) == len(new)
    for a, b in zip(old, new, strict=True):
        for key in ('sample_id', 'targets', 'mask', 'group_id', 'target_order'):
            assert a[key] == b[key], (cohort, key)
    reloaded = read(reload_dir / f'predictions-{cohort}.json')
    assert reloaded == new, f'Reload scores differ: {cohort}'
    result['cohorts'][cohort] = {'baseline': metrics(old), 'candidate': metrics(new), 'reload_parity': 'EXACT'}
    if cohort == 'selection':
        for group in sorted({r['group_id'] for r in old}):
            result['family_selection'][group] = {
                'baseline': metrics([r for r in old if r['group_id'] == group]),
                'candidate': metrics([r for r in new if r['group_id'] == group])}
        result['outside_CF-Q072'] = {
            'baseline': metrics([r for r in old if r['group_id'] != 'CF-Q072']),
            'candidate': metrics([r for r in new if r['group_id'] != 'CF-Q072'])}
        for a, b in zip(old, new, strict=True):
            for i, target in enumerate(a['target_order']):
                if a['mask'][i] and a['decisions'][i] != b['decisions'][i]:
                    result['changed_errors'].append({'sample_id': a['sample_id'], 'group': a['group_id'],
                        'target': target, 'truth': a['targets'][i], 'before': a['scores'][i],
                        'after': b['scores'][i], 'fixed': int(b['decisions'][i]) == a['targets'][i]})
result['run'] = verified(candidate, 'run.json')
result['train_metrics'] = verified(candidate, 'metrics.json')['train']
selection = verified(candidate, 'metrics.json')['selection']
targets = selection['targets']
result['development_gate_comparison'] = {
    'M1': all(t['precision'] is not None and t['precision'] >= .85 and t['recall'] >= .8
              and t['fpr'] <= .1 for t in targets.values()),
    'M2': all(t['ap'] is not None and t['ap'] >= .8 for t in targets.values())
          and selection['macro_ap'] >= .85,
    'M3': selection['macro_masked_bce'] <= .9 * selection['constant_train_prevalence']['macro_masked_bce'],
    'M3_ratio': selection['macro_masked_bce'] / selection['constant_train_prevalence']['macro_masked_bce'],
    'M4': 'INCONCLUSIVE', 'scope': 'Development diagnostic only; not final-test gate results'}
result['baseline_archive_sha256'] = backup['sha256']
result['limitations'] = ['One seed, selection reused; no independent generalization claim',
                         'New train data changes updates/epoch from 45 to 67',
                         'No promotion or final-test authorization']
write_json(HERE / 'comparison.json', result)
print(json.dumps(result['cohorts']['selection'], indent=2))

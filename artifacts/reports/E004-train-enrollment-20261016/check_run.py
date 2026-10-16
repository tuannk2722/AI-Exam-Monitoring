"""Verify completed run identity, epoch selection, sampler and reload parity."""
import json
import math
from pathlib import Path

import torch

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_model import tensor_digest
from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

run = ROOT / 'outputs/E004-C345-W-H'
reload_dir = ROOT / 'outputs/E004-C345-W-H-reload'
for folder in (run, ROOT / 'outputs/E004-C345-W-H-SMOKE', reload_dir):
    for name, checksum in read(folder / 'checksums.json').items():
        path = (folder / name).resolve()
        assert path.is_relative_to(folder.resolve())
        assert sha256_file(path) == checksum, path
record = read(run / 'run.json')
config = read(run / 'resolved-config.json')
assert record['status'] == 'FINISHED'
assert record['code_sha256'] == code_identity()['sha256']
assert record['config_sha256'] == digest_json(config)
assert record['elapsed_seconds'] <= config['wall_time_seconds']
history = read(run / 'history.json')
assert len(history) == record['completed_epochs']
best = min(history, key=lambda r: r['val_loss'])
assert record['best_epoch'] == best['epoch']
ids = next(c['sample_ids'] for c in config['cohorts'] if c['role'] == 'train')
generator = torch.Generator().manual_seed(config['seed'])
for row in history:
    permutation = torch.randperm(len(ids), generator=generator).tolist()
    assert row['permutation_sha256'] == digest_json([ids[i] for i in permutation])
last = torch.load(run / 'last.pt', map_location='cpu', weights_only=True)
checkpoint = torch.load(run / 'best.pt', map_location='cpu', weights_only=True)
assert last['global_step'] == len(history) * math.ceil(len(ids) / config['batch_size'])
assert checkpoint['model_tensor_sha256'] == tensor_digest(checkpoint['model'])
assert checkpoint['model_tensor_sha256'] == tensor_digest(last['best_model'])
assert checkpoint['epoch'] == best['epoch']
assert checkpoint['val_loss'] == best['val_loss']
assert read(run / 'initialization.json') == read(ROOT / 'outputs/E004-RC1-W-H/initialization.json')
metrics = read(run / 'metrics.json')
reloaded = read(reload_dir / 'metrics.json')
for name in reloaded:
    assert metrics[name] == reloaded[name], name
diagnostics = read(run / 'early-diagnostics.json')
assert [r['global_step'] for r in diagnostics] == [0, 15, 30]
assert diagnostics == read(ROOT / 'outputs/E004-C345-W-H-SMOKE/early-diagnostics.json')
write_json(HERE / 'run-integrity.json', {
    'status': 'PASS', 'code_sha256': record['code_sha256'],
    'completed_epochs': len(history), 'best_epoch': best['epoch'],
    'steps_per_epoch': math.ceil(len(ids) / config['batch_size']), 'global_steps': last['global_step'],
    'elapsed_seconds': record['elapsed_seconds'], 'wall_budget_seconds': config['wall_time_seconds'],
    'initialization_exact_baseline': True, 'sampler_recomputed': True,
    'checkpoint_tensors_and_best_epoch': 'PASS', 'smoke_early_diagnostics_parity': 'EXACT',
    'reload_metrics_parity': 'EXACT', 'all_artifact_checksums': 'PASS', 'test_inference': False})
print('Run integrity PASS', flush=True)

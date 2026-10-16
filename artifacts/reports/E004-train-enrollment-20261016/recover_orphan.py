"""Record an orphaned RUNNING process, preserve evidence, resume exact checkpoint."""
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import torch

from ai_exam_monitoring.training.adaptation_config import (
    config_from_dict,
    verify_adaptation_approval,
)
from ai_exam_monitoring.training.adaptation_train import runtime_signature
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    digest_json,
    environment,
    write_json,
)

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'outputs/E004-C345-W-H'
HERE = Path(__file__).resolve().parent
record = json.loads((RUN / 'run.json').read_text(encoding='utf8'))
assert record['status'] == 'RUNNING' and not record['resumed_at']
config = config_from_dict(json.loads((RUN / 'resolved-config.json').read_text(encoding='utf8')))
verify_adaptation_approval(config, ROOT)
torch.set_num_threads(config.threads)
assert record['code_sha256'] == code_identity()['sha256']
assert record['config_sha256'] == digest_json(config.to_dict())
assert runtime_signature(record['environment']) == runtime_signature(environment())
checkpoint = torch.load(RUN / 'last.pt', map_location='cpu', weights_only=True)
assert checkpoint['config'] == config.to_dict()
assert checkpoint['epoch'] == 8 and checkpoint['sampler_cursor'] == 1061
history = json.loads((RUN / 'history.json').read_text(encoding='utf8'))
assert checkpoint['history'] == history and checkpoint['global_step'] == 8 * 67
assert checkpoint['identity'] == digest_json({
    'config': config.to_dict(), 'code': record['code_sha256'],
    'runtime': runtime_signature(record['environment'])})
snapshot = ROOT / 'outputs/E004-C345-W-H-orphan-snapshot'
snapshot.mkdir(exist_ok=False)
for path in RUN.iterdir():
    if path.is_file():
        shutil.copy2(path, snapshot / path.name)
checksum_artifacts(snapshot)
now = datetime.now(UTC)
charged = (now - datetime.fromisoformat(record['started_at'])).total_seconds()
assert charged < config.wall_time_seconds
record.update(status='INTERRUPTED', ended_at=now.isoformat(),
              completed_epochs=checkpoint['epoch'], best_epoch=checkpoint['best_epoch'],
              elapsed_seconds=charged, error='Orphaned RUNNING process; no Python process exists',
              observation='Owner requested resume. Full wall interval including downtime charged conservatively; checkpoint bytes preserved.')
write_json(RUN / 'run.json', record)
checksum_artifacts(RUN)
write_json(HERE / 'orphan-recovery.json', {
    'status': 'validated_for_same_identity_resume', 'checkpoint_epoch': checkpoint['epoch'],
    'process_inventory': 'Get-CimInstance python.exe returned no processes before recovery',
    'cause': 'Unknown abrupt process termination; usage-limit causality not established',
    'snapshot': snapshot.relative_to(ROOT).as_posix(), 'charged_seconds': charged,
    'remaining_budget_seconds': config.wall_time_seconds - charged,
    'checkpoint_unchanged': True, 'config_unchanged': True,
    'checksum_note': 'Recovery checksum inventory newly created; not a pre-crash integrity claim. Checkpoint identity/config/history/sampler validated.'})
print('Recovery validated; resume epoch 9; remaining seconds', config.wall_time_seconds - charged)

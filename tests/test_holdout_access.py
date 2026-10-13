from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.training import holdout_access


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class HoldoutAccessTests(unittest.TestCase):
    def test_pending_failed_consumed_and_tampered_receipts_block_every_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for i, success in enumerate((None, False, True)):
                payload = str(i) * 64
                token = holdout_access.reserve(root, payload, {"model": "first"})
                if success is not None:
                    holdout_access.finish(root, payload, token, success=success, evidence={})
                expected = "reserved" if success is None else "consumed" if success else "failed"
                self.assertEqual(holdout_access.history(root, payload)[-1]["status"], expected)
                with self.assertRaises(DataContractError):
                    holdout_access.reserve(root, payload, {"model": "other", "output": "new"})
            path = root / "outputs/holdout-access" / ("0" * 64 + ".jsonl")
            row = json.loads(path.read_text())
            row["request"]["model"] = "tampered"
            path.write_text(json.dumps(row) + "\n")
            with self.assertRaises(DataContractError):
                holdout_access.history(root, "0" * 64)
            path.write_text("")  # crash during first write still fails closed
            with self.assertRaises(DataContractError):
                holdout_access.reserve(root, "0" * 64, {})
            with self.assertRaises(DataContractError):
                holdout_access.history(root, "0" * 64)

    def test_competing_processes_have_exactly_one_winner(self):
        code = (
            "from pathlib import Path\n"
            "import sys\n"
            "from ai_exam_monitoring.training.holdout_access import reserve\n"
            "from ai_exam_monitoring.common.errors import DataContractError\n"
            "try:\n"
            " reserve(Path(sys.argv[1]), 'a'*64, {'process':sys.argv[2]})\n"
            " print('won')\n"
            "except DataContractError:\n"
            " print('blocked')\n"
        )
        with tempfile.TemporaryDirectory() as directory:

            def attempt(index):
                return subprocess.run(
                    [sys.executable, "-c", code, directory, str(index)],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(attempt, range(4)))
            self.assertEqual(results.count("won"), 1)
            self.assertEqual(results.count("blocked"), 3)
            self.assertEqual(len(holdout_access.history(Path(directory), "a" * 64)), 1)


if __name__ == "__main__":
    unittest.main()

import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_repo import DOCUMENTS, REQUIRED, main


class RepositoryCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in REQUIRED:
            self.write(name, "")
        self.write("docs/00-INDEX.md", "\n".join(
            f"[{Path(name).stem}]({Path(name).name})" for name in sorted(DOCUMENTS)
        ))
        self.write("pyproject.toml", "")
        self.registry("history-20261010")
        self.write("artifacts/reports/pilot-b-v5-release-20261007/owner-approval.json",
                   json.dumps({key: {"path": path, "sha256": hashlib.sha256(b"").hexdigest()}
                               for key, path in {
                                   "membership": "artifacts/reports/pilot-b-v5-proposal-20261007/"
                                                 "membership-proposals.json",
                                   "groups": "artifacts/reports/pilot-b-v5-proposal-20261007/"
                                             "group-components.json",
                                   "proposal_config": "configs/datasets/"
                                                      "pilot_b_v5_release_proposal_20261007.yaml",
                               }.items()}))

    def registry(self, name: str) -> None:
        self.write("archive/index.json", json.dumps({"schema_version": 1, "bundles": [{
            "name": name, "path": f"archive/{name}.zip", "sha256": "a" * 64,
            "archive_bytes": 10,
        }]}))
        self.write(f"archive/{name}.zip.dvc",
                   f"outs:\n- path: {name}.zip\n  md5: {'b' * 32}\n  size: 10\n")

    def write(self, name: str, content: str = "fixture") -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def init_git(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("Git executable unavailable")
        self.git("init")
        self.git("add", ".")

    def check(self, *, strict: bool = False) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(self.root, require_git=strict)
        return result, output.getvalue()

    def test_ignored_and_untracked_local_files_are_not_tracked(self) -> None:
        self.init_git()
        self.write(".gitignore", ".venv/\ndata/\n*.pt\n.env\n")
        for name in [".venv/Lib/package.pth", "data/raw/photo.png", "weights.pt", ".env",
                     "untracked.mp4"]:
            self.write(name)
        self.git("add", ".gitignore")
        self.write("src/fixture.egg-info/SOURCES.txt", "generated packaging metadata")
        self.assertEqual(self.check(strict=True)[0], 0)

    def test_force_added_paths_are_rejected_even_if_deleted_on_disk(self) -> None:
        self.init_git()
        self.write(".gitignore", "*\n")
        names = ["weights.PT", "clip with spaces\nnewline.mp4", ".env", ".env.local",
                 ".dvc/config.local", "credentials.json", "private.pem",
                 ".venv/Lib/package.pth", "data/raw/manifest.csv", "model.onnx", "photo.png",
                 "archive/history-20261010.zip", "archive/check/docs/old.md"]
        for name in names:
            # Windows does not permit newline in filenames.
            if "\n" in name:
                name = name.replace("\n", " ")
            self.write(name)
            self.git("add", "-f", "--", name)
            (self.root / name).unlink()
            with self.subTest(name=name):
                code, output = self.check()
                self.assertEqual(code, 1)
                self.assertIn(name, output)

    def test_safe_templates_pointers_and_placeholders(self) -> None:
        self.init_git()
        for name in [".env.example", "data/raw.dvc", "data/raw/.gitkeep", ".dvc/config",
                     "data/raw/source.dvc", "data/interim/pilot/.gitignore",
                     "data/processed/pilot-b/pilot-b-20261005-v4.dvc",
                     "data/processed/pilot-b/.gitignore", "archive/.gitignore"]:
            self.write(name)
            self.git("add", "--", name)
        self.assertEqual(self.check()[0], 0)

    def test_strict_delivery_rejects_untracked_required_and_new_module(self) -> None:
        self.init_git()
        self.git("rm", "--cached", "docs/system.md")
        self.write("src/new_module.py", "")
        code, output = self.check(strict=True)
        self.assertEqual(code, 1)
        self.assertIn("not in Git index: docs/system.md", output)
        self.assertIn("not in Git index: src/new_module.py", output)

    def test_web_delivery_requires_original_metadata_in_git_index(self) -> None:
        self.init_git()
        config = "configs/web/LAPTOP-VIDEO-20261108"
        execution = {}
        for key, name in {
            "decision_ref": f"{config}/README.md",
            "parity": "outputs/verify-b0-01/parity/parity.json",
            "profile": "outputs/verify-b0-01/B1/profile.json",
            "profile_code": "outputs/verify-b0-01/B1/code.json",
        }.items():
            self.write(name, "original metadata")
            execution[key] = dict(path=name,
                                  sha256=hashlib.sha256(b"original metadata").hexdigest())
        self.write(f"{config}/execution.json", json.dumps(execution))
        self.write(f"{config}/inputs.json", "{}")
        self.write("RUN.ps1", "# synthetic launcher")
        self.assertEqual(self.check()[0], 0)
        self.assertEqual(self.check(strict=True)[0], 1)
        self.git("add", ".")
        self.assertEqual(self.check(strict=True)[0], 0)
        parity = execution["parity"]["path"]
        self.write(parity, "changed metadata")
        self.assertIn("web metadata bytes differ", self.check()[1])
        self.git("add", "--", parity)
        self.write(parity, "original metadata")
        self.assertIn("Git index web metadata bytes differ", self.check(strict=True)[1])

    def test_future_registered_archive_is_allowed_but_payload_is_not(self) -> None:
        self.registry("history-20261101")
        (self.root / "archive/history-20261010.zip.dvc").unlink()
        self.init_git()
        self.assertEqual(self.check(strict=True)[0], 0)
        self.write("archive/history-20261101.zip")
        self.git("add", "archive/history-20261101.zip")
        self.assertEqual(self.check(strict=True)[0], 1)

    def test_registry_rejects_wrong_pointer_and_unregistered_pointer(self) -> None:
        self.init_git()
        self.write("archive/other.zip.dvc")
        self.git("add", "archive/other.zip.dvc")
        self.assertEqual(self.check()[0], 1)
        self.write("archive/history-20261010.zip.dvc", "outs: []")
        self.assertIn("invalid archive registry", self.check()[1])

    def test_data_metadata_exception_keeps_payload_cache_and_secrets_blocked(self) -> None:
        self.init_git()
        for name in ["data/processed/pilot-b/crops/person.png",
                     "data/processed/pilot-b/manifest.jsonl", "data/raw/credentials.json",
                     ".dvc/cache/example.dvc", ".dvc/tmp/.gitignore",
                     ".venv/package.dvc", "artifacts/models/.gitignore"]:
            self.write(name)
            self.git("add", "-f", "--", name)
        code, output = self.check(strict=True)
        self.assertEqual(code, 1)
        for name in ["data/processed/pilot-b/crops/person.png",
                     "data/processed/pilot-b/manifest.jsonl", "data/raw/credentials.json",
                     ".dvc/cache/example.dvc", ".dvc/tmp/.gitignore",
                     ".venv/package.dvc", "artifacts/models/.gitignore"]:
            self.assertIn(name, output)

    def test_zip_is_explicitly_partial_and_strict_mode_fails(self) -> None:
        self.write(".venv/local.pth")
        code, output = self.check()
        self.assertEqual(code, 0)
        self.assertIn("NOT verified", output)
        self.assertEqual(self.check(strict=True)[0], 1)

    def test_staged_dependency_drift_is_rejected_even_when_local_bytes_restored(self) -> None:
        self.init_git()
        name = "configs/datasets/pilot_b_v5_release_proposal_20261007.yaml"
        self.write(name, "normalized or modified")
        self.git("add", name)
        self.write(name, "")
        code, output = self.check(strict=True)
        self.assertEqual(code, 1)
        self.assertIn("Git index bytes differ", output)

    def test_missing_required_file_and_incomplete_index(self) -> None:
        (self.root / "README.md").unlink()
        self.write("docs/00-INDEX.md", "01-only")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("missing required file: README.md", output)
        self.assertIn("does not reference docs/system.md", output)

    def test_index_rejects_missing_link_target(self) -> None:
        with (self.root / "docs/00-INDEX.md").open("a", encoding="utf-8") as handle:
            handle.write("\n[Missing](removed.md)\n")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("missing target: removed.md", output)

    def test_git_failure_does_not_fall_back_to_zip(self) -> None:
        (self.root / ".git").mkdir()
        for error in [FileNotFoundError(), subprocess.CalledProcessError(128, "git")]:
            with self.subTest(error=error), patch("scripts.check_repo.subprocess.run",
                                                 side_effect=error):
                self.assertEqual(self.check()[0], 1)

    def test_worktree_git_file_and_nul_delimited_paths(self) -> None:
        self.write(".git", "gitdir: elsewhere")
        result = subprocess.CompletedProcess([], 0, b"safe.txt\0video\nname.mp4\0")
        with patch("scripts.check_repo.subprocess.run", return_value=result):
            code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("video\nname.mp4", output)


if __name__ == "__main__":
    unittest.main()

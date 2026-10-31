"""Failure-path regression: a failed build must preserve the published PDF."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuildSafetyTest(unittest.TestCase):
    def test_failed_compiler_preserves_published_pdf(self):
        with tempfile.TemporaryDirectory(prefix="cv build test ") as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "build.sh", root / "build.sh")
            pdf = root / "cv_full_leschultz.pdf"
            pdf.write_bytes(b"previous successful PDF")
            tools = root / "tools"
            tools.mkdir()
            for name, exit_code in (("xelatex", 1), ("biber", 0)):
                executable = tools / name
                executable.write_text(f"#!/bin/sh\nexit {exit_code}\n")
                executable.chmod(0o755)
            env = dict(os.environ, PATH=f"{tools}{os.pathsep}{os.environ['PATH']}")
            result = subprocess.run(["bash", str(root / "build.sh")], cwd="/", env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(pdf.read_bytes(), b"previous successful PDF")
            self.assertIn("Diagnostics:", result.stderr)
            self.assertEqual(len(list((root / ".build").glob("run.*/build.log"))), 1)

    def test_unknown_option_is_rejected(self):
        result = subprocess.run(["bash", str(ROOT / "build.sh"), "--invalid"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()

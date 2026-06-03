import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def run_demo(script):
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / script), "--demo"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return result.returncode, result.stdout

class TestDemos(unittest.TestCase):
    def test_capo_normal(self):
        code, out = run_demo("tools/capo-parameter-checker.py")
        self.assertEqual(code, 0, f"exit={code}\n{out}")
        self.assertIn("NORMAL", out)

    def test_dvn_critical(self):
        code, out = run_demo("tools/dvn-config-checker.py")
        self.assertEqual(code, 0, f"exit={code}\n{out}")
        self.assertIn("CRITICAL", out)

    def test_vectors_access_control(self):
        code, out = run_demo("tools/analyze-vectors.py")
        self.assertEqual(code, 0, f"exit={code}\n{out}")
        self.assertIn("ACCESS_CONTROL", out)

if __name__ == "__main__":
    unittest.main()

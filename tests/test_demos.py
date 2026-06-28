import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_cross_layer_module():
    """Load cross-layer-agreement-checker.py by file path (hyphen in name prevents normal import)."""
    spec = importlib.util.spec_from_file_location(
        "cross_layer_agreement_checker",
        str(REPO_ROOT / "tools" / "cross-layer-agreement-checker.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_demo(script):
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / script), "--demo"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return result.returncode, result.stdout

class TestDemos(unittest.TestCase):
    def test_dvn_critical(self):
        code, out = run_demo("tools/dvn-config-checker.py")
        self.assertEqual(code, 0, f"exit={code}\n{out}")
        self.assertIn("CRITICAL", out)

    def test_vectors_access_control(self):
        code, out = run_demo("tools/analyze-vectors.py")
        self.assertEqual(code, 0, f"exit={code}\n{out}")
        self.assertIn("ACCESS_CONTROL", out)

    def test_cross_layer_reject(self):
        code, out = run_demo("tools/cross-layer-agreement-checker.py")
        self.assertEqual(code, 0, f"exit={code}\n{out}")
        self.assertIn("REJECT", out)


class TestCheckAgreementDirect(unittest.TestCase):
    """Unit tests for check_agreement() — one assertion per reason code."""

    def setUp(self):
        self.mod = _load_cross_layer_module()

    def test_vacuous_proof(self):
        """identity_count == 0 must produce vacuous_proof, never multiple_identities."""
        verdict, reason = self.mod.check_agreement("asset_alpha", "asset_alpha", 0)
        self.assertEqual(verdict, "REJECT — fail closed required")
        self.assertEqual(reason, "vacuous_proof")

    def test_multiple_identities(self):
        """identity_count > 1 must produce multiple_identities."""
        verdict, reason = self.mod.check_agreement("asset_alpha", "asset_alpha", 2)
        self.assertEqual(verdict, "REJECT — fail closed required")
        self.assertEqual(reason, "multiple_identities")

    def test_layer_disagreement(self):
        """identity_count == 1 but differing resolutions must produce layer_disagreement."""
        verdict, reason = self.mod.check_agreement("asset_alpha", "asset_beta", 1)
        self.assertEqual(verdict, "REJECT — fail closed required")
        self.assertEqual(reason, "layer_disagreement")

    def test_pass(self):
        """Unanimous single-identity resolution must PASS with no reason."""
        verdict, reason = self.mod.check_agreement("asset_alpha", "asset_alpha", 1)
        self.assertEqual(verdict, "PASS")
        self.assertIsNone(reason)


if __name__ == "__main__":
    unittest.main()

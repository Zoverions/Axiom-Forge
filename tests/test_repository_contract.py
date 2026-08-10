import importlib.util
import os
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_zwa_module():
    path = ROOT / "zwa_lite.py"
    spec = importlib.util.spec_from_file_location("zwa_lite_contract_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RepositoryBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zwa = load_zwa_module()

    def test_import_does_not_load_model_stack(self):
        self.assertNotIn("torch", sys.modules)
        self.assertNotIn("transformers", sys.modules)

    def test_unsafe_executor_denies_default(self):
        code = "def execute():\n    return 'ok'\n"
        with self.assertRaises(PermissionError):
            self.zwa._unsafe_execute_generated_code(code)

    def test_unsafe_executor_requires_exact_environment_acknowledgment(self):
        code = "def execute():\n    return 'ok'\n"
        with patch.dict(os.environ, {self.zwa.UNSAFE_ACK_ENV: "wrong"}, clear=False):
            with self.assertRaises(PermissionError):
                self.zwa._unsafe_execute_generated_code(code, allow_unsafe=True)

    def test_explicit_double_opt_in_can_execute_benign_research_code(self):
        code = "def execute():\n    return 'ok'\n"
        with patch.dict(
            os.environ,
            {self.zwa.UNSAFE_ACK_ENV: self.zwa.UNSAFE_ACK_VALUE},
            clear=False,
        ):
            result = self.zwa._unsafe_execute_generated_code(code, allow_unsafe=True)
        self.assertEqual(result, "ok")

    def test_stored_skill_is_proposal_only_by_default(self):
        constellation = {
            "example": {
                "desc": "calculate example value",
                "code": "def execute():\n    return 'should not run'\n",
            }
        }
        result = self.zwa.run("calculate example value", constellation=constellation)
        self.assertIn("NOT EXECUTED", result)
        self.assertIn("def execute", result)

    def test_security_docs_do_not_claim_a_sandbox(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        self.assertIn("not a sandbox", readme.lower())
        self.assertIn("not a secure python sandbox", security.lower())
        self.assertNotIn("MIT License", readme)


if __name__ == "__main__":
    unittest.main()

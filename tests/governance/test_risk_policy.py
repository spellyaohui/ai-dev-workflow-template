import unittest

from scripts.governance.risk_policy import effective_risk


class RiskPolicyTests(unittest.TestCase):
    def test_low_stays_low_without_high_signal(self):
        result = effective_risk("LOW", "LOW", "LOW", ["src/ui.py"])
        self.assertEqual(result.level, "LOW")

    def test_governance_path_forces_high(self):
        result = effective_risk("LOW", "LOW", "LOW", [".github/workflows/x.yml"])
        self.assertEqual(result.level, "HIGH")

    def test_unknown_forces_high(self):
        result = effective_risk("LOW", "LOW", None, ["src/app.py"])
        self.assertEqual(result.level, "HIGH")

    def test_any_high_signal_forces_high(self):
        result = effective_risk("LOW", "HIGH", "LOW", ["src/app.py"])
        self.assertEqual(result.level, "HIGH")

    def test_configured_high_risk_category_forces_high(self):
        result = effective_risk(
            "LOW", "LOW", "LOW", ["src/app.py"], categories=["auth"]
        )
        self.assertEqual(result.level, "HIGH")


if __name__ == "__main__":
    unittest.main()

import unittest

import pandas as pd

from dcf_model import (
    CompanyFinancialSnapshot,
    DCFInputs,
    build_sensitivity_heatmap,
    calculate_cagr,
    create_pitch_pdf_bytes,
    run_dcf,
)


class DCFModelTests(unittest.TestCase):
    def setUp(self):
        index = pd.to_datetime(
            ["2021-12-31", "2022-12-31", "2023-12-31", "2024-12-31"]
        )
        self.snapshot = CompanyFinancialSnapshot(
            ticker="TEST",
            company_name="Test Corp",
            currency="USD",
            current_price=42.0,
            shares_outstanding=100.0,
            net_debt=250.0,
            revenue_history=pd.Series([1000.0, 1120.0, 1232.0, 1355.2], index=index),
            net_income_history=pd.Series([90.0, 96.0, 107.0, 120.0], index=index),
            free_cash_flow_history=pd.Series([110.0, 123.0, 135.0, 149.0], index=index),
        )

    def test_calculate_cagr_uses_series_growth(self):
        cagr = calculate_cagr(self.snapshot.revenue_history)
        self.assertAlmostEqual(cagr, 0.1066266659, places=6)

    def test_run_dcf_builds_projection_and_intrinsic_value(self):
        result = run_dcf(
            self.snapshot,
            DCFInputs(
                revenue_growth_rate=0.08,
                wacc=0.10,
                terminal_growth_rate=0.03,
                projection_years=5,
            ),
        )
        self.assertEqual(len(result.projection_table), 5)
        self.assertGreater(result.enterprise_value, 0.0)
        self.assertGreater(result.intrinsic_value_per_share, 0.0)
        self.assertIn("FY2025", set(result.projection_table["label"]))

    def test_sensitivity_heatmap_moves_in_expected_direction(self):
        base_inputs = DCFInputs(
            revenue_growth_rate=0.08,
            wacc=0.10,
            terminal_growth_rate=0.03,
            projection_years=5,
        )
        heatmap = build_sensitivity_heatmap(
            self.snapshot,
            base_inputs,
            wacc_values=[0.08, 0.10, 0.12],
            terminal_growth_values=[0.02, 0.03, 0.04],
        )
        self.assertGreater(heatmap.loc[0.08, 0.03], heatmap.loc[0.12, 0.03])
        self.assertGreater(heatmap.loc[0.10, 0.04], heatmap.loc[0.10, 0.02])

    def test_pdf_export_returns_pdf_bytes(self):
        inputs = DCFInputs(
            revenue_growth_rate=0.08,
            wacc=0.10,
            terminal_growth_rate=0.03,
            projection_years=5,
        )
        result = run_dcf(self.snapshot, inputs)
        heatmap = build_sensitivity_heatmap(
            self.snapshot,
            inputs,
            wacc_values=[0.08, 0.10, 0.12],
            terminal_growth_values=[0.02, 0.03, 0.04],
        )
        pdf_bytes = create_pitch_pdf_bytes(self.snapshot, result, heatmap)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 1000)


if __name__ == "__main__":
    unittest.main()

import unittest

import generate_pitches as gp


class MetricsTests(unittest.TestCase):
    def test_normalize_tickers_dedupes_and_upcases(self):
        tickers = gp.normalize_tickers("medp, PLTR,medp , dds")
        self.assertEqual(tickers, ["MEDP", "PLTR", "DDS"])

    def test_normalize_tickers_rejects_invalid(self):
        with self.assertRaises(ValueError):
            gp.normalize_tickers("AAPL,PLTR")

    def test_target_move_pct_handles_long_and_short(self):
        short_move = gp.target_move_pct(gp.PITCH_PROFILES["PLTR"])
        long_move = gp.target_move_pct(gp.PITCH_PROFILES["MEDP"])
        self.assertGreater(short_move, 0.0)
        self.assertGreater(long_move, 0.0)

    def test_portfolio_metrics_rank_by_conviction(self):
        metrics = gp.build_portfolio_metrics(["PLTR", "MEDP", "DDS"])
        self.assertEqual(metrics[0]["ticker"], "PLTR")
        self.assertEqual([m["rank"] for m in metrics], [1.0, 2.0, 3.0])
        self.assertGreater(metrics[0]["conviction_score"], metrics[-1]["conviction_score"])

    def test_suggested_weights_sum_to_100(self):
        metrics = gp.build_portfolio_metrics(["PLTR", "MEDP", "DDS"])
        weighted = gp.suggested_weights(metrics)
        total_weight = sum(metric["suggested_weight_pct"] for metric in weighted)
        self.assertAlmostEqual(total_weight, 100.0, places=6)
        short_row = next(metric for metric in weighted if metric["recommendation"] == "SHORT")
        self.assertEqual(short_row["stop_rule"], "Cover +12% above entry")

    def test_cover_stamp_text_uses_runtime_profile(self):
        original_profile = gp.RENDER_PROFILE
        gp.RENDER_PROFILE = gp.RenderProfile(
            deck_date="May 2026",
            audience_label="For IC Review Only",
            desk_name="Blue River Capital",
            analyst_name="Jane Doe",
        )
        stamp = gp.cover_stamp_text()
        self.assertIn("Blue River Capital", stamp)
        self.assertIn("May 2026", stamp)
        self.assertIn("For IC Review Only", stamp)
        gp.RENDER_PROFILE = original_profile


if __name__ == "__main__":
    unittest.main()

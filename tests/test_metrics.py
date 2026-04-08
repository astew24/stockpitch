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


if __name__ == "__main__":
    unittest.main()

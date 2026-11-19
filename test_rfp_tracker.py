import csv
from datetime import date
from pathlib import Path
import tempfile
import unittest
from rfp_tracker import connect, import_csv, summarize, validate


class TrackerTests(unittest.TestCase):
    def test_import_is_idempotent(self):
        with connect(":memory:") as conn:
            path = Path(__file__).resolve().parents[1] / "data/sample_rfps.csv"
            import_csv(conn, path)
            import_csv(conn, path)
            report = summarize(conn, date(2026, 11, 19))
            self.assertEqual(report["total_rfps"], 10)
            self.assertEqual(report["deadlines_next_7_days"], 4)
            self.assertEqual(report["closed_win_rate_pct"], 50.0)

    def test_rejects_negative_value(self):
        bad = dict(rfp_id="X", organization="Fake", stage="new", estimated_value="-5",
                   received_date="2026-01-01", due_date="2026-01-03")
        with self.assertRaises(ValueError):
            validate(bad)

    def test_rejects_backdated_deadline(self):
        bad = dict(rfp_id="X", organization="Fake", stage="new", estimated_value="5",
                   received_date="2026-01-09", due_date="2026-01-03")
        with self.assertRaises(ValueError):
            validate(bad)


if __name__ == "__main__":
    unittest.main()

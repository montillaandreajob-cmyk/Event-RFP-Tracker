"""Privacy-safe demonstration of RFP tracking and reporting."""
import argparse
import csv
import sqlite3
from datetime import date, timedelta
from pathlib import Path

STAGES = {"new", "qualified", "proposal", "won", "lost"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS rfps (
    rfp_id TEXT PRIMARY KEY,
    organization TEXT NOT NULL,
    stage TEXT NOT NULL CHECK (stage IN ('new', 'qualified', 'proposal', 'won', 'lost')),
    estimated_value REAL NOT NULL CHECK (estimated_value >= 0),
    received_date TEXT NOT NULL,
    due_date TEXT NOT NULL
);
"""


def validate(row):
    required = {"rfp_id", "organization", "stage", "estimated_value", "received_date", "due_date"}
    if not required.issubset(row) or any(not str(row[key]).strip() for key in required):
        raise ValueError("One or more required fields are missing")
    stage = row["stage"].strip().lower()
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    received = date.fromisoformat(row["received_date"])
    due = date.fromisoformat(row["due_date"])
    if due < received:
        raise ValueError("Due date must not precede received date")
    amount = float(row["estimated_value"])
    if amount < 0:
        raise ValueError("Estimated value must not be negative")
    return (
        row["rfp_id"].strip(), row["organization"].strip(), stage,
        amount, received.isoformat(), due.isoformat()
    )


def connect(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def import_csv(conn, path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [validate(row) for row in reader]
    with conn:
        conn.executemany("""
            INSERT INTO rfps VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(rfp_id) DO UPDATE SET
                organization=excluded.organization, stage=excluded.stage,
                estimated_value=excluded.estimated_value,
                received_date=excluded.received_date, due_date=excluded.due_date
        """, rows)
    return len(rows)


def summarize(conn, as_of):
    by_stage = dict(conn.execute("SELECT stage, COUNT(*) FROM rfps GROUP BY stage"))
    pipeline = conn.execute("""
        SELECT COALESCE(SUM(estimated_value), 0) FROM rfps
        WHERE stage IN ('new', 'qualified', 'proposal')
    """).fetchone()[0]
    upcoming = conn.execute("""
        SELECT COUNT(*) FROM rfps
        WHERE stage IN ('new', 'qualified', 'proposal') AND due_date BETWEEN ? AND ?
    """, (as_of.isoformat(), (as_of + timedelta(days=7)).isoformat())).fetchone()[0]
    won = conn.execute("SELECT COUNT(*) FROM rfps WHERE stage = 'won'").fetchone()[0]
    lost = conn.execute("SELECT COUNT(*) FROM rfps WHERE stage = 'lost'").fetchone()[0]
    return {
        "total_rfps": sum(by_stage.values()), "by_stage": by_stage,
        "active_pipeline_value": round(pipeline, 2), "deadlines_next_7_days": upcoming,
        "closed_win_rate_pct": round(100 * won / (won + lost), 1) if won + lost else 0.0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="data/sample_rfps.csv")
    parser.add_argument("--db", default=":memory:")
    parser.add_argument("--as-of", default="2026-11-19")
    args = parser.parse_args()
    with connect(args.db) as conn:
        count = import_csv(conn, args.csv)
        report = summarize(conn, date.fromisoformat(args.as_of))
    print(f"Imported or updated {count} sample records")
    for key, value in report.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

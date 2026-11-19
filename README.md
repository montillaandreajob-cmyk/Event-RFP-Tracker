# Event RFP Tracker | Python + SQLite

A runnable case study of a fictional events sales pipeline: import proposals from CSV, validate records, store them in SQLite, and report opportunity volume, pipeline value and upcoming deadlines.

## Context
Inspired by the type of RFP coordination and proposal reporting I worked with in the convention and events industry. **This is a new portfolio reconstruction, not software developed for or deployed by an employer.** Every company and amount in the example CSV is fictional.

## Features
- CSV import with validation and repeatable upsert by RFP ID
- SQLite data model and parameterized queries
- Summary by stage, active pipeline value and due-soon count
- Adjustable `--as-of` reporting date for reproducibility
- Automated tests using Python's standard library

## Quick start
```bash
python rfp_tracker.py --csv data/sample_rfps.csv --db demo.sqlite3 --as-of 2026-11-19
python -m unittest discover -s tests -v
```

Python 3.10+; no external packages. Running the app writes `demo.sqlite3` locally. This database is intentionally excluded from version control.

## What I would highlight to recruiters
Data validation, structured storage, repeatable imports, deadline tracking, and commercial pipeline reporting.

## Transparency
Developed as a public demonstration with AI assistance, inspired by prior professional responsibilities. Do not infer these files represent an employer's internal systems.

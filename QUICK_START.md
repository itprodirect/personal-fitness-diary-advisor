# Quick Start Guide

## TL;DR - What to Do in Claude Code Right Now

### Step 1: Data Discovery (5 min)
Copy this into Claude Code:

```
I have a Fitbit data export from Google Takeout in the "Fitbit" folder. 
Explore it and give me a data discovery report:
1. Folder structure (all subdirectories)
2. File types and counts
3. Sample file content for: heart rate, steps, sleep
4. Date range of the data

This will help us design the ETL correctly.
```

### Step 2: Build Everything (30-45 min)
After reviewing discovery results, copy this single prompt:

```
Build a complete MVP for personal-fitness-diary-advisor.

CONTEXT:
- Fitbit data export is in the "Fitbit" folder
- Stack: Python, Pandas, DuckDB, Streamlit, Parquet
- Priority metrics: steps, heart rate (resting HR trends), sleep (duration + stages)
- Must be extensible for future data sources (nutrition, stretching, medical)

DELIVERABLES:
1. Project structure with etl/, analytics/, ui/, tests/, data/ folders
2. ETL pipeline (etl/pipeline.py) that:
   - Reads Fitbit JSON/CSV files
   - Creates Parquet files: daily_summary.parquet, heart_rate.parquet, sleep.parquet
   - Logs errors to logs/etl.log
3. Streamlit dashboard (app.py) with:
   - Date range selector
   - Steps chart with 7-day rolling average
   - Resting HR trend line
   - Sleep duration/stages visualization
   - Uses DuckDB to query Parquet files
4. Sample test data in data/sample/fitbit/
5. pytest tests for ETL
6. requirements.txt
7. README.md with setup instructions
8. .gitignore (exclude raw data, processed data, logs)

CONSTRAINTS:
- All local, no cloud services
- Handle missing data gracefully
- Make UI look professional (not default Streamlit)
- Code should be production-quality with error handling

After building, run the ETL and start Streamlit to verify it works.
```

### Step 3: Git Push
```
Initialize git, commit with message "feat: Sprint 1 MVP", and show me commands to push to GitHub.
Make sure no raw health data is committed!
```

---

## Expected Output Files

After Sprint 1, you should have:

```
personal-fitness-diary-advisor/
├── app.py                    ✅ Streamlit entry
├── config.toml               ✅ Configuration
├── requirements.txt          ✅ Dependencies
├── README.md                 ✅ Documentation
├── .gitignore               ✅ Excludes data
├── etl/
│   ├── pipeline.py          ✅ Main ETL
│   └── loaders/fitbit.py    ✅ Fitbit parsing
├── analytics/queries.py      ✅ DuckDB queries
├── ui/pages/dashboard.py     ✅ Dashboard page
├── tests/test_etl.py        ✅ Tests
├── data/
│   ├── processed/*.parquet  ✅ Generated data
│   └── sample/fitbit/       ✅ Test data
└── logs/etl.log             ✅ ETL log
```

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Fitbit folder not found" | Make sure you're in the right directory: `cd personal-fitness-diary-advisor` |
| JSON parsing errors | Ask Claude Code to show the problematic file and adjust the parser |
| Missing sleep stages | Your Fitbit might only have "classic" sleep data (no stages) - parser should handle this |
| Streamlit port in use | Run `streamlit run app.py --server.port 8502` |
| Tests fail on real data | Tests should use sample data only; check conftest.py fixtures |

---

## After MVP Works

1. Take a screenshot of your working dashboard
2. `git push origin main`
3. Add the screenshot to README.md
4. Start Sprint 2: Zone minutes, activity log, weekly views

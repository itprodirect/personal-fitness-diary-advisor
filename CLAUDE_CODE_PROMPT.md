# Claude Code Prompt - Personal Fitness Diary Advisor

Copy and paste these prompts into Claude Code in sequence.

---

## PROMPT 1: Data Discovery (Run This First!)

```
I have a Fitbit data export from Google Takeout in the "Fitbit" folder. Before we build anything, I need to understand the data structure.

Please:
1. Recursively explore the Fitbit folder and list all subdirectories
2. Identify all unique file types (extensions) and count how many of each
3. For each major folder, show me 2-3 sample filenames
4. Read and display the structure of ONE sample file for each of these types (if they exist):
   - A heart rate JSON file
   - A steps JSON or CSV file  
   - A sleep JSON file
   - Any CSV file with daily summaries
5. Identify the date range of the data (earliest and latest dates you can find)

Present this as a data discovery report so we can design the ETL correctly.
```

**After running this**, review the output and note any surprises before moving to Prompt 2.

---

## PROMPT 2: Project Initialization

```
Let's initialize the project structure for personal-fitness-diary-advisor.

Create this folder structure:
- etl/
  - __init__.py
  - pipeline.py (placeholder)
  - loaders/
    - __init__.py
    - base.py (abstract base class)
    - fitbit.py (placeholder)
  - utils.py (placeholder)
- analytics/
  - __init__.py
  - queries.py (placeholder)
- ui/
  - __init__.py
  - components.py (placeholder)
  - pages/
    - __init__.py
    - dashboard.py (placeholder)
- tests/
  - __init__.py
  - conftest.py
  - test_etl.py (placeholder)
- data/
  - raw/ (with .gitkeep)
  - processed/ (with .gitkeep)
  - sample/
    - fitbit/ (with .gitkeep)
- logs/ (with .gitkeep)
- notebooks/

Also create:
- requirements.txt with: pandas, pyarrow, duckdb, streamlit, pytest, python-dotenv, tomli
- config.toml with sensible defaults for paths and settings
- .gitignore that excludes: data/raw/*, data/processed/*, logs/*.log, __pycache__, .env, *.pyc, .DS_Store
- README.md with project title and "Setup instructions coming soon"

Use /init if helpful. After creating the structure, show me a tree view of what was created.
```

---

## PROMPT 3: Build the ETL Foundation

```
Now let's build the ETL system. Based on the data discovery, create:

1. etl/loaders/base.py - Abstract base class for all data loaders:
   - Abstract method: load(source_path: Path) -> pd.DataFrame
   - Abstract method: get_metric_name() -> str
   - Helper method: discover_files(path, patterns) -> list[Path]

2. etl/utils.py with helper functions:
   - find_files_recursive(root: Path, extensions: list[str]) -> list[Path]
   - parse_fitbit_date(date_str: str) -> datetime
   - safe_read_json(path: Path) -> dict | list | None (with error handling)
   - setup_logging(log_path: Path) -> Logger

3. etl/loaders/fitbit.py with these loader classes (each inherits from BaseLoader):

   a) FitbitStepsLoader:
      - Reads steps JSON files (intraday) or steps CSV (daily totals)
      - Output columns: timestamp, steps, data_source='fitbit'
      - For daily summary: date, steps_total

   b) FitbitHeartRateLoader:
      - Reads heart_rate JSON files
      - Output columns: timestamp, bpm, confidence (if available), data_source='fitbit'
      - Extract resting HR if available in the data

   c) FitbitSleepLoader:
      - Reads sleep JSON files
      - Output columns: date, start_time, end_time, total_minutes, 
        deep_min, rem_min, light_min, awake_min, sleep_score (nullable), data_source='fitbit'
      - Handle both "classic" and "stages" sleep data formats

   d) FitbitActivityLoader:
      - Reads exercise/activity JSON files
      - Output columns: date, activity_type, start_time, duration_min, 
        calories, avg_hr (nullable), distance_km (nullable), data_source='fitbit'

4. etl/pipeline.py - Main orchestrator:
   - CLI interface with argparse: --source (input dir), --output (output dir), --metrics (optional filter)
   - Instantiates each loader, runs them, writes Parquet files
   - Creates daily_summary.parquet by aggregating:
     - steps_total from steps
     - resting_hr from heart_rate
     - sleep metrics from sleep
     - zone minutes if available
   - Logs progress and errors to logs/etl.log

Handle edge cases:
- Missing files for certain date ranges
- Malformed JSON (log and skip)
- Different Fitbit export formats (try multiple parsing strategies)
- Timezone handling: assume UTC if not specified, preserve original when possible

Make the code robust with try/except blocks and informative error messages.
After creating the files, run `python -m etl.pipeline --source Fitbit --output data/processed` and show me the results.
```

---

## PROMPT 4: Create Sample Test Data

```
Create synthetic sample data for testing in data/sample/fitbit/:

1. Create 5 days of sample heart rate JSON files (heart_rate-2024-01-01.json through heart_rate-2024-01-05.json):
   - Format should match actual Fitbit export structure
   - Include realistic HR values (60-150 bpm range)
   - Include timestamps at 1-minute intervals for a few hours

2. Create 5 days of sample steps JSON files:
   - Match Fitbit export structure
   - Include realistic step counts (0-500 per interval)

3. Create 5 days of sample sleep JSON files:
   - Include sleep stages (deep, light, rem, wake)
   - Include start/end times
   - Realistic durations (6-8 hours)

4. Create a sample daily summary CSV if that format exists in my real data

Then run the ETL on the sample data to verify it works:
python -m etl.pipeline --source data/sample/fitbit --output data/processed

Show me the output and confirm the Parquet files were created correctly.
```

---

## PROMPT 5: Build the Streamlit Dashboard

```
Now let's build the Streamlit app. Create:

1. ui/styles.py:
   - Custom CSS for a clean, modern dark theme
   - Card-style containers for metrics
   - Consistent typography

2. ui/components.py:
   - data_status_card(): Shows which Parquet files exist and their date ranges
   - metric_card(title, value, delta, icon): KPI display card
   - date_range_selector(): Returns start_date, end_date
   - chart_container(title): Styled container for charts

3. analytics/queries.py:
   - get_daily_summary(start_date, end_date) -> DataFrame
   - get_steps_with_rolling_avg(start_date, end_date, window=7) -> DataFrame
   - get_heart_rate_daily(start_date, end_date) -> DataFrame (daily avg/min/max/resting)
   - get_sleep_summary(start_date, end_date) -> DataFrame
   - Use DuckDB to query the Parquet files directly

4. ui/pages/dashboard.py:
   - Main dashboard with:
     - Header with title and date range selector
     - Row of KPI cards: avg steps, avg sleep, avg resting HR, total active days
     - Steps chart: daily bars + 7-day rolling average line (use plotly or altair)
     - Resting HR trend: line chart with reference bands (healthy range)
     - Sleep chart: stacked bars showing deep/rem/light/awake per night
   - Use st.cache_data for query results
   - Handle missing data gracefully (show "No data" message)

5. app.py:
   - Streamlit entry point
   - Page config (title, icon, layout)
   - Sidebar navigation (for future pages)
   - Load and display dashboard page
   - Error boundary for missing data

Use Plotly for charts (better interactivity than matplotlib).
Make it look professional - not the default Streamlit look.

After creating everything, run `streamlit run app.py` and show me any errors to fix.
```

---

## PROMPT 6: Add Tests

```
Create comprehensive tests in tests/:

1. tests/conftest.py:
   - Fixture: sample_data_path pointing to data/sample/fitbit
   - Fixture: temp_output_dir using pytest tmp_path
   - Fixture: sample_heart_rate_df with known test data
   - Fixture: sample_sleep_df with known test data

2. tests/test_etl.py:
   - test_find_files_recursive(): Verify file discovery
   - test_fitbit_steps_loader(): Load sample steps, verify columns and types
   - test_fitbit_heart_rate_loader(): Load sample HR, verify data
   - test_fitbit_sleep_loader(): Load sample sleep, verify stages
   - test_pipeline_creates_parquet(): Run full pipeline, verify output files exist
   - test_pipeline_handles_missing_files(): Verify graceful handling

3. tests/test_queries.py:
   - test_get_daily_summary_returns_dataframe()
   - test_date_filtering_works()
   - test_rolling_average_calculation()

Run pytest -v and fix any failing tests.
```

---

## PROMPT 7: Documentation & Git

```
Finalize the project for GitHub:

1. Update README.md with:
   - Project description and features
   - Screenshots placeholder
   - Prerequisites (Python 3.11+, etc.)
   - Installation steps (git clone, pip install, etc.)
   - How to add your Fitbit data
   - How to run the ETL
   - How to start the dashboard
   - Project structure overview
   - Sprint 2 roadmap
   - Contributing section
   - License (MIT)

2. Create CHANGELOG.md:
   - v0.1.0 - Sprint 1 MVP

3. Verify .gitignore is correct

4. Initialize git repo if not already:
   git init
   git add .
   git commit -m "feat: Sprint 1 MVP - Fitbit data ETL and dashboard"

5. Show me the git status and confirm what will be committed (make sure no raw data is included!)
```

---

## PROMPT 8: Final Verification

```
Let's do a final end-to-end test:

1. Delete data/processed/* to start fresh
2. Run the ETL on the sample data: python -m etl.pipeline --source data/sample/fitbit --output data/processed
3. Verify Parquet files exist and show their schemas
4. Run the Streamlit app: streamlit run app.py
5. Run all tests: pytest -v
6. Show me any errors or warnings

If everything works, create the GitHub remote:
- Instructions for `git remote add origin` and `git push`
```

---

## Troubleshooting Prompts

### If ETL fails on your real data:
```
The ETL failed with this error: [paste error]

Please examine the problematic file and update the loader to handle this format.
Show me the file structure and your fix.
```

### If a specific Fitbit format is different:
```
My Fitbit export has a different format for [heart_rate/sleep/steps].
Here's what the file looks like: [paste sample]

Please update the FitbitXxxLoader to handle this format.
```

### If charts don't display:
```
The [steps/HR/sleep] chart isn't showing data. 
Query the Parquet file directly with DuckDB and show me what data is available.
Then fix the chart code.
```

---

## Sprint 2 Features (After MVP Works)

Once Sprint 1 is working and pushed to GitHub, start Sprint 2:

```
Let's start Sprint 2. Add these features:

1. Zone minutes visualization (fat burn / cardio / peak stacked area chart)
2. Activity log page with filtering and sorting
3. Weekly summary view (aggregated by week instead of day)
4. CSV export button for any data view
5. Improved error handling with user-friendly messages
6. Settings page to configure timezone and date format

Start with zone minutes since that builds on existing infrastructure.
```

---

## Notes

- Always review Claude Code's output before running commands that modify files
- If Claude Code suggests installing packages, verify they're in requirements.txt
- Keep your real Fitbit data in data/raw/fitbit/ and ensure it's gitignored
- The sample data in data/sample/ should be committed for testing
- Back up your Fitbit export before making any changes to the folder

# Personal Fitness Diary Advisor

A comprehensive dashboard for analyzing and visualizing Fitbit health data. Built with Python, DuckDB, and Streamlit.

## Features

- **Steps Analysis**: Daily step counts, goal tracking, day-of-week patterns
- **Heart Rate Analysis**: Resting heart rate trends, hourly patterns, distribution analysis
- **Sleep Analysis**: Duration trends, sleep stages breakdown, efficiency metrics
- **Zone Minutes**: Active zone minutes visualization (Fat Burn, Cardio, Peak)
- **Activity Log**: Exercise history with filtering, sorting, and detailed breakdowns
- **Data Export**: CSV download on all pages
- **Flexible Aggregation**: Daily, weekly, and monthly views

## Project Structure

```
personal-fitness-diary-advisor/
├── scripts/
│   └── run_pipeline.py       # ETL pipeline runner
├── src/
│   ├── config/
│   │   └── settings.py       # Configuration and paths
│   ├── dashboard/
│   │   ├── app.py            # Main Streamlit application
│   │   ├── utils.py          # Shared utilities (CSV export)
│   │   └── pages/
│   │       ├── overview.py   # Dashboard overview with KPIs
│   │       ├── steps.py      # Steps analysis page
│   │       ├── heart_rate.py # Heart rate analysis page
│   │       ├── sleep.py      # Sleep analysis page
│   │       ├── zone_minutes.py # Zone minutes page
│   │       └── activities.py # Activity log page
│   ├── ingest/
│   │   ├── base.py           # Base ingestor class
│   │   ├── steps.py          # Steps data ingestor
│   │   ├── heart_rate.py     # Heart rate ingestor
│   │   ├── sleep.py          # Sleep data ingestor
│   │   ├── zone_minutes.py   # Zone minutes ingestor
│   │   └── activities.py     # Activities ingestor
│   └── storage/
│       ├── duckdb_manager.py # DuckDB query manager
│       └── parquet_writer.py # Parquet file writer
├── data/
│   └── parquet/              # Processed parquet files
├── Fitbit/
│   └── Global Export Data/   # Raw Fitbit JSON exports (not in repo)
└── requirements.txt
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd personal-fitness-diary-advisor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Fitbit data**

   Export your data from Fitbit and place the JSON files in:
   ```
   Fitbit/Global Export Data/
   ```

   Expected file patterns:
   - `steps-*.json`
   - `heart_rate-*.json`
   - `resting_heart_rate-*.json`
   - `sleep-*.json`
   - `time_in_heart_rate_zones-*.json`
   - `exercise-*.json`

5. **Run the ETL pipeline**
   ```bash
   python scripts/run_pipeline.py
   ```

6. **Launch the dashboard**
   ```bash
   streamlit run src/dashboard/app.py
   ```

## Data Processing

The ETL pipeline processes raw Fitbit JSON exports into optimized Parquet files:

| Data Type | Source Pattern | Output File | Records |
|-----------|---------------|-------------|---------|
| Steps | `steps-*.json` | `steps_daily.parquet` | Daily totals |
| Heart Rate | `heart_rate-*.json` | `heart_rate_hourly.parquet` | Hourly aggregates |
| Resting HR | `resting_heart_rate-*.json` | `resting_heart_rate.parquet` | Daily values |
| Sleep | `sleep-*.json` | `sleep_sessions.parquet` | Per-session data |
| Zone Minutes | `time_in_heart_rate_zones-*.json` | `zone_minutes_daily.parquet` | Daily zone breakdown |
| Activities | `exercise-*.json` | `activities.parquet` | Individual exercises |

## Technology Stack

- **Python 3.12+**
- **Pandas** - Data manipulation
- **DuckDB** - Fast analytical queries
- **Streamlit** - Interactive dashboard
- **Plotly** - Interactive visualizations
- **Parquet** - Columnar storage format

## License

Private project for personal use.

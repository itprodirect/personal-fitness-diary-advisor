"""Configuration settings for the Personal Fitness Diary Advisor."""

from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
FITBIT_DATA_PATH = PROJECT_ROOT / "Fitbit" / "Global Export Data"
DATA_PATH = PROJECT_ROOT / "data"
PARQUET_PATH = DATA_PATH / "parquet"
DUCKDB_PATH = DATA_PATH / "fitness.duckdb"

# Ensure directories exist
PARQUET_PATH.mkdir(parents=True, exist_ok=True)

# File patterns for each data type
FILE_PATTERNS = {
    "steps": "steps-*.json",
    "heart_rate": "heart_rate-*.json",
    "resting_heart_rate": "resting_heart_rate-*.json",
    "sleep": "sleep-*.json",
}

# Parquet file names
PARQUET_FILES = {
    "steps_daily": PARQUET_PATH / "steps_daily.parquet",
    "heart_rate_hourly": PARQUET_PATH / "heart_rate_hourly.parquet",
    "resting_heart_rate": PARQUET_PATH / "resting_heart_rate.parquet",
    "sleep_sessions": PARQUET_PATH / "sleep_sessions.parquet",
}

# Dashboard settings
DEFAULT_DATE_RANGE_DAYS = 30
STEPS_GOAL = 10000

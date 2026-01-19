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
    "zone_minutes": "time_in_heart_rate_zones-*.json",
    "activities": "exercise-*.json",
}

# Parquet file names
PARQUET_FILES = {
    "steps_daily": PARQUET_PATH / "steps_daily.parquet",
    "heart_rate_hourly": PARQUET_PATH / "heart_rate_hourly.parquet",
    "resting_heart_rate": PARQUET_PATH / "resting_heart_rate.parquet",
    "sleep_sessions": PARQUET_PATH / "sleep_sessions.parquet",
    "zone_minutes_daily": PARQUET_PATH / "zone_minutes_daily.parquet",
    "activities": PARQUET_PATH / "activities.parquet",
}

# Dashboard settings
DEFAULT_DATE_RANGE_DAYS = 30

# User-configurable goals (defaults)
GOALS = {
    "steps_daily": 10000,
    "sleep_hours": 8,
    "sleep_hours_minimum": 7,
    "sleep_efficiency": 85,
    "zone_minutes_daily": 30,
}

# Chart settings
CHART_CONFIG = {
    "rolling_window_short": 7,
    "rolling_window_long": 30,
    "histogram_bins": 30,
}

# Legacy - keep for backward compatibility
STEPS_GOAL = GOALS["steps_daily"]

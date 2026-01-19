"""Sleep data ingestor."""

import pandas as pd
from pathlib import Path
from .base import BaseIngestor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SleepIngestor(BaseIngestor):
    """Ingestor for Fitbit sleep data."""

    # Mapping from classic stages to modern stages
    CLASSIC_TO_STAGES = {
        "awake": "wake",
        "restless": "light",  # Best approximation
        "asleep": "light",    # Best approximation
    }

    def __init__(self, data_path: Path):
        super().__init__(data_path, "sleep-*.json")

    def ingest(self) -> pd.DataFrame:
        """Load and process all sleep data."""
        all_data = self.load_all_files()
        if not all_data:
            return pd.DataFrame()

        # Process each sleep session
        sessions = []
        for record in all_data:
            session = self._process_session(record)
            if session:
                sessions.append(session)

        if not sessions:
            return pd.DataFrame()

        df = pd.DataFrame(sessions)
        return self.transform(df)

    def _process_session(self, record: dict) -> dict | None:
        """Process a single sleep session record."""
        try:
            sleep_type = record.get("type", "classic")
            levels = record.get("levels", {})
            summary = levels.get("summary", {})

            # Base session info
            session = {
                "log_id": record.get("logId"),
                "date": record.get("dateOfSleep"),
                "start_time": record.get("startTime"),
                "end_time": record.get("endTime"),
                "duration_ms": record.get("duration", 0),
                "duration_hours": record.get("duration", 0) / 3600000,
                "minutes_asleep": record.get("minutesAsleep", 0),
                "minutes_awake": record.get("minutesAwake", 0),
                "time_in_bed": record.get("timeInBed", 0),
                "efficiency": record.get("efficiency", 0),
                "sleep_type": sleep_type,
            }

            # Extract stage minutes based on sleep type
            if sleep_type == "stages":
                # Modern sleep tracking with stages
                session["wake_minutes"] = summary.get("wake", {}).get("minutes", 0)
                session["light_minutes"] = summary.get("light", {}).get("minutes", 0)
                session["deep_minutes"] = summary.get("deep", {}).get("minutes", 0)
                session["rem_minutes"] = summary.get("rem", {}).get("minutes", 0)
            else:
                # Classic sleep tracking - normalize to stages format
                awake_mins = summary.get("awake", {}).get("minutes", 0)
                restless_mins = summary.get("restless", {}).get("minutes", 0)
                asleep_mins = summary.get("asleep", {}).get("minutes", 0)

                session["wake_minutes"] = awake_mins
                session["light_minutes"] = restless_mins + asleep_mins
                session["deep_minutes"] = 0  # Not tracked in classic
                session["rem_minutes"] = 0   # Not tracked in classic

            return session
        except Exception as e:
            logger.warning("Could not process sleep session: %s", e)
            return None

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform sleep data into final format."""
        if df.empty:
            return df

        # Parse dates
        df["date"] = pd.to_datetime(df["date"])
        df["start_time"] = pd.to_datetime(df["start_time"])
        df["end_time"] = pd.to_datetime(df["end_time"])

        # Round numeric columns
        df["duration_hours"] = df["duration_hours"].round(2)

        # Sort by date
        return df.sort_values("date").reset_index(drop=True)

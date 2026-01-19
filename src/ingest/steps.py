"""Steps data ingestor."""

import pandas as pd
from pathlib import Path
from .base import BaseIngestor


class StepsIngestor(BaseIngestor):
    """Ingestor for Fitbit steps data."""

    def __init__(self, data_path: Path):
        super().__init__(data_path, "steps-*.json")

    def ingest(self) -> pd.DataFrame:
        """Load and process all steps data."""
        all_data = self.load_all_files()
        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        return self.transform(df)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform steps data to daily aggregates."""
        if df.empty:
            return df

        # Parse datetime - format is "MM/DD/YY HH:MM:SS"
        df["datetime"] = pd.to_datetime(df["dateTime"], format="%m/%d/%y %H:%M:%S")
        df["date"] = df["datetime"].dt.date
        df["steps"] = pd.to_numeric(df["value"], errors="coerce").fillna(0).astype(int)

        # Aggregate to daily
        daily = df.groupby("date").agg(
            total_steps=("steps", "sum"),
            active_minutes=("steps", lambda x: (x > 0).sum()),
        ).reset_index()

        daily["date"] = pd.to_datetime(daily["date"])
        return daily.sort_values("date").reset_index(drop=True)

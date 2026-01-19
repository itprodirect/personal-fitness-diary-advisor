"""Heart rate data ingestors."""

import pandas as pd
from pathlib import Path
from .base import BaseIngestor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HeartRateIngestor(BaseIngestor):
    """Ingestor for Fitbit heart rate data."""

    BATCH_SIZE = 100  # Process 100 files at a time

    def __init__(self, data_path: Path):
        super().__init__(data_path, "heart_rate-*.json")

    def ingest(self) -> pd.DataFrame:
        """Load and process all heart rate data in batches."""
        files = self.get_files()
        if not files:
            return pd.DataFrame()

        logger.info("Processing %d heart rate files in batches...", len(files))

        all_hourly = []
        for i in range(0, len(files), self.BATCH_SIZE):
            batch_files = files[i:i + self.BATCH_SIZE]
            batch_data = []

            for f in batch_files:
                try:
                    data = self.load_json_file(f)
                    batch_data.extend(data)
                except Exception as e:
                    logger.warning("Could not load %s: %s", f, e)

            if batch_data:
                df = pd.DataFrame(batch_data)
                hourly = self._transform_batch(df)
                if not hourly.empty:
                    all_hourly.append(hourly)

            logger.info("Processed %d/%d files", min(i + self.BATCH_SIZE, len(files)), len(files))

        if not all_hourly:
            return pd.DataFrame()

        # Combine all batches and re-aggregate in case of overlapping hours
        combined = pd.concat(all_hourly, ignore_index=True)
        return self._final_aggregate(combined)

    def _transform_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform a batch of heart rate data to hourly aggregates."""
        if df.empty:
            return df

        # Parse datetime - format is "MM/DD/YY HH:MM:SS"
        df["datetime"] = pd.to_datetime(df["dateTime"], format="%m/%d/%y %H:%M:%S")

        # Extract bpm from nested value
        df["bpm"] = df["value"].apply(lambda x: x.get("bpm") if isinstance(x, dict) else None)

        # Filter out invalid readings
        df = df.dropna(subset=["bpm"])
        if df.empty:
            return df

        df["bpm"] = df["bpm"].astype(int)

        # Create hour column for aggregation
        df["hour"] = df["datetime"].dt.floor("h")

        # Aggregate to hourly with sum/count for later re-aggregation
        hourly = df.groupby("hour").agg(
            bpm_sum=("bpm", "sum"),
            bpm_count=("bpm", "count"),
            min_bpm=("bpm", "min"),
            max_bpm=("bpm", "max"),
        ).reset_index()

        return hourly

    def _final_aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final aggregation to handle overlapping hours from batches."""
        if df.empty:
            return df

        # Re-aggregate by hour
        final = df.groupby("hour").agg(
            bpm_sum=("bpm_sum", "sum"),
            bpm_count=("bpm_count", "sum"),
            min_bpm=("min_bpm", "min"),
            max_bpm=("max_bpm", "max"),
        ).reset_index()

        # Calculate average
        final["avg_bpm"] = (final["bpm_sum"] / final["bpm_count"]).round(1)
        final["reading_count"] = final["bpm_count"]

        # Select final columns
        result = final[["hour", "avg_bpm", "min_bpm", "max_bpm", "reading_count"]]
        return result.sort_values("hour").reset_index(drop=True)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform heart rate data to hourly aggregates (for compatibility)."""
        return self._transform_batch(df)


class RestingHeartRateIngestor(BaseIngestor):
    """Ingestor for Fitbit resting heart rate data."""

    def __init__(self, data_path: Path):
        super().__init__(data_path, "resting_heart_rate-*.json")

    def ingest(self) -> pd.DataFrame:
        """Load and process all resting heart rate data."""
        all_data = self.load_all_files()
        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        return self.transform(df)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform resting heart rate data."""
        if df.empty:
            return df

        # Parse datetime - format is "MM/DD/YY HH:MM:SS"
        df["datetime"] = pd.to_datetime(df["dateTime"], format="%m/%d/%y %H:%M:%S")
        df["date"] = df["datetime"].dt.date

        # Extract values from nested structure
        df["resting_hr"] = df["value"].apply(lambda x: x.get("value") if isinstance(x, dict) else None)
        df["error"] = df["value"].apply(lambda x: x.get("error") if isinstance(x, dict) else None)

        # Filter out invalid readings
        df = df.dropna(subset=["resting_hr"])
        df["resting_hr"] = df["resting_hr"].round(1)
        df["error"] = df["error"].round(2)

        # Select relevant columns
        result = df[["date", "resting_hr", "error"]].copy()
        result["date"] = pd.to_datetime(result["date"])
        return result.sort_values("date").reset_index(drop=True)

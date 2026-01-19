"""Activities (exercise) data ingestor."""

import pandas as pd
from pathlib import Path
from .base import BaseIngestor


class ActivitiesIngestor(BaseIngestor):
    """Ingestor for Fitbit exercise/activity data."""

    def __init__(self, data_path: Path):
        super().__init__(data_path, "exercise-*.json")

    def ingest(self) -> pd.DataFrame:
        """Load and process all activities data."""
        all_data = self.load_all_files()
        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        return self.transform(df)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform activities data."""
        if df.empty:
            return df

        # Parse start time - format is "MM/DD/YY HH:MM:SS"
        df["start_time"] = pd.to_datetime(df["startTime"], format="%m/%d/%y %H:%M:%S")
        df["date"] = df["start_time"].dt.date

        # Convert duration from milliseconds to minutes
        df["duration_minutes"] = df["activeDuration"].fillna(df["duration"]) / 60000.0

        # Extract heart rate zone minutes from nested array
        def get_zone_minutes(hr_zones, zone_name):
            if hr_zones is None or not isinstance(hr_zones, list):
                return 0
            for zone in hr_zones:
                if isinstance(zone, dict) and zone.get("name") == zone_name:
                    return zone.get("minutes", 0)
            return 0

        df["fat_burn_minutes"] = df["heartRateZones"].apply(
            lambda x: get_zone_minutes(x, "Fat Burn")
        )
        df["cardio_minutes"] = df["heartRateZones"].apply(
            lambda x: get_zone_minutes(x, "Cardio")
        )
        df["peak_minutes"] = df["heartRateZones"].apply(
            lambda x: get_zone_minutes(x, "Peak")
        )

        # Handle missing values
        df["calories"] = pd.to_numeric(df.get("calories", 0), errors="coerce").fillna(0)
        df["distance"] = pd.to_numeric(df.get("distance", 0), errors="coerce").fillna(0)
        df["avg_heart_rate"] = pd.to_numeric(
            df.get("averageHeartRate", 0), errors="coerce"
        ).fillna(0)
        df["steps"] = pd.to_numeric(df.get("steps", 0), errors="coerce").fillna(0)

        # Select columns for output
        result = df[
            [
                "logId",
                "date",
                "start_time",
                "activityName",
                "duration_minutes",
                "calories",
                "distance",
                "avg_heart_rate",
                "steps",
                "fat_burn_minutes",
                "cardio_minutes",
                "peak_minutes",
            ]
        ].copy()

        # Rename columns
        result = result.rename(columns={"activityName": "activity_name"})

        # Convert date to datetime
        result["date"] = pd.to_datetime(result["date"])

        # Sort by start_time and reset index
        return result.sort_values("start_time").reset_index(drop=True)

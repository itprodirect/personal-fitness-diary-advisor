"""Zone minutes (time in heart rate zones) data ingestor."""

import pandas as pd
from pathlib import Path
from .base import BaseIngestor


class ZoneMinutesIngestor(BaseIngestor):
    """Ingestor for Fitbit time in heart rate zones data."""

    def __init__(self, data_path: Path):
        super().__init__(data_path, "time_in_heart_rate_zones-*.json")

    def ingest(self) -> pd.DataFrame:
        """Load and process all zone minutes data."""
        all_data = self.load_all_files()
        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        return self.transform(df)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform zone minutes data to daily format."""
        if df.empty:
            return df

        # Parse datetime - format is "MM/DD/YY HH:MM:SS"
        df["date"] = pd.to_datetime(df["dateTime"], format="%m/%d/%y %H:%M:%S").dt.date

        # Extract zone values from nested structure
        # Zone mapping:
        # IN_DEFAULT_ZONE_1 = Fat Burn
        # IN_DEFAULT_ZONE_2 = Cardio
        # IN_DEFAULT_ZONE_3 = Peak
        # BELOW_DEFAULT_ZONE_1 = Out of Range
        df["fat_burn_minutes"] = df["value"].apply(
            lambda x: x.get("valuesInZones", {}).get("IN_DEFAULT_ZONE_1", 0)
        )
        df["cardio_minutes"] = df["value"].apply(
            lambda x: x.get("valuesInZones", {}).get("IN_DEFAULT_ZONE_2", 0)
        )
        df["peak_minutes"] = df["value"].apply(
            lambda x: x.get("valuesInZones", {}).get("IN_DEFAULT_ZONE_3", 0)
        )
        df["out_of_range_minutes"] = df["value"].apply(
            lambda x: x.get("valuesInZones", {}).get("BELOW_DEFAULT_ZONE_1", 0)
        )

        # Calculate total active zone minutes (Fat Burn + Cardio + Peak)
        df["total_active_minutes"] = (
            df["fat_burn_minutes"] + df["cardio_minutes"] + df["peak_minutes"]
        )

        # Select and aggregate by date (in case of duplicates)
        result = df.groupby("date").agg(
            fat_burn_minutes=("fat_burn_minutes", "sum"),
            cardio_minutes=("cardio_minutes", "sum"),
            peak_minutes=("peak_minutes", "sum"),
            out_of_range_minutes=("out_of_range_minutes", "sum"),
            total_active_minutes=("total_active_minutes", "sum"),
        ).reset_index()

        result["date"] = pd.to_datetime(result["date"])
        return result.sort_values("date").reset_index(drop=True)

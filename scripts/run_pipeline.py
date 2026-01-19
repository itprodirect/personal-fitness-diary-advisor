"""ETL pipeline script to process Fitbit data."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.config.settings import FITBIT_DATA_PATH, PARQUET_PATH
from src.ingest import (
    StepsIngestor,
    HeartRateIngestor,
    RestingHeartRateIngestor,
    SleepIngestor,
    ZoneMinutesIngestor,
    ActivitiesIngestor,
)
from src.storage import ParquetWriter

logger = get_logger(__name__)


def run_pipeline():
    """Run the full ETL pipeline."""
    logger.info("=" * 60)
    logger.info("Personal Fitness Diary Advisor - ETL Pipeline")
    logger.info("=" * 60)

    writer = ParquetWriter(PARQUET_PATH)

    # Process steps data
    logger.info("[1/6] Processing steps data...")
    steps_ingestor = StepsIngestor(FITBIT_DATA_PATH)
    steps_df = steps_ingestor.ingest()
    writer.write(steps_df, "steps_daily.parquet")
    if not steps_df.empty:
        logger.info("  Date range: %s to %s", steps_df['date'].min(), steps_df['date'].max())

    # Process heart rate data
    logger.info("[2/6] Processing heart rate data...")
    hr_ingestor = HeartRateIngestor(FITBIT_DATA_PATH)
    hr_df = hr_ingestor.ingest()
    writer.write(hr_df, "heart_rate_hourly.parquet")
    if not hr_df.empty:
        logger.info("  Date range: %s to %s", hr_df['hour'].min(), hr_df['hour'].max())

    # Process resting heart rate data
    logger.info("[3/6] Processing resting heart rate data...")
    rhr_ingestor = RestingHeartRateIngestor(FITBIT_DATA_PATH)
    rhr_df = rhr_ingestor.ingest()
    writer.write(rhr_df, "resting_heart_rate.parquet")
    if not rhr_df.empty:
        logger.info("  Date range: %s to %s", rhr_df['date'].min(), rhr_df['date'].max())

    # Process sleep data
    logger.info("[4/6] Processing sleep data...")
    sleep_ingestor = SleepIngestor(FITBIT_DATA_PATH)
    sleep_df = sleep_ingestor.ingest()
    writer.write(sleep_df, "sleep_sessions.parquet")
    if not sleep_df.empty:
        logger.info("  Date range: %s to %s", sleep_df['date'].min(), sleep_df['date'].max())

    # Process zone minutes data
    logger.info("[5/6] Processing zone minutes data...")
    zone_ingestor = ZoneMinutesIngestor(FITBIT_DATA_PATH)
    zone_df = zone_ingestor.ingest()
    writer.write(zone_df, "zone_minutes_daily.parquet")
    if not zone_df.empty:
        logger.info("  Date range: %s to %s", zone_df['date'].min(), zone_df['date'].max())

    # Process activities data
    logger.info("[6/6] Processing activities data...")
    activities_ingestor = ActivitiesIngestor(FITBIT_DATA_PATH)
    activities_df = activities_ingestor.ingest()
    writer.write(activities_df, "activities.parquet")
    if not activities_df.empty:
        logger.info("  Date range: %s to %s", activities_df['date'].min(), activities_df['date'].max())
        logger.info("  Total activities: %d", len(activities_df))

    logger.info("=" * 60)
    logger.info("Pipeline completed successfully!")
    logger.info("Parquet files written to: %s", PARQUET_PATH)
    logger.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()

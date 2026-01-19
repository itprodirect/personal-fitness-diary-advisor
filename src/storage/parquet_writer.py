"""Parquet file writer for processed data."""

from pathlib import Path
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ParquetWriter:
    """Write DataFrames to Parquet files."""

    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.output_path.mkdir(parents=True, exist_ok=True)

    def write(self, df: pd.DataFrame, filename: str) -> Path:
        """Write a DataFrame to a Parquet file."""
        if df.empty:
            logger.warning("Empty DataFrame, skipping write for %s", filename)
            return None

        file_path = self.output_path / filename
        df.to_parquet(file_path, index=False, engine="pyarrow")
        logger.info("Wrote %d records to %s", len(df), file_path)
        return file_path

    def read(self, filename: str) -> pd.DataFrame:
        """Read a Parquet file into a DataFrame."""
        file_path = self.output_path / filename
        if not file_path.exists():
            return pd.DataFrame()
        return pd.read_parquet(file_path)

    def exists(self, filename: str) -> bool:
        """Check if a Parquet file exists."""
        return (self.output_path / filename).exists()

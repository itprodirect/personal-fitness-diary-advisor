"""Base class for data ingestors."""

from abc import ABC, abstractmethod
from pathlib import Path
import json
import pandas as pd
from typing import List


class BaseIngestor(ABC):
    """Abstract base class for all data ingestors."""

    def __init__(self, data_path: Path, file_pattern: str):
        self.data_path = data_path
        self.file_pattern = file_pattern

    def get_files(self) -> List[Path]:
        """Get all files matching the pattern."""
        return sorted(self.data_path.glob(self.file_pattern))

    def load_json_file(self, file_path: Path) -> list:
        """Load a single JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_all_files(self) -> list:
        """Load all matching JSON files and combine their data."""
        all_data = []
        for file_path in self.get_files():
            try:
                data = self.load_json_file(file_path)
                all_data.extend(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load {file_path}: {e}")
        return all_data

    @abstractmethod
    def ingest(self) -> pd.DataFrame:
        """Ingest data and return a DataFrame."""
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform the raw DataFrame into the final format."""
        pass

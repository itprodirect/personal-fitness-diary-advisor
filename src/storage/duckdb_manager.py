"""DuckDB connection and query manager."""

from pathlib import Path
import duckdb
import pandas as pd


class DuckDBManager:
    """Manage DuckDB connections and queries."""

    def __init__(self, db_path: Path, parquet_path: Path):
        self.db_path = db_path
        self.parquet_path = parquet_path
        self._conn = None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create a DuckDB connection."""
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
            self._create_views()
        return self._conn

    def _create_views(self):
        """Create views for all Parquet files."""
        parquet_files = {
            "steps_daily": "steps_daily.parquet",
            "heart_rate_hourly": "heart_rate_hourly.parquet",
            "resting_heart_rate": "resting_heart_rate.parquet",
            "sleep_sessions": "sleep_sessions.parquet",
            "zone_minutes_daily": "zone_minutes_daily.parquet",
            "activities": "activities.parquet",
        }

        for view_name, filename in parquet_files.items():
            file_path = self.parquet_path / filename
            if file_path.exists():
                self.conn.execute(f"""
                    CREATE OR REPLACE VIEW {view_name} AS
                    SELECT * FROM read_parquet('{file_path}')
                """)

    def query(self, sql: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        return self.conn.execute(sql).fetchdf()

    def get_date_range(self) -> tuple:
        """Get the overall date range of all data."""
        try:
            result = self.query("""
                SELECT
                    MIN(date) as min_date,
                    MAX(date) as max_date
                FROM (
                    SELECT date FROM steps_daily
                    UNION ALL
                    SELECT date FROM resting_heart_rate
                    UNION ALL
                    SELECT date FROM sleep_sessions
                    UNION ALL
                    SELECT date FROM zone_minutes_daily
                    UNION ALL
                    SELECT date FROM activities
                )
            """)
            if not result.empty:
                return result.iloc[0]["min_date"], result.iloc[0]["max_date"]
        except Exception:
            pass
        return None, None

    def get_steps_daily(self, start_date=None, end_date=None) -> pd.DataFrame:
        """Get daily steps data with optional date filtering."""
        sql = "SELECT * FROM steps_daily"
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY date"
        return self.query(sql)

    def get_heart_rate_hourly(self, start_date=None, end_date=None) -> pd.DataFrame:
        """Get hourly heart rate data with optional date filtering."""
        sql = "SELECT * FROM heart_rate_hourly"
        conditions = []
        if start_date:
            conditions.append(f"hour >= '{start_date}'")
        if end_date:
            conditions.append(f"hour <= '{end_date}'")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY hour"
        return self.query(sql)

    def get_resting_heart_rate(self, start_date=None, end_date=None) -> pd.DataFrame:
        """Get resting heart rate data with optional date filtering."""
        sql = "SELECT * FROM resting_heart_rate"
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY date"
        return self.query(sql)

    def get_sleep_sessions(self, start_date=None, end_date=None) -> pd.DataFrame:
        """Get sleep session data with optional date filtering."""
        sql = "SELECT * FROM sleep_sessions"
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY date"
        return self.query(sql)

    def get_zone_minutes_daily(self, start_date=None, end_date=None) -> pd.DataFrame:
        """Get daily zone minutes data with optional date filtering."""
        sql = "SELECT * FROM zone_minutes_daily"
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY date"
        return self.query(sql)

    def get_activities(self, start_date=None, end_date=None) -> pd.DataFrame:
        """Get activities data with optional date filtering."""
        sql = "SELECT * FROM activities"
        conditions = []
        if start_date:
            conditions.append(f"date >= '{start_date}'")
        if end_date:
            conditions.append(f"date <= '{end_date}'")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY start_time"
        return self.query(sql)

    def get_activity_names(self) -> list:
        """Get list of unique activity names."""
        try:
            result = self.query("SELECT DISTINCT activity_name FROM activities ORDER BY activity_name")
            return result["activity_name"].tolist()
        except Exception:
            return []

    def close(self):
        """Close the DuckDB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

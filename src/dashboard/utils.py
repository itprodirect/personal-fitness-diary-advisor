"""Shared dashboard utilities."""

import streamlit as st
import pandas as pd


def add_csv_download(df: pd.DataFrame, filename_prefix: str, start_date, end_date):
    """Add a CSV download button for the given DataFrame.

    Args:
        df: The DataFrame to export
        filename_prefix: Prefix for the filename (e.g., "steps", "zone_minutes")
        start_date: Start date for the filename
        end_date: End date for the filename
    """
    if df.empty:
        return

    csv = df.to_csv(index=False)
    filename = f"{filename_prefix}_{start_date}_to_{end_date}.csv"

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        key=f"download_{filename_prefix}",
    )

"""Data quality dashboard page."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.storage import DuckDBManager
from src.config.settings import PARQUET_PATH
from src.dashboard.theme import get_theme_colors, get_plotly_layout_defaults


def render_data_quality(db: DuckDBManager, theme: str = "light"):
    """Render the data quality dashboard page."""
    colors = get_theme_colors(theme)
    layout_defaults = get_plotly_layout_defaults(theme)

    st.title("Data Quality")
    st.caption("Overview of data completeness and freshness")

    # Data source definitions
    data_sources = {
        "Steps": {
            "query_method": "get_steps_daily",
            "date_column": "date",
            "parquet_file": "steps_daily.parquet",
        },
        "Heart Rate (Hourly)": {
            "query_method": "get_heart_rate_hourly",
            "date_column": "hour",
            "parquet_file": "heart_rate_hourly.parquet",
        },
        "Resting Heart Rate": {
            "query_method": "get_resting_heart_rate",
            "date_column": "date",
            "parquet_file": "resting_heart_rate.parquet",
        },
        "Sleep": {
            "query_method": "get_sleep_sessions",
            "date_column": "date",
            "parquet_file": "sleep_sessions.parquet",
        },
        "Zone Minutes": {
            "query_method": "get_zone_minutes_daily",
            "date_column": "date",
            "parquet_file": "zone_minutes_daily.parquet",
        },
        "Activities": {
            "query_method": "get_activities",
            "date_column": "date",
            "parquet_file": "activities.parquet",
        },
    }

    # Collect metrics for each data source
    metrics = []
    for name, config in data_sources.items():
        try:
            query_method = getattr(db, config["query_method"])
            df = query_method()

            if df.empty:
                metrics.append({
                    "Source": name,
                    "Records": 0,
                    "Date Range": "No data",
                    "First Date": None,
                    "Last Date": None,
                    "Days with Data": 0,
                    "File Size": get_file_size(config["parquet_file"]),
                    "Last Updated": get_file_modified_time(config["parquet_file"]),
                })
            else:
                date_col = config["date_column"]
                dates = pd.to_datetime(df[date_col])
                first_date = dates.min()
                last_date = dates.max()

                # For hourly data, count unique dates
                if date_col == "hour":
                    unique_days = dates.dt.date.nunique()
                else:
                    unique_days = dates.nunique()

                metrics.append({
                    "Source": name,
                    "Records": len(df),
                    "Date Range": f"{first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}",
                    "First Date": first_date,
                    "Last Date": last_date,
                    "Days with Data": unique_days,
                    "File Size": get_file_size(config["parquet_file"]),
                    "Last Updated": get_file_modified_time(config["parquet_file"]),
                })
        except Exception as e:
            metrics.append({
                "Source": name,
                "Records": 0,
                "Date Range": f"Error: {str(e)[:30]}",
                "First Date": None,
                "Last Date": None,
                "Days with Data": 0,
                "File Size": "N/A",
                "Last Updated": "N/A",
            })

    metrics_df = pd.DataFrame(metrics)

    # Summary KPIs
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_records = metrics_df["Records"].sum()
        st.metric("Total Records", f"{total_records:,}")

    with col2:
        sources_with_data = (metrics_df["Records"] > 0).sum()
        st.metric("Active Data Sources", f"{sources_with_data}/{len(data_sources)}")

    with col3:
        # Find overall date range
        valid_first = metrics_df["First Date"].dropna()
        valid_last = metrics_df["Last Date"].dropna()
        if len(valid_first) > 0:
            overall_first = valid_first.min()
            st.metric("Earliest Data", overall_first.strftime("%Y-%m-%d"))
        else:
            st.metric("Earliest Data", "N/A")

    with col4:
        if len(valid_last) > 0:
            overall_last = valid_last.max()
            st.metric("Latest Data", overall_last.strftime("%Y-%m-%d"))
        else:
            st.metric("Latest Data", "N/A")

    st.divider()

    # Data source details table
    st.subheader("Data Source Details")

    display_df = metrics_df[["Source", "Records", "Date Range", "Days with Data", "File Size", "Last Updated"]].copy()
    display_df["Records"] = display_df["Records"].apply(lambda x: f"{x:,}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # Record counts visualization
    st.subheader("Record Counts by Source")

    fig_counts = go.Figure(data=[
        go.Bar(
            x=metrics_df["Source"],
            y=metrics_df["Records"],
            marker_color=colors["steps"]["primary"],
            text=metrics_df["Records"].apply(lambda x: f"{x:,}"),
            textposition="auto",
        )
    ])

    fig_counts.update_layout(
        xaxis_title="Data Source",
        yaxis_title="Number of Records",
        **layout_defaults,
    )

    st.plotly_chart(fig_counts, use_container_width=True)

    # Data coverage timeline
    st.subheader("Data Coverage Timeline")

    # Filter to sources with data
    timeline_data = metrics_df[metrics_df["Records"] > 0].copy()

    if not timeline_data.empty:
        fig_timeline = go.Figure()

        for i, row in timeline_data.iterrows():
            if row["First Date"] is not None and row["Last Date"] is not None:
                fig_timeline.add_trace(go.Scatter(
                    x=[row["First Date"], row["Last Date"]],
                    y=[row["Source"], row["Source"]],
                    mode="lines+markers",
                    name=row["Source"],
                    line=dict(width=10),
                    marker=dict(size=12),
                    hovertemplate=f"{row['Source']}<br>%{{x}}<extra></extra>",
                ))

        fig_timeline.update_layout(
            xaxis_title="Date",
            yaxis_title="Data Source",
            showlegend=False,
            **layout_defaults,
        )

        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No data available to display timeline.")

    # Data gaps analysis
    st.subheader("Data Freshness")

    freshness_data = []
    for _, row in metrics_df.iterrows():
        if row["Last Date"] is not None:
            days_since_update = (datetime.now() - row["Last Date"]).days
            freshness_data.append({
                "Source": row["Source"],
                "Days Since Last Data": days_since_update,
                "Status": "Current" if days_since_update <= 7 else ("Stale" if days_since_update <= 30 else "Old"),
            })
        else:
            freshness_data.append({
                "Source": row["Source"],
                "Days Since Last Data": None,
                "Status": "No Data",
            })

    freshness_df = pd.DataFrame(freshness_data)

    # Color-coded status indicators
    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(freshness_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Status Legend:**")
        st.markdown("- **Current**: Data within last 7 days")
        st.markdown("- **Stale**: Data 8-30 days old")
        st.markdown("- **Old**: Data > 30 days old")
        st.markdown("- **No Data**: No records found")

    st.divider()

    # Refresh instructions
    st.subheader("Refresh Data")
    st.markdown("To update your fitness data, run the ETL pipeline:")
    st.code("python scripts/run_pipeline.py")
    st.caption("This will process new data from your Fitbit export and update all Parquet files.")


def get_file_size(filename: str) -> str:
    """Get formatted file size for a Parquet file."""
    file_path = PARQUET_PATH / filename
    if file_path.exists():
        size_bytes = file_path.stat().st_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    return "N/A"


def get_file_modified_time(filename: str) -> str:
    """Get formatted last modified time for a Parquet file."""
    file_path = PARQUET_PATH / filename
    if file_path.exists():
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        return mtime.strftime("%Y-%m-%d %H:%M")
    return "N/A"

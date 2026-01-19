"""Heart rate analysis page."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.storage import DuckDBManager


def render_heart_rate(db: DuckDBManager, start_date, end_date):
    """Render the heart rate analysis page."""
    st.title("Heart Rate Analysis")
    st.caption(f"Showing data from {start_date} to {end_date}")

    # Get data
    rhr_df = db.get_resting_heart_rate(start_date, end_date)
    hr_hourly_df = db.get_heart_rate_hourly(start_date, end_date)

    # Resting Heart Rate Section
    st.subheader("Resting Heart Rate")

    if not rhr_df.empty:
        # Stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Current", f"{rhr_df['resting_hr'].iloc[-1]:.0f} bpm")
        with col2:
            st.metric("Average", f"{rhr_df['resting_hr'].mean():.1f} bpm")
        with col3:
            st.metric("Lowest", f"{rhr_df['resting_hr'].min():.0f} bpm")
        with col4:
            st.metric("Highest", f"{rhr_df['resting_hr'].max():.0f} bpm")

        # Trend chart with rolling average
        rhr_df = rhr_df.copy()
        rhr_df["rolling_7d"] = rhr_df["resting_hr"].rolling(window=7, min_periods=1).mean()
        rhr_df["rolling_30d"] = rhr_df["resting_hr"].rolling(window=30, min_periods=1).mean()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=rhr_df["date"],
            y=rhr_df["resting_hr"],
            mode="markers",
            name="Daily",
            marker=dict(color="lightcoral", size=5),
        ))
        fig.add_trace(go.Scatter(
            x=rhr_df["date"],
            y=rhr_df["rolling_7d"],
            mode="lines",
            name="7-day Average",
            line=dict(color="red", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=rhr_df["date"],
            y=rhr_df["rolling_30d"],
            mode="lines",
            name="30-day Average",
            line=dict(color="darkred", width=2, dash="dash"),
        ))

        fig.update_layout(
            title="Resting Heart Rate Trend",
            xaxis_title="Date",
            yaxis_title="BPM",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No resting heart rate data available for this period.")

    st.divider()

    # Hourly Heart Rate Section
    st.subheader("Heart Rate Patterns")

    if not hr_hourly_df.empty:
        # Add date and hour columns
        hr_hourly_df = hr_hourly_df.copy()
        hr_hourly_df["date"] = pd.to_datetime(hr_hourly_df["hour"]).dt.date
        hr_hourly_df["hour_of_day"] = pd.to_datetime(hr_hourly_df["hour"]).dt.hour

        col1, col2 = st.columns(2)

        with col1:
            # Average by hour of day
            hourly_avg = hr_hourly_df.groupby("hour_of_day").agg(
                avg_bpm=("avg_bpm", "mean"),
                min_bpm=("min_bpm", "mean"),
                max_bpm=("max_bpm", "mean"),
            ).reset_index()

            fig_hourly = go.Figure()

            # Fill between min and max
            fig_hourly.add_trace(go.Scatter(
                x=hourly_avg["hour_of_day"],
                y=hourly_avg["max_bpm"],
                mode="lines",
                name="Max",
                line=dict(width=0),
                showlegend=False,
            ))
            fig_hourly.add_trace(go.Scatter(
                x=hourly_avg["hour_of_day"],
                y=hourly_avg["min_bpm"],
                mode="lines",
                name="Range",
                fill="tonexty",
                fillcolor="rgba(255, 0, 0, 0.1)",
                line=dict(width=0),
            ))
            fig_hourly.add_trace(go.Scatter(
                x=hourly_avg["hour_of_day"],
                y=hourly_avg["avg_bpm"],
                mode="lines+markers",
                name="Average",
                line=dict(color="red", width=2),
            ))

            fig_hourly.update_layout(
                title="Average Heart Rate by Hour of Day",
                xaxis_title="Hour",
                yaxis_title="BPM",
                xaxis=dict(tickmode="linear", tick0=0, dtick=3),
            )
            st.plotly_chart(fig_hourly, use_container_width=True)

        with col2:
            # Distribution of average heart rates
            fig_dist = px.histogram(
                hr_hourly_df,
                x="avg_bpm",
                nbins=40,
                title="Heart Rate Distribution",
                labels={"avg_bpm": "BPM (Hourly Average)"},
            )
            fig_dist.update_layout(showlegend=False)
            st.plotly_chart(fig_dist, use_container_width=True)

        # Daily min/max/avg chart
        daily_hr = hr_hourly_df.groupby("date").agg(
            avg_bpm=("avg_bpm", "mean"),
            min_bpm=("min_bpm", "min"),
            max_bpm=("max_bpm", "max"),
        ).reset_index()

        fig_daily = go.Figure()

        # Shaded area between min and max
        fig_daily.add_trace(go.Scatter(
            x=daily_hr["date"],
            y=daily_hr["max_bpm"],
            mode="lines",
            name="Max",
            line=dict(width=0),
            showlegend=False,
        ))
        fig_daily.add_trace(go.Scatter(
            x=daily_hr["date"],
            y=daily_hr["min_bpm"],
            mode="lines",
            name="Daily Range",
            fill="tonexty",
            fillcolor="rgba(255, 0, 0, 0.2)",
            line=dict(width=0),
        ))
        fig_daily.add_trace(go.Scatter(
            x=daily_hr["date"],
            y=daily_hr["avg_bpm"],
            mode="lines",
            name="Average",
            line=dict(color="red", width=2),
        ))

        fig_daily.update_layout(
            title="Daily Heart Rate Range",
            xaxis_title="Date",
            yaxis_title="BPM",
            hovermode="x unified",
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    else:
        st.info("No hourly heart rate data available for this period.")

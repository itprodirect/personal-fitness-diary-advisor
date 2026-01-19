"""Overview page with KPIs and trends."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.storage import DuckDBManager
from src.config.settings import GOALS, CHART_CONFIG
from src.dashboard.utils import add_csv_download
from src.dashboard.theme import get_theme_colors, get_plotly_layout_defaults


def render_overview(db: DuckDBManager, start_date, end_date, theme: str = "light"):
    """Render the overview dashboard page."""
    colors = get_theme_colors(theme)
    layout_defaults = get_plotly_layout_defaults(theme)

    st.title("Overview")
    st.caption(f"Showing data from {start_date} to {end_date}")

    # Get data
    steps_df = db.get_steps_daily(start_date, end_date)
    rhr_df = db.get_resting_heart_rate(start_date, end_date)
    sleep_df = db.get_sleep_sessions(start_date, end_date)

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if not steps_df.empty:
            avg_steps = steps_df["total_steps"].mean()
            recent_avg = steps_df.tail(CHART_CONFIG["rolling_window_short"])["total_steps"].mean() if len(steps_df) >= CHART_CONFIG["rolling_window_short"] else avg_steps
            delta = recent_avg - avg_steps
            st.metric(
                "Avg Daily Steps",
                f"{avg_steps:,.0f}",
                delta=f"{delta:+,.0f} vs period avg" if delta != 0 else None,
            )
        else:
            st.metric("Avg Daily Steps", "N/A")

    with col2:
        if not rhr_df.empty:
            avg_rhr = rhr_df["resting_hr"].mean()
            recent_rhr = rhr_df.tail(CHART_CONFIG["rolling_window_short"])["resting_hr"].mean() if len(rhr_df) >= CHART_CONFIG["rolling_window_short"] else avg_rhr
            delta = recent_rhr - avg_rhr
            st.metric(
                "Avg Resting HR",
                f"{avg_rhr:.1f} bpm",
                delta=f"{delta:+.1f}" if delta != 0 else None,
                delta_color="inverse",  # Lower HR is better
            )
        else:
            st.metric("Avg Resting HR", "N/A")

    with col3:
        if not sleep_df.empty:
            avg_sleep = sleep_df["duration_hours"].mean()
            recent_sleep = sleep_df.tail(CHART_CONFIG["rolling_window_short"])["duration_hours"].mean() if len(sleep_df) >= CHART_CONFIG["rolling_window_short"] else avg_sleep
            delta = recent_sleep - avg_sleep
            st.metric(
                "Avg Sleep",
                f"{avg_sleep:.1f} hrs",
                delta=f"{delta:+.1f} hrs" if delta != 0 else None,
            )
        else:
            st.metric("Avg Sleep", "N/A")

    with col4:
        if not sleep_df.empty:
            avg_efficiency = sleep_df["efficiency"].mean()
            recent_eff = sleep_df.tail(CHART_CONFIG["rolling_window_short"])["efficiency"].mean() if len(sleep_df) >= CHART_CONFIG["rolling_window_short"] else avg_efficiency
            delta = recent_eff - avg_efficiency
            st.metric(
                "Sleep Efficiency",
                f"{avg_efficiency:.0f}%",
                delta=f"{delta:+.0f}%" if delta != 0 else None,
            )
        else:
            st.metric("Sleep Efficiency", "N/A")

    st.divider()

    # CSV downloads
    col1, col2, col3 = st.columns(3)
    with col1:
        add_csv_download(steps_df, "overview_steps", start_date, end_date)
    with col2:
        add_csv_download(rhr_df, "overview_heart_rate", start_date, end_date)
    with col3:
        add_csv_download(sleep_df, "overview_sleep", start_date, end_date)

    st.divider()

    # Trend tabs
    tab1, tab2, tab3 = st.tabs(["Steps Trend", "Heart Rate Trend", "Sleep Trend"])

    with tab1:
        if not steps_df.empty:
            # Add 7-day rolling average
            steps_df["rolling_avg"] = steps_df["total_steps"].rolling(window=CHART_CONFIG["rolling_window_short"], min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=steps_df["date"],
                y=steps_df["total_steps"],
                mode="lines",
                name="Daily Steps",
                line=dict(color=colors["steps"]["secondary"], width=1),
            ))
            fig.add_trace(go.Scatter(
                x=steps_df["date"],
                y=steps_df["rolling_avg"],
                mode="lines",
                name=f"{CHART_CONFIG['rolling_window_short']}-day Average",
                line=dict(color=colors["steps"]["primary"], width=2),
            ))
            # Goal line
            fig.add_hline(y=GOALS["steps_daily"], line_dash="dash", line_color=colors["chart"]["goal_line"],
                          annotation_text=f"Goal: {GOALS['steps_daily']:,}")

            fig.update_layout(
                title=f"Daily Steps with {CHART_CONFIG['rolling_window_short']}-Day Rolling Average",
                xaxis_title="Date",
                yaxis_title="Steps",
                hovermode="x unified",
                **layout_defaults,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No steps data available for this period.")

    with tab2:
        if not rhr_df.empty:
            rhr_df["rolling_avg"] = rhr_df["resting_hr"].rolling(window=CHART_CONFIG["rolling_window_short"], min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=rhr_df["date"],
                y=rhr_df["resting_hr"],
                mode="lines+markers",
                name="Resting HR",
                line=dict(color=colors["heart_rate"]["secondary"], width=1),
                marker=dict(size=4),
            ))
            fig.add_trace(go.Scatter(
                x=rhr_df["date"],
                y=rhr_df["rolling_avg"],
                mode="lines",
                name=f"{CHART_CONFIG['rolling_window_short']}-day Average",
                line=dict(color=colors["heart_rate"]["primary"], width=2),
            ))

            fig.update_layout(
                title=f"Resting Heart Rate with {CHART_CONFIG['rolling_window_short']}-Day Rolling Average",
                xaxis_title="Date",
                yaxis_title="BPM",
                hovermode="x unified",
                **layout_defaults,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No heart rate data available for this period.")

    with tab3:
        if not sleep_df.empty:
            sleep_df["rolling_avg"] = sleep_df["duration_hours"].rolling(window=CHART_CONFIG["rolling_window_short"], min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sleep_df["date"],
                y=sleep_df["duration_hours"],
                name="Sleep Duration",
                marker_color=colors["sleep"]["bar"],
                opacity=colors["sleep"]["bar_opacity"],
            ))
            fig.add_trace(go.Scatter(
                x=sleep_df["date"],
                y=sleep_df["rolling_avg"],
                mode="lines",
                name=f"{CHART_CONFIG['rolling_window_short']}-day Average",
                line=dict(color=colors["sleep"]["primary"], width=2),
            ))
            # Recommended sleep line
            fig.add_hline(y=GOALS["sleep_hours"], line_dash="dash", line_color=colors["sleep"]["goal_line"],
                          annotation_text=f"Recommended: {GOALS['sleep_hours']} hrs")

            fig.update_layout(
                title=f"Sleep Duration with {CHART_CONFIG['rolling_window_short']}-Day Rolling Average",
                xaxis_title="Date",
                yaxis_title="Hours",
                hovermode="x unified",
                **layout_defaults,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sleep data available for this period.")

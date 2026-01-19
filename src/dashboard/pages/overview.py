"""Overview page with KPIs and trends."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.storage import DuckDBManager
from src.config.settings import STEPS_GOAL


def render_overview(db: DuckDBManager, start_date, end_date):
    """Render the overview dashboard page."""
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
            recent_avg = steps_df.tail(7)["total_steps"].mean() if len(steps_df) >= 7 else avg_steps
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
            recent_rhr = rhr_df.tail(7)["resting_hr"].mean() if len(rhr_df) >= 7 else avg_rhr
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
            recent_sleep = sleep_df.tail(7)["duration_hours"].mean() if len(sleep_df) >= 7 else avg_sleep
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
            recent_eff = sleep_df.tail(7)["efficiency"].mean() if len(sleep_df) >= 7 else avg_efficiency
            delta = recent_eff - avg_efficiency
            st.metric(
                "Sleep Efficiency",
                f"{avg_efficiency:.0f}%",
                delta=f"{delta:+.0f}%" if delta != 0 else None,
            )
        else:
            st.metric("Sleep Efficiency", "N/A")

    st.divider()

    # Trend tabs
    tab1, tab2, tab3 = st.tabs(["Steps Trend", "Heart Rate Trend", "Sleep Trend"])

    with tab1:
        if not steps_df.empty:
            # Add 7-day rolling average
            steps_df["rolling_avg"] = steps_df["total_steps"].rolling(window=7, min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=steps_df["date"],
                y=steps_df["total_steps"],
                mode="lines",
                name="Daily Steps",
                line=dict(color="lightblue", width=1),
            ))
            fig.add_trace(go.Scatter(
                x=steps_df["date"],
                y=steps_df["rolling_avg"],
                mode="lines",
                name="7-day Average",
                line=dict(color="blue", width=2),
            ))
            # Goal line
            fig.add_hline(y=STEPS_GOAL, line_dash="dash", line_color="green",
                          annotation_text=f"Goal: {STEPS_GOAL:,}")

            fig.update_layout(
                title="Daily Steps with 7-Day Rolling Average",
                xaxis_title="Date",
                yaxis_title="Steps",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No steps data available for this period.")

    with tab2:
        if not rhr_df.empty:
            rhr_df["rolling_avg"] = rhr_df["resting_hr"].rolling(window=7, min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=rhr_df["date"],
                y=rhr_df["resting_hr"],
                mode="lines+markers",
                name="Resting HR",
                line=dict(color="lightcoral", width=1),
                marker=dict(size=4),
            ))
            fig.add_trace(go.Scatter(
                x=rhr_df["date"],
                y=rhr_df["rolling_avg"],
                mode="lines",
                name="7-day Average",
                line=dict(color="red", width=2),
            ))

            fig.update_layout(
                title="Resting Heart Rate with 7-Day Rolling Average",
                xaxis_title="Date",
                yaxis_title="BPM",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No heart rate data available for this period.")

    with tab3:
        if not sleep_df.empty:
            sleep_df["rolling_avg"] = sleep_df["duration_hours"].rolling(window=7, min_periods=1).mean()

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sleep_df["date"],
                y=sleep_df["duration_hours"],
                name="Sleep Duration",
                marker_color="mediumpurple",
                opacity=0.7,
            ))
            fig.add_trace(go.Scatter(
                x=sleep_df["date"],
                y=sleep_df["rolling_avg"],
                mode="lines",
                name="7-day Average",
                line=dict(color="purple", width=2),
            ))
            # Recommended sleep line
            fig.add_hline(y=8, line_dash="dash", line_color="green",
                          annotation_text="Recommended: 8 hrs")

            fig.update_layout(
                title="Sleep Duration with 7-Day Rolling Average",
                xaxis_title="Date",
                yaxis_title="Hours",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sleep data available for this period.")

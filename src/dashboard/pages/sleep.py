"""Sleep analysis page."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.storage import DuckDBManager
from src.dashboard.utils import add_csv_download


def render_sleep(db: DuckDBManager, start_date, end_date):
    """Render the sleep analysis page."""
    st.title("Sleep Analysis")
    st.caption(f"Showing data from {start_date} to {end_date}")

    # Get data
    sleep_df = db.get_sleep_sessions(start_date, end_date)

    if sleep_df.empty:
        st.warning("No sleep data available for the selected period.")
        return

    # Stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_duration = sleep_df["duration_hours"].mean()
        st.metric("Avg Duration", f"{avg_duration:.1f} hrs")

    with col2:
        avg_efficiency = sleep_df["efficiency"].mean()
        st.metric("Avg Efficiency", f"{avg_efficiency:.0f}%")

    with col3:
        # Only count stages sleep for deep/REM analysis
        stages_df = sleep_df[sleep_df["sleep_type"] == "stages"]
        if not stages_df.empty:
            avg_deep = stages_df["deep_minutes"].mean()
            st.metric("Avg Deep Sleep", f"{avg_deep:.0f} min")
        else:
            st.metric("Avg Deep Sleep", "N/A")

    with col4:
        if not stages_df.empty:
            avg_rem = stages_df["rem_minutes"].mean()
            st.metric("Avg REM Sleep", f"{avg_rem:.0f} min")
        else:
            st.metric("Avg REM Sleep", "N/A")

    st.divider()

    # CSV download
    add_csv_download(sleep_df, "sleep", start_date, end_date)

    # Duration trend
    st.subheader("Sleep Duration Trend")

    # Aggregation toggle
    agg_option = st.radio(
        "Aggregation",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
        key="sleep_aggregation",
    )

    sleep_df = sleep_df.copy()

    if agg_option == "Daily":
        plot_df = sleep_df.copy()
        plot_df["period"] = plot_df["date"]
        plot_df["rolling_avg"] = plot_df["duration_hours"].rolling(window=7, min_periods=1).mean()
        x_label = "Date"
    elif agg_option == "Weekly":
        sleep_df["week"] = pd.to_datetime(sleep_df["date"]).dt.to_period("W").dt.start_time
        plot_df = sleep_df.groupby("week").agg(
            duration_hours=("duration_hours", "mean"),
            efficiency=("efficiency", "mean"),
        ).reset_index()
        plot_df["period"] = plot_df["week"]
        x_label = "Week Starting"
    else:  # Monthly
        sleep_df["month"] = pd.to_datetime(sleep_df["date"]).dt.to_period("M").dt.start_time
        plot_df = sleep_df.groupby("month").agg(
            duration_hours=("duration_hours", "mean"),
            efficiency=("efficiency", "mean"),
        ).reset_index()
        plot_df["period"] = plot_df["month"]
        x_label = "Month"

    fig_duration = go.Figure()

    if agg_option == "Daily":
        fig_duration.add_trace(go.Bar(
            x=plot_df["period"],
            y=plot_df["duration_hours"],
            name="Duration",
            marker_color="mediumpurple",
            opacity=0.6,
        ))
        fig_duration.add_trace(go.Scatter(
            x=plot_df["period"],
            y=plot_df["rolling_avg"],
            mode="lines",
            name="7-day Average",
            line=dict(color="purple", width=2),
        ))
    else:
        fig_duration.add_trace(go.Bar(
            x=plot_df["period"],
            y=plot_df["duration_hours"],
            name=f"{agg_option} Average",
            marker_color="mediumpurple",
        ))

    # Recommended sleep range
    fig_duration.add_hline(y=8, line_dash="dash", line_color="green",
                           annotation_text="Recommended: 8 hrs")
    fig_duration.add_hline(y=7, line_dash="dot", line_color="orange",
                           annotation_text="Minimum: 7 hrs")

    fig_duration.update_layout(
        title=f"Sleep Duration ({agg_option})",
        xaxis_title=x_label,
        yaxis_title="Hours",
        hovermode="x unified",
        barmode="overlay",
    )
    st.plotly_chart(fig_duration, use_container_width=True)

    # Sleep stages analysis (only for stages-type sleep)
    stages_df = sleep_df[sleep_df["sleep_type"] == "stages"]

    if not stages_df.empty:
        st.subheader("Sleep Stages Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            # Stacked area chart of sleep stages
            stage_data = stages_df[["date", "wake_minutes", "light_minutes", "deep_minutes", "rem_minutes"]].copy()

            fig_stages = go.Figure()

            fig_stages.add_trace(go.Scatter(
                x=stage_data["date"],
                y=stage_data["deep_minutes"],
                mode="lines",
                name="Deep",
                stackgroup="one",
                fillcolor="rgba(75, 0, 130, 0.8)",
                line=dict(width=0),
            ))
            fig_stages.add_trace(go.Scatter(
                x=stage_data["date"],
                y=stage_data["rem_minutes"],
                mode="lines",
                name="REM",
                stackgroup="one",
                fillcolor="rgba(138, 43, 226, 0.8)",
                line=dict(width=0),
            ))
            fig_stages.add_trace(go.Scatter(
                x=stage_data["date"],
                y=stage_data["light_minutes"],
                mode="lines",
                name="Light",
                stackgroup="one",
                fillcolor="rgba(186, 85, 211, 0.6)",
                line=dict(width=0),
            ))
            fig_stages.add_trace(go.Scatter(
                x=stage_data["date"],
                y=stage_data["wake_minutes"],
                mode="lines",
                name="Awake",
                stackgroup="one",
                fillcolor="rgba(200, 200, 200, 0.6)",
                line=dict(width=0),
            ))

            fig_stages.update_layout(
                title="Sleep Stages Over Time",
                xaxis_title="Date",
                yaxis_title="Minutes",
                hovermode="x unified",
            )
            st.plotly_chart(fig_stages, use_container_width=True)

        with col2:
            # Average stage distribution pie chart
            avg_stages = {
                "Deep": stages_df["deep_minutes"].mean(),
                "REM": stages_df["rem_minutes"].mean(),
                "Light": stages_df["light_minutes"].mean(),
                "Awake": stages_df["wake_minutes"].mean(),
            }

            fig_pie = px.pie(
                values=list(avg_stages.values()),
                names=list(avg_stages.keys()),
                title="Average Sleep Stage Distribution",
                color_discrete_sequence=["indigo", "blueviolet", "mediumpurple", "lightgray"],
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Sleep quality metrics
    st.subheader("Sleep Quality Metrics")

    col1, col2 = st.columns(2)

    with col1:
        # Efficiency trend
        fig_eff = go.Figure()
        fig_eff.add_trace(go.Scatter(
            x=sleep_df["date"],
            y=sleep_df["efficiency"],
            mode="lines+markers",
            name="Efficiency",
            line=dict(color="teal"),
            marker=dict(size=4),
        ))
        fig_eff.add_hline(y=85, line_dash="dash", line_color="green",
                          annotation_text="Good: 85%")

        fig_eff.update_layout(
            title="Sleep Efficiency Trend",
            xaxis_title="Date",
            yaxis_title="Efficiency (%)",
            yaxis=dict(range=[0, 100]),
        )
        st.plotly_chart(fig_eff, use_container_width=True)

    with col2:
        # Sleep timing analysis
        sleep_df["start_hour"] = pd.to_datetime(sleep_df["start_time"]).dt.hour
        sleep_df["end_hour"] = pd.to_datetime(sleep_df["end_time"]).dt.hour

        # Adjust for times after midnight
        sleep_df["start_hour_adj"] = sleep_df["start_hour"].apply(
            lambda x: x - 24 if x < 12 else x
        )

        fig_timing = px.histogram(
            sleep_df,
            x="start_hour_adj",
            nbins=12,
            title="Bedtime Distribution",
            labels={"start_hour_adj": "Hour (24h format)"},
        )
        fig_timing.update_xaxes(
            tickvals=list(range(18, 30)),
            ticktext=[str(h % 24) for h in range(18, 30)],
        )
        st.plotly_chart(fig_timing, use_container_width=True)

    # Day of week analysis
    st.subheader("Sleep by Day of Week")

    sleep_df["day_of_week"] = pd.to_datetime(sleep_df["date"]).dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    dow_stats = sleep_df.groupby("day_of_week").agg(
        avg_duration=("duration_hours", "mean"),
        avg_efficiency=("efficiency", "mean"),
    ).reindex(day_order)

    col1, col2 = st.columns(2)

    with col1:
        fig_dow_dur = px.bar(
            x=day_order,
            y=dow_stats["avg_duration"].values,
            title="Average Sleep Duration by Day",
            labels={"x": "Day", "y": "Hours"},
        )
        fig_dow_dur.add_hline(y=8, line_dash="dash", line_color="green")
        st.plotly_chart(fig_dow_dur, use_container_width=True)

    with col2:
        fig_dow_eff = px.bar(
            x=day_order,
            y=dow_stats["avg_efficiency"].values,
            title="Average Sleep Efficiency by Day",
            labels={"x": "Day", "y": "Efficiency (%)"},
        )
        fig_dow_eff.add_hline(y=85, line_dash="dash", line_color="green")
        st.plotly_chart(fig_dow_eff, use_container_width=True)

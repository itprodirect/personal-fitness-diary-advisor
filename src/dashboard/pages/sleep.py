"""Sleep analysis page."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.storage import DuckDBManager
from src.config.settings import GOALS, CHART_CONFIG
from src.dashboard.utils import add_csv_download
from src.dashboard.theme import get_theme_colors, get_plotly_layout_defaults


def render_sleep(db: DuckDBManager, start_date, end_date, theme: str = "light"):
    """Render the sleep analysis page."""
    colors = get_theme_colors(theme)
    layout_defaults = get_plotly_layout_defaults(theme)

    st.title("Sleep Analysis")
    st.caption(f"Showing data from {start_date} to {end_date}")

    # Get data
    sleep_df = db.get_sleep_sessions(start_date, end_date)

    if sleep_df.empty:
        st.info("No sleep data available for the selected period.")
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
        plot_df["rolling_avg"] = plot_df["duration_hours"].rolling(window=CHART_CONFIG["rolling_window_short"], min_periods=1).mean()
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
            marker_color=colors["sleep"]["bar"],
            opacity=colors["sleep"]["bar_opacity"],
        ))
        fig_duration.add_trace(go.Scatter(
            x=plot_df["period"],
            y=plot_df["rolling_avg"],
            mode="lines",
            name=f"{CHART_CONFIG['rolling_window_short']}-day Average",
            line=dict(color=colors["sleep"]["primary"], width=2),
        ))
    else:
        fig_duration.add_trace(go.Bar(
            x=plot_df["period"],
            y=plot_df["duration_hours"],
            name=f"{agg_option} Average",
            marker_color=colors["sleep"]["bar"],
        ))

    # Recommended sleep range
    fig_duration.add_hline(y=GOALS["sleep_hours"], line_dash="dash", line_color=colors["sleep"]["goal_line"],
                           annotation_text=f"Recommended: {GOALS['sleep_hours']} hrs")
    fig_duration.add_hline(y=GOALS["sleep_hours_minimum"], line_dash="dot", line_color=colors["sleep"]["minimum_line"],
                           annotation_text=f"Minimum: {GOALS['sleep_hours_minimum']} hrs")

    fig_duration.update_layout(
        title=f"Sleep Duration ({agg_option})",
        xaxis_title=x_label,
        yaxis_title="Hours",
        hovermode="x unified",
        barmode="overlay",
        **layout_defaults,
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
                fillcolor=colors["sleep"]["deep"],
                line=dict(width=0),
            ))
            fig_stages.add_trace(go.Scatter(
                x=stage_data["date"],
                y=stage_data["rem_minutes"],
                mode="lines",
                name="REM",
                stackgroup="one",
                fillcolor=colors["sleep"]["rem"],
                line=dict(width=0),
            ))
            fig_stages.add_trace(go.Scatter(
                x=stage_data["date"],
                y=stage_data["light_minutes"],
                mode="lines",
                name="Light",
                stackgroup="one",
                fillcolor=colors["sleep"]["light"],
                line=dict(width=0),
            ))
            fig_stages.add_trace(go.Scatter(
                x=stage_data["date"],
                y=stage_data["wake_minutes"],
                mode="lines",
                name="Awake",
                stackgroup="one",
                fillcolor=colors["sleep"]["awake"],
                line=dict(width=0),
            ))

            fig_stages.update_layout(
                title="Sleep Stages Over Time",
                xaxis_title="Date",
                yaxis_title="Minutes",
                hovermode="x unified",
                **layout_defaults,
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
                template=layout_defaults["template"],
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
            line=dict(color=colors["sleep"]["efficiency"]),
            marker=dict(size=4),
        ))
        fig_eff.add_hline(y=GOALS["sleep_efficiency"], line_dash="dash", line_color=colors["sleep"]["goal_line"],
                          annotation_text=f"Good: {GOALS['sleep_efficiency']}%")

        fig_eff.update_layout(
            title="Sleep Efficiency Trend",
            xaxis_title="Date",
            yaxis_title="Efficiency (%)",
            yaxis=dict(range=[0, 100]),
            **layout_defaults,
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
            template=layout_defaults["template"],
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
            template=layout_defaults["template"],
        )
        fig_dow_dur.add_hline(y=GOALS["sleep_hours"], line_dash="dash", line_color=colors["sleep"]["goal_line"])
        st.plotly_chart(fig_dow_dur, use_container_width=True)

    with col2:
        fig_dow_eff = px.bar(
            x=day_order,
            y=dow_stats["avg_efficiency"].values,
            title="Average Sleep Efficiency by Day",
            labels={"x": "Day", "y": "Efficiency (%)"},
            template=layout_defaults["template"],
        )
        fig_dow_eff.add_hline(y=GOALS["sleep_efficiency"], line_dash="dash", line_color=colors["sleep"]["goal_line"])
        st.plotly_chart(fig_dow_eff, use_container_width=True)

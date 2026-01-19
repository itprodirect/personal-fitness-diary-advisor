"""Steps analysis page."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.storage import DuckDBManager
from src.config.settings import GOALS, CHART_CONFIG
from src.dashboard.utils import add_csv_download
from src.dashboard.theme import get_theme_colors, get_plotly_layout_defaults


def render_steps(db: DuckDBManager, start_date, end_date, theme: str = "light"):
    """Render the steps analysis page."""
    colors = get_theme_colors(theme)
    layout_defaults = get_plotly_layout_defaults(theme)

    st.title("Steps Analysis")
    st.caption(f"Showing data from {start_date} to {end_date}")

    # Get data
    steps_df = db.get_steps_daily(start_date, end_date)

    if steps_df.empty:
        st.info("No steps data available for the selected period.")
        return

    # Aggregation toggle
    agg_option = st.radio(
        "Aggregation",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
    )

    # Prepare data based on aggregation
    if agg_option == "Daily":
        plot_df = steps_df.copy()
        plot_df["period"] = plot_df["date"]
        x_label = "Date"
    elif agg_option == "Weekly":
        steps_df["week"] = pd.to_datetime(steps_df["date"]).dt.to_period("W").dt.start_time
        plot_df = steps_df.groupby("week").agg(
            total_steps=("total_steps", "sum"),
            avg_steps=("total_steps", "mean"),
            active_minutes=("active_minutes", "sum"),
        ).reset_index()
        plot_df["period"] = plot_df["week"]
        x_label = "Week Starting"
    else:  # Monthly
        steps_df["month"] = pd.to_datetime(steps_df["date"]).dt.to_period("M").dt.start_time
        plot_df = steps_df.groupby("month").agg(
            total_steps=("total_steps", "sum"),
            avg_steps=("total_steps", "mean"),
            active_minutes=("active_minutes", "sum"),
        ).reset_index()
        plot_df["period"] = plot_df["month"]
        x_label = "Month"

    # Stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Steps", f"{steps_df['total_steps'].sum():,.0f}")

    with col2:
        avg_daily = steps_df["total_steps"].mean()
        st.metric("Daily Average", f"{avg_daily:,.0f}")

    with col3:
        goal_days = (steps_df["total_steps"] >= GOALS["steps_daily"]).sum()
        total_days = len(steps_df)
        pct = (goal_days / total_days * 100) if total_days > 0 else 0
        st.metric("Days at Goal", f"{goal_days}/{total_days} ({pct:.0f}%)")

    with col4:
        st.metric("Best Day", f"{steps_df['total_steps'].max():,.0f}")

    st.divider()

    # CSV download
    add_csv_download(steps_df, "steps", start_date, end_date)

    # Main chart
    if agg_option == "Daily":
        # Bar chart with goal line
        fig = go.Figure()

        # Color bars based on goal achievement
        bar_colors = [colors["steps"]["goal_met"] if x >= GOALS["steps_daily"] else colors["steps"]["secondary"] for x in plot_df["total_steps"]]

        fig.add_trace(go.Bar(
            x=plot_df["period"],
            y=plot_df["total_steps"],
            marker_color=bar_colors,
            name="Steps",
            hovertemplate="%{x}<br>Steps: %{y:,.0f}<extra></extra>",
        ))

        # Goal line
        fig.add_hline(y=GOALS["steps_daily"], line_dash="dash", line_color=colors["steps"]["goal_line"],
                      annotation_text=f"Goal: {GOALS['steps_daily']:,}")

        fig.update_layout(
            title="Daily Steps",
            xaxis_title=x_label,
            yaxis_title="Steps",
            showlegend=False,
            **layout_defaults,
        )
    else:
        # Use average for weekly/monthly
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=plot_df["period"],
            y=plot_df["avg_steps"],
            marker_color=colors["steps"]["primary"],
            name="Avg Daily Steps",
            hovertemplate="%{x}<br>Avg: %{y:,.0f}<extra></extra>",
        ))

        fig.add_hline(y=GOALS["steps_daily"], line_dash="dash", line_color=colors["steps"]["goal_line"],
                      annotation_text=f"Goal: {GOALS['steps_daily']:,}")

        fig.update_layout(
            title=f"{agg_option} Average Daily Steps",
            xaxis_title=x_label,
            yaxis_title="Average Steps per Day",
            **layout_defaults,
        )

    st.plotly_chart(fig, use_container_width=True)

    # Distribution chart
    st.subheader("Steps Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig_hist = px.histogram(
            steps_df,
            x="total_steps",
            nbins=CHART_CONFIG["histogram_bins"],
            title="Distribution of Daily Steps",
            labels={"total_steps": "Steps"},
            template=layout_defaults["template"],
        )
        fig_hist.add_vline(x=GOALS["steps_daily"], line_dash="dash", line_color=colors["steps"]["goal_line"],
                           annotation_text=f"Goal: {GOALS['steps_daily']:,}")
        fig_hist.add_vline(x=avg_daily, line_dash="dot", line_color=colors["chart"]["average_line"],
                           annotation_text=f"Avg: {avg_daily:,.0f}")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Day of week analysis
        steps_df["day_of_week"] = pd.to_datetime(steps_df["date"]).dt.day_name()
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_avg = steps_df.groupby("day_of_week")["total_steps"].mean().reindex(day_order)

        fig_dow = px.bar(
            x=day_order,
            y=dow_avg.values,
            title="Average Steps by Day of Week",
            labels={"x": "Day", "y": "Average Steps"},
            template=layout_defaults["template"],
        )
        fig_dow.add_hline(y=GOALS["steps_daily"], line_dash="dash", line_color=colors["steps"]["goal_line"])
        st.plotly_chart(fig_dow, use_container_width=True)

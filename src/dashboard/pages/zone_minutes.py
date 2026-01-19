"""Zone minutes analysis page."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.storage import DuckDBManager
from src.config.settings import GOALS, CHART_CONFIG
from src.dashboard.utils import add_csv_download
from src.dashboard.theme import get_theme_colors, get_plotly_layout_defaults


def render_zone_minutes(db: DuckDBManager, start_date, end_date, theme: str = "light"):
    """Render the zone minutes analysis page."""
    colors = get_theme_colors(theme)
    layout_defaults = get_plotly_layout_defaults(theme)

    st.title("Active Zone Minutes")
    st.caption(f"Showing data from {start_date} to {end_date}")

    # Get data
    zone_df = db.get_zone_minutes_daily(start_date, end_date)

    if zone_df.empty:
        st.info("No zone minutes data available for the selected period.")
        return

    # Aggregation toggle
    agg_option = st.radio(
        "Aggregation",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
    )

    # Prepare data based on aggregation
    if agg_option == "Daily":
        plot_df = zone_df.copy()
        plot_df["period"] = plot_df["date"]
        x_label = "Date"
    elif agg_option == "Weekly":
        zone_df["week"] = pd.to_datetime(zone_df["date"]).dt.to_period("W").dt.start_time
        plot_df = zone_df.groupby("week").agg(
            fat_burn_minutes=("fat_burn_minutes", "sum"),
            cardio_minutes=("cardio_minutes", "sum"),
            peak_minutes=("peak_minutes", "sum"),
            out_of_range_minutes=("out_of_range_minutes", "sum"),
            total_active_minutes=("total_active_minutes", "sum"),
        ).reset_index()
        plot_df["period"] = plot_df["week"]
        x_label = "Week Starting"
    else:  # Monthly
        zone_df["month"] = pd.to_datetime(zone_df["date"]).dt.to_period("M").dt.start_time
        plot_df = zone_df.groupby("month").agg(
            fat_burn_minutes=("fat_burn_minutes", "sum"),
            cardio_minutes=("cardio_minutes", "sum"),
            peak_minutes=("peak_minutes", "sum"),
            out_of_range_minutes=("out_of_range_minutes", "sum"),
            total_active_minutes=("total_active_minutes", "sum"),
        ).reset_index()
        plot_df["period"] = plot_df["month"]
        x_label = "Month"

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_active = zone_df["total_active_minutes"].sum()
        st.metric("Total Active Zone Min", f"{total_active:,.0f}")

    with col2:
        avg_daily = zone_df["total_active_minutes"].mean()
        st.metric("Daily Average", f"{avg_daily:,.1f} min")

    with col3:
        avg_fat_burn = zone_df["fat_burn_minutes"].mean()
        st.metric("Avg Fat Burn", f"{avg_fat_burn:,.1f} min/day")

    with col4:
        avg_cardio_peak = zone_df["cardio_minutes"].mean() + zone_df["peak_minutes"].mean()
        st.metric("Avg Cardio + Peak", f"{avg_cardio_peak:,.1f} min/day")

    st.divider()

    # CSV download
    add_csv_download(zone_df, "zone_minutes", start_date, end_date)

    # Main stacked area chart
    st.subheader("Active Zone Minutes Over Time")

    fig = go.Figure()

    # Stack order: Peak (top), Cardio, Fat Burn (bottom)
    fig.add_trace(go.Scatter(
        x=plot_df["period"],
        y=plot_df["fat_burn_minutes"],
        mode="lines",
        name="Fat Burn",
        stackgroup="one",
        fillcolor=colors["zone_minutes"]["fat_burn"],
        line=dict(width=0),
        hovertemplate="%{y:,.0f} min<extra>Fat Burn</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=plot_df["period"],
        y=plot_df["cardio_minutes"],
        mode="lines",
        name="Cardio",
        stackgroup="one",
        fillcolor=colors["zone_minutes"]["cardio"],
        line=dict(width=0),
        hovertemplate="%{y:,.0f} min<extra>Cardio</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=plot_df["period"],
        y=plot_df["peak_minutes"],
        mode="lines",
        name="Peak",
        stackgroup="one",
        fillcolor=colors["zone_minutes"]["peak"],
        line=dict(width=0),
        hovertemplate="%{y:,.0f} min<extra>Peak</extra>",
    ))

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title="Minutes",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        **layout_defaults,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Zone breakdown charts
    st.subheader("Zone Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # Average zone distribution pie chart
        avg_zones = {
            "Fat Burn": zone_df["fat_burn_minutes"].mean(),
            "Cardio": zone_df["cardio_minutes"].mean(),
            "Peak": zone_df["peak_minutes"].mean(),
        }

        fig_pie = go.Figure(data=[go.Pie(
            labels=list(avg_zones.keys()),
            values=list(avg_zones.values()),
            marker_colors=[
                colors["zone_minutes"]["fat_burn_solid"],
                colors["zone_minutes"]["cardio_solid"],
                colors["zone_minutes"]["peak_solid"],
            ],
            hole=0.4,
        )])
        fig_pie.update_layout(
            title="Average Daily Zone Distribution",
            **layout_defaults,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Day of week analysis
        zone_df_copy = zone_df.copy()
        zone_df_copy["day_of_week"] = pd.to_datetime(zone_df_copy["date"]).dt.day_name()
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_avg = zone_df_copy.groupby("day_of_week")["total_active_minutes"].mean().reindex(day_order)

        fig_dow = go.Figure(data=[go.Bar(
            x=day_order,
            y=dow_avg.values,
            marker_color=colors["zone_minutes"]["dow_bar"],
        )])
        fig_dow.update_layout(
            title="Average Active Zone Minutes by Day of Week",
            xaxis_title="Day",
            yaxis_title="Minutes",
            **layout_defaults,
        )
        st.plotly_chart(fig_dow, use_container_width=True)

    # Trend analysis
    st.subheader("Trend Analysis")

    zone_df_trend = zone_df.copy()
    zone_df_trend["rolling_7d"] = zone_df_trend["total_active_minutes"].rolling(window=CHART_CONFIG["rolling_window_short"], min_periods=1).mean()
    zone_df_trend["rolling_30d"] = zone_df_trend["total_active_minutes"].rolling(window=CHART_CONFIG["rolling_window_long"], min_periods=1).mean()

    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=zone_df_trend["date"],
        y=zone_df_trend["total_active_minutes"],
        mode="markers",
        name="Daily",
        marker=dict(color=colors["zone_minutes"]["trend_daily"], size=4),
    ))
    fig_trend.add_trace(go.Scatter(
        x=zone_df_trend["date"],
        y=zone_df_trend["rolling_7d"],
        mode="lines",
        name=f"{CHART_CONFIG['rolling_window_short']}-day Average",
        line=dict(color=colors["zone_minutes"]["trend_7d"], width=2),
    ))
    fig_trend.add_trace(go.Scatter(
        x=zone_df_trend["date"],
        y=zone_df_trend["rolling_30d"],
        mode="lines",
        name=f"{CHART_CONFIG['rolling_window_long']}-day Average",
        line=dict(color=colors["zone_minutes"]["trend_30d"], width=2, dash="dash"),
    ))

    fig_trend.update_layout(
        title="Active Zone Minutes Trend",
        xaxis_title="Date",
        yaxis_title="Minutes",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        **layout_defaults,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

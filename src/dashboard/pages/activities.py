"""Activities (exercise log) analysis page."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.storage import DuckDBManager
from src.dashboard.utils import add_csv_download


def render_activities(db: DuckDBManager, start_date, end_date):
    """Render the activities analysis page."""
    st.title("Activity Log")
    st.caption(f"Showing data from {start_date} to {end_date}")

    # Get data
    activities_df = db.get_activities(start_date, end_date)

    if activities_df.empty:
        st.warning("No activity data available for the selected period.")
        return

    # Filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)

    with col1:
        # Activity type filter
        activity_names = sorted(activities_df["activity_name"].unique())
        selected_activities = st.multiselect(
            "Activity Type",
            options=activity_names,
            default=activity_names,
        )

    with col2:
        # Minimum duration filter
        min_duration = st.slider(
            "Minimum Duration (min)",
            min_value=0,
            max_value=int(activities_df["duration_minutes"].max()),
            value=0,
        )

    with col3:
        # Sort option
        sort_option = st.selectbox(
            "Sort By",
            ["Date (newest)", "Date (oldest)", "Duration", "Calories", "Distance"],
        )

    # Apply filters
    filtered_df = activities_df[
        (activities_df["activity_name"].isin(selected_activities)) &
        (activities_df["duration_minutes"] >= min_duration)
    ].copy()

    # Apply sorting
    if sort_option == "Date (newest)":
        filtered_df = filtered_df.sort_values("start_time", ascending=False)
    elif sort_option == "Date (oldest)":
        filtered_df = filtered_df.sort_values("start_time", ascending=True)
    elif sort_option == "Duration":
        filtered_df = filtered_df.sort_values("duration_minutes", ascending=False)
    elif sort_option == "Calories":
        filtered_df = filtered_df.sort_values("calories", ascending=False)
    elif sort_option == "Distance":
        filtered_df = filtered_df.sort_values("distance", ascending=False)

    st.divider()

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Activities", f"{len(filtered_df):,}")

    with col2:
        total_duration = filtered_df["duration_minutes"].sum()
        hours = int(total_duration // 60)
        mins = int(total_duration % 60)
        st.metric("Total Duration", f"{hours}h {mins}m")

    with col3:
        total_calories = filtered_df["calories"].sum()
        st.metric("Total Calories", f"{total_calories:,.0f}")

    with col4:
        total_distance = filtered_df["distance"].sum()
        st.metric("Total Distance", f"{total_distance:,.1f} mi")

    st.divider()

    # CSV download
    add_csv_download(filtered_df, "activities", start_date, end_date)

    # Activity table
    st.subheader(f"Activity Log ({len(filtered_df)} activities)")

    # Format for display
    display_df = filtered_df[
        ["date", "activity_name", "duration_minutes", "calories", "distance", "avg_heart_rate", "steps"]
    ].copy()
    display_df.columns = ["Date", "Activity", "Duration (min)", "Calories", "Distance (mi)", "Avg HR", "Steps"]
    display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.strftime("%Y-%m-%d")
    display_df["Duration (min)"] = display_df["Duration (min)"].round(1)
    display_df["Distance (mi)"] = display_df["Distance (mi)"].round(2)
    display_df["Avg HR"] = display_df["Avg HR"].astype(int)
    display_df["Steps"] = display_df["Steps"].astype(int)

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # Charts
    st.subheader("Activity Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Activity type breakdown
        activity_counts = filtered_df.groupby("activity_name").size().reset_index(name="count")
        activity_counts = activity_counts.sort_values("count", ascending=False).head(10)

        fig_types = px.bar(
            activity_counts,
            x="count",
            y="activity_name",
            orientation="h",
            title="Top Activities by Count",
            labels={"count": "Count", "activity_name": "Activity"},
        )
        fig_types.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_types, use_container_width=True)

    with col2:
        # Activity duration breakdown
        activity_duration = filtered_df.groupby("activity_name")["duration_minutes"].sum().reset_index()
        activity_duration = activity_duration.sort_values("duration_minutes", ascending=False).head(10)

        fig_duration = px.bar(
            activity_duration,
            x="duration_minutes",
            y="activity_name",
            orientation="h",
            title="Top Activities by Total Duration",
            labels={"duration_minutes": "Minutes", "activity_name": "Activity"},
        )
        fig_duration.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_duration, use_container_width=True)

    # Activities over time
    st.subheader("Activities Over Time")

    # Group by week
    time_df = filtered_df.copy()
    time_df["week"] = pd.to_datetime(time_df["date"]).dt.to_period("W").dt.start_time

    weekly_summary = time_df.groupby("week").agg(
        count=("logId", "count"),
        total_duration=("duration_minutes", "sum"),
        total_calories=("calories", "sum"),
    ).reset_index()

    fig_weekly = go.Figure()

    fig_weekly.add_trace(go.Bar(
        x=weekly_summary["week"],
        y=weekly_summary["count"],
        name="Activities",
        marker_color="steelblue",
        yaxis="y",
    ))

    fig_weekly.add_trace(go.Scatter(
        x=weekly_summary["week"],
        y=weekly_summary["total_duration"],
        mode="lines+markers",
        name="Duration (min)",
        line=dict(color="orange", width=2),
        yaxis="y2",
    ))

    fig_weekly.update_layout(
        title="Weekly Activity Summary",
        xaxis_title="Week",
        yaxis=dict(title="Number of Activities", side="left"),
        yaxis2=dict(title="Duration (minutes)", side="right", overlaying="y"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_weekly, use_container_width=True)

    # Day of week analysis
    st.subheader("Activity Patterns")

    col1, col2 = st.columns(2)

    with col1:
        time_df["day_of_week"] = pd.to_datetime(time_df["date"]).dt.day_name()
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_counts = time_df.groupby("day_of_week").size().reindex(day_order)

        fig_dow = px.bar(
            x=day_order,
            y=dow_counts.values,
            title="Activities by Day of Week",
            labels={"x": "Day", "y": "Count"},
        )
        st.plotly_chart(fig_dow, use_container_width=True)

    with col2:
        # Hour of day analysis
        time_df["hour"] = pd.to_datetime(time_df["start_time"]).dt.hour
        hour_counts = time_df.groupby("hour").size().reset_index(name="count")

        fig_hour = px.bar(
            hour_counts,
            x="hour",
            y="count",
            title="Activities by Hour of Day",
            labels={"hour": "Hour", "count": "Count"},
        )
        fig_hour.update_xaxes(tickmode="linear", tick0=0, dtick=2)
        st.plotly_chart(fig_hour, use_container_width=True)

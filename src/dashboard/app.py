"""Main Streamlit dashboard application."""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import PARQUET_PATH, DUCKDB_PATH, DEFAULT_DATE_RANGE_DAYS
from src.storage import DuckDBManager
from src.dashboard.theme import get_theme_css

# Page configuration
st.set_page_config(
    page_title="Personal Fitness Diary",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_db_manager():
    """Get cached DuckDB manager."""
    return DuckDBManager(DUCKDB_PATH, PARQUET_PATH)


def init_theme():
    """Initialize theme in session state."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"


def init_sidebar():
    """Initialize sidebar with global filters."""
    st.sidebar.title("Fitness Diary")

    db = get_db_manager()
    min_date, max_date = db.get_date_range()

    if min_date is None:
        st.sidebar.warning("No data found. Please run the pipeline first.")
        return None, None

    # Convert to datetime if needed
    if hasattr(min_date, "date"):
        min_date = min_date.date() if hasattr(min_date, "date") else min_date
        max_date = max_date.date() if hasattr(max_date, "date") else max_date

    # Date range filter
    st.sidebar.subheader("Date Range")

    # Quick select buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Last 30 days"):
            end = datetime.now().date()
            start = end - timedelta(days=30)
            st.session_state["start_date"] = max(start, min_date) if isinstance(min_date, type(start)) else start
            st.session_state["end_date"] = end
    with col2:
        if st.button("Last 90 days"):
            end = datetime.now().date()
            start = end - timedelta(days=90)
            st.session_state["start_date"] = max(start, min_date) if isinstance(min_date, type(start)) else start
            st.session_state["end_date"] = end

    col3, col4 = st.sidebar.columns(2)
    with col3:
        if st.button("Last year"):
            end = datetime.now().date()
            start = end - timedelta(days=365)
            st.session_state["start_date"] = max(start, min_date) if isinstance(min_date, type(start)) else start
            st.session_state["end_date"] = end
    with col4:
        if st.button("All time"):
            st.session_state["start_date"] = min_date
            st.session_state["end_date"] = max_date

    # Date pickers with defaults
    default_end = datetime.now().date()
    default_start = default_end - timedelta(days=DEFAULT_DATE_RANGE_DAYS)

    start_date = st.sidebar.date_input(
        "Start date",
        value=st.session_state.get("start_date", default_start),
        min_value=min_date,
        max_value=max_date,
        key="start_picker",
    )
    end_date = st.sidebar.date_input(
        "End date",
        value=st.session_state.get("end_date", default_end),
        min_value=min_date,
        max_value=max_date,
        key="end_picker",
    )

    st.sidebar.divider()
    st.sidebar.caption(f"Data available: {min_date} to {max_date}")

    # Preferences expander
    with st.sidebar.expander("Preferences"):
        # Theme selection
        theme_options = ["Light", "Dark"]
        current_theme = st.session_state.get("theme", "light").capitalize()
        theme_index = theme_options.index(current_theme) if current_theme in theme_options else 0

        selected_theme = st.selectbox(
            "Theme",
            theme_options,
            index=theme_index,
            key="theme_selector",
        )
        st.session_state["theme"] = selected_theme.lower()

        # Default date range selection
        date_range_options = ["30 days", "90 days", "1 year", "All time"]
        st.selectbox(
            "Default Date Range",
            date_range_options,
            index=0,
            key="default_range_selector",
        )

    return start_date, end_date


def main():
    """Main dashboard entry point."""
    # Initialize theme
    init_theme()

    # Initialize sidebar and get date range
    start_date, end_date = init_sidebar()

    if start_date is None:
        st.error("No data available. Please run the ETL pipeline first:")
        st.code("python scripts/run_pipeline.py")
        return

    # Store dates in session state for pages
    st.session_state["filter_start"] = start_date
    st.session_state["filter_end"] = end_date

    # Get current theme and apply CSS
    theme = st.session_state.get("theme", "light")
    theme_css = get_theme_css(theme)
    if theme_css:
        st.markdown(theme_css, unsafe_allow_html=True)

    # Navigation
    page = st.sidebar.radio(
        "Navigate to:",
        ["Overview", "Steps", "Heart Rate", "Sleep", "Zone Minutes", "Activities", "Data Quality"],
        label_visibility="collapsed",
    )

    # Import and render pages
    if page == "Overview":
        from src.dashboard.pages.overview import render_overview
        render_overview(get_db_manager(), start_date, end_date, theme)
    elif page == "Steps":
        from src.dashboard.pages.steps import render_steps
        render_steps(get_db_manager(), start_date, end_date, theme)
    elif page == "Heart Rate":
        from src.dashboard.pages.heart_rate import render_heart_rate
        render_heart_rate(get_db_manager(), start_date, end_date, theme)
    elif page == "Sleep":
        from src.dashboard.pages.sleep import render_sleep
        render_sleep(get_db_manager(), start_date, end_date, theme)
    elif page == "Zone Minutes":
        from src.dashboard.pages.zone_minutes import render_zone_minutes
        render_zone_minutes(get_db_manager(), start_date, end_date, theme)
    elif page == "Activities":
        from src.dashboard.pages.activities import render_activities
        render_activities(get_db_manager(), start_date, end_date, theme)
    elif page == "Data Quality":
        from src.dashboard.pages.data_quality import render_data_quality
        render_data_quality(get_db_manager(), theme)


if __name__ == "__main__":
    main()

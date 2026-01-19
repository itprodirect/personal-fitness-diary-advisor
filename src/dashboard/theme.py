"""Centralized color themes and Plotly templates for the dashboard."""

# Light theme color palette
LIGHT_THEME = {
    # Steps colors
    "steps": {
        "primary": "#4A90D9",
        "secondary": "lightblue",
        "goal_met": "#28A745",
        "goal_line": "#DC3545",
    },
    # Heart rate colors
    "heart_rate": {
        "primary": "#DC3545",
        "secondary": "lightcoral",
        "range_fill": "rgba(255, 0, 0, 0.1)",
        "daily_range_fill": "rgba(255, 0, 0, 0.2)",
        "trend_7d": "red",
        "trend_30d": "darkred",
    },
    # Sleep colors
    "sleep": {
        "primary": "#9B59B6",
        "bar": "mediumpurple",
        "bar_opacity": 0.6,
        "deep": "rgba(75, 0, 130, 0.8)",
        "rem": "rgba(138, 43, 226, 0.8)",
        "light": "rgba(186, 85, 211, 0.6)",
        "awake": "rgba(200, 200, 200, 0.6)",
        "efficiency": "teal",
        "goal_line": "#28A745",
        "minimum_line": "orange",
    },
    # Zone minutes colors
    "zone_minutes": {
        "fat_burn": "rgba(255, 193, 7, 0.7)",
        "fat_burn_solid": "#FFC107",
        "cardio": "rgba(255, 87, 34, 0.8)",
        "cardio_solid": "#FF5722",
        "peak": "rgba(183, 28, 28, 0.9)",
        "peak_solid": "#B71C1C",
        "trend_daily": "lightcoral",
        "trend_7d": "orangered",
        "trend_30d": "darkred",
        "dow_bar": "coral",
    },
    # Activities colors
    "activities": {
        "primary": "steelblue",
        "secondary": "orange",
    },
    # General chart colors
    "chart": {
        "goal_line": "#28A745",
        "average_line": "green",
        "background": "#FFFFFF",
        "text": "#262730",
        "grid": "#E0E0E0",
    },
    # Plotly template name
    "plotly_template": "plotly_white",
}

# Dark theme color palette
DARK_THEME = {
    # Steps colors
    "steps": {
        "primary": "#6BB3F0",
        "secondary": "#4A90D9",
        "goal_met": "#48D068",
        "goal_line": "#FF6B6B",
    },
    # Heart rate colors
    "heart_rate": {
        "primary": "#FF6B6B",
        "secondary": "#FF9999",
        "range_fill": "rgba(255, 100, 100, 0.15)",
        "daily_range_fill": "rgba(255, 100, 100, 0.25)",
        "trend_7d": "#FF6B6B",
        "trend_30d": "#CC5555",
    },
    # Sleep colors
    "sleep": {
        "primary": "#BB86FC",
        "bar": "#9B6FD9",
        "bar_opacity": 0.7,
        "deep": "rgba(100, 50, 150, 0.85)",
        "rem": "rgba(150, 80, 200, 0.85)",
        "light": "rgba(180, 120, 220, 0.7)",
        "awake": "rgba(150, 150, 150, 0.6)",
        "efficiency": "#03DAC6",
        "goal_line": "#48D068",
        "minimum_line": "#FFB74D",
    },
    # Zone minutes colors
    "zone_minutes": {
        "fat_burn": "rgba(255, 213, 79, 0.75)",
        "fat_burn_solid": "#FFD54F",
        "cardio": "rgba(255, 112, 67, 0.85)",
        "cardio_solid": "#FF7043",
        "peak": "rgba(229, 57, 53, 0.9)",
        "peak_solid": "#E53935",
        "trend_daily": "#FF9999",
        "trend_7d": "#FF7043",
        "trend_30d": "#E53935",
        "dow_bar": "#FF8A65",
    },
    # Activities colors
    "activities": {
        "primary": "#64B5F6",
        "secondary": "#FFB74D",
    },
    # General chart colors
    "chart": {
        "goal_line": "#48D068",
        "average_line": "#66BB6A",
        "background": "#1E1E1E",
        "text": "#E0E0E0",
        "grid": "#404040",
    },
    # Plotly template name
    "plotly_template": "plotly_dark",
}

# Theme registry
THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}


def get_theme_colors(theme_name: str = "light") -> dict:
    """Get color palette for the specified theme.

    Args:
        theme_name: Either "light" or "dark"

    Returns:
        Dictionary containing all color definitions for the theme
    """
    return THEMES.get(theme_name.lower(), LIGHT_THEME)


def get_plotly_template(theme_name: str = "light") -> str:
    """Get Plotly template name for the specified theme.

    Args:
        theme_name: Either "light" or "dark"

    Returns:
        Plotly template name string
    """
    theme = get_theme_colors(theme_name)
    return theme.get("plotly_template", "plotly_white")


def get_plotly_layout_defaults(theme_name: str = "light") -> dict:
    """Get default Plotly layout settings for the specified theme.

    Args:
        theme_name: Either "light" or "dark"

    Returns:
        Dictionary of Plotly layout settings
    """
    theme = get_theme_colors(theme_name)
    return {
        "template": theme["plotly_template"],
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
    }


def get_theme_css(theme_name: str = "light") -> str:
    """Get CSS styles for the specified theme.

    Args:
        theme_name: Either "light" or "dark"

    Returns:
        CSS string to inject into Streamlit
    """
    if theme_name.lower() == "dark":
        return """
        <style>
        /* Dark theme overrides */
        .stApp {
            background-color: #1E1E1E;
            color: #E0E0E0;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #262626;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            color: #E0E0E0;
        }

        /* Headers */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #FFFFFF;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #FFFFFF;
        }

        [data-testid="stMetricLabel"] {
            color: #B0B0B0;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #262626;
        }

        .stTabs [data-baseweb="tab"] {
            color: #E0E0E0;
        }

        /* Expander */
        [data-testid="stExpander"] {
            background-color: #262626;
            border-color: #404040;
        }

        /* Divider */
        hr {
            border-color: #404040;
        }

        /* Dataframe */
        .stDataFrame {
            background-color: #262626;
        }

        /* Caption */
        .stCaption {
            color: #909090;
        }

        /* Radio buttons and selectbox */
        .stRadio > div, .stSelectbox > div {
            color: #E0E0E0;
        }

        /* Info/Warning/Error boxes */
        .stAlert {
            background-color: #2D2D2D;
        }

        /* Code blocks */
        .stCodeBlock {
            background-color: #2D2D2D;
        }
        </style>
        """
    else:
        # Light theme - return empty (use Streamlit defaults)
        return ""

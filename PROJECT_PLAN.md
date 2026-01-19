# Personal Fitness Diary Advisor - Project Plan

## Vision
A private, local-first health analytics platform that consolidates Fitbit data with future integrations (nutrition, stretching, medical records) into a unified personal health dashboard. Designed for extensibility and long-term use.

---

## Architecture Decisions

### Core Stack (Locked In)
| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Language** | Python 3.11+ | Ecosystem, your familiarity |
| **Data Processing** | Pandas + PyArrow | Mature, well-documented |
| **Analytics DB** | DuckDB | SQL interface, blazing fast on Parquet, embeddable |
| **Storage Format** | Parquet | Columnar, compressed, schema-preserving |
| **Frontend** | Streamlit | Fastest path to interactive dashboards |
| **Testing** | pytest | Standard, simple |
| **Config** | TOML / python-dotenv | Human-readable, no YAML complexity |

### Why This Stack for Long-Term Extensibility

1. **DuckDB + Parquet** creates a "data lakehouse" pattern locally:
   - Each data source (Fitbit, nutrition, stretching) becomes its own Parquet dataset
   - DuckDB queries across them with SQL JOINs - no ETL into a single table
   - Adding new sources = adding new Parquet files + new ETL script
   - Schema evolution is easy (add columns, DuckDB handles nulls)

2. **Modular ETL Design**:
   - Each data source gets its own loader: `etl/loaders/fitbit.py`, `etl/loaders/nutrition.py`
   - Common interface: `load(source_path) -> DataFrame`
   - Central orchestrator: `etl/pipeline.py` calls loaders and writes Parquet

3. **Streamlit for MVP, Option to Upgrade Later**:
   - Fast iteration now
   - If you outgrow it, the Parquet + DuckDB backend works with any frontend (Dash, React, etc.)

---

## Data Model (Extensible Schema)

### Core Tables (Sprint 1 - Fitbit)

```
daily_summary
├── date (DATE, PK)
├── steps_total (INT)
├── active_minutes (INT)
├── calories_burned (INT)
├── distance_km (FLOAT)
├── floors (INT)
├── resting_hr (INT)
├── sleep_duration_min (INT)
├── sleep_score (INT, nullable)
├── deep_sleep_min (INT)
├── rem_sleep_min (INT)
├── light_sleep_min (INT)
├── awake_min (INT)
├── zone_fat_burn_min (INT)
├── zone_cardio_min (INT)
├── zone_peak_min (INT)
└── data_source (VARCHAR) = 'fitbit'

heart_rate_intraday
├── timestamp (TIMESTAMP, PK)
├── bpm (INT)
├── confidence (INT, nullable)
└── data_source (VARCHAR) = 'fitbit'

sleep_stages
├── date (DATE)
├── start_time (TIMESTAMP)
├── end_time (TIMESTAMP)
├── stage (VARCHAR) - 'deep', 'rem', 'light', 'awake'
├── duration_min (INT)
└── data_source (VARCHAR) = 'fitbit'

activities
├── date (DATE)
├── activity_id (VARCHAR, PK)
├── activity_type (VARCHAR)
├── start_time (TIMESTAMP)
├── duration_min (INT)
├── calories (INT)
├── avg_hr (INT, nullable)
├── distance_km (FLOAT, nullable)
└── data_source (VARCHAR) = 'fitbit'
```

### Future Tables (Sprint 3+)

```
nutrition_log
├── date (DATE)
├── meal_type (VARCHAR) - 'breakfast', 'lunch', 'dinner', 'snack'
├── food_item (VARCHAR)
├── calories (INT)
├── protein_g (FLOAT)
├── carbs_g (FLOAT)
├── fat_g (FLOAT)
├── fiber_g (FLOAT)
├── notes (TEXT)
└── data_source (VARCHAR) - 'manual', 'myfitnesspal', 'cronometer'

stretching_log
├── date (DATE)
├── session_id (VARCHAR, PK)
├── routine_name (VARCHAR)
├── duration_min (INT)
├── body_areas (VARCHAR[]) - ['hamstrings', 'shoulders', 'back']
├── notes (TEXT)
└── data_source (VARCHAR) = 'manual'

medical_records
├── date (DATE)
├── record_type (VARCHAR) - 'lab_result', 'vitals', 'diagnosis', 'medication'
├── metric_name (VARCHAR)
├── value (VARCHAR)
├── unit (VARCHAR)
├── provider (VARCHAR, nullable)
├── notes (TEXT)
└── data_source (VARCHAR)

body_measurements
├── date (DATE)
├── weight_kg (FLOAT)
├── body_fat_pct (FLOAT, nullable)
├── muscle_mass_kg (FLOAT, nullable)
├── bmi (FLOAT, nullable)
└── data_source (VARCHAR) - 'fitbit', 'manual', 'withings'
```

### Key Design Principle: `data_source` Column
Every table has a `data_source` column. This enables:
- Tracking where data came from
- Handling duplicates across sources
- Filtering by source in queries
- Auditing data lineage

---

## Folder Structure

```
personal-fitness-diary-advisor/
├── app.py                      # Streamlit entry point
├── config.toml                 # App configuration
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── fitbit/             # Your Fitbit export (gitignored)
│   ├── processed/              # Parquet files (gitignored)
│   │   ├── daily_summary.parquet
│   │   ├── heart_rate.parquet
│   │   ├── sleep_stages.parquet
│   │   └── activities.parquet
│   └── sample/                 # Synthetic test data (committed)
│       └── fitbit/
│
├── etl/
│   ├── __init__.py
│   ├── pipeline.py             # Main orchestrator
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract loader interface
│   │   ├── fitbit.py           # Fitbit-specific parsing
│   │   └── manual.py           # For future manual entries
│   └── utils.py                # Date parsing, file discovery
│
├── analytics/
│   ├── __init__.py
│   ├── queries.py              # DuckDB query functions
│   └── calculations.py         # Derived metrics, rolling averages
│
├── ui/
│   ├── __init__.py
│   ├── components.py           # Reusable Streamlit components
│   ├── pages/
│   │   ├── dashboard.py        # Main dashboard
│   │   ├── sleep.py            # Sleep deep-dive
│   │   ├── heart.py            # HR analysis
│   │   └── settings.py         # Config/data management
│   └── styles.py               # Custom CSS
│
├── tests/
│   ├── __init__.py
│   ├── test_etl.py
│   ├── test_queries.py
│   └── conftest.py             # Pytest fixtures
│
├── logs/
│   └── etl.log
│
└── notebooks/                  # Exploration (optional)
    └── explore.sql
```

---

## Sprint Plan

### Sprint 1: Foundation (MVP) - ~4-6 hours
**Goal**: Load Fitbit data, display core metrics in Streamlit

**Deliverables**:
1. ✅ ETL pipeline that processes Fitbit export → Parquet
2. ✅ Daily summary aggregation
3. ✅ Streamlit dashboard with:
   - Data status panel
   - Date range selector
   - Steps chart (daily + 7-day rolling avg)
   - Resting HR trend
   - Sleep duration/stages visualization
4. ✅ Basic tests with synthetic sample data
5. ✅ README with setup instructions

**Acceptance Criteria**:
- `python -m etl.pipeline --source data/raw/fitbit` creates Parquet files
- `streamlit run app.py` shows working dashboard
- Tests pass: `pytest tests/`

---

### Sprint 2: Analytics & Polish - ~3-4 hours
**Goal**: Deeper insights, better UX

**Deliverables**:
1. Zone minutes visualization (fat burn / cardio / peak)
2. Activity log table with filtering
3. Sleep score trend (if available in your data)
4. Weekly/monthly summary views
5. CSV export functionality
6. Improved error handling & logging
7. Dark/light theme toggle

---

### Sprint 3: Manual Data Entry - ~3-4 hours
**Goal**: Add data that Fitbit doesn't capture

**Deliverables**:
1. Stretching log entry form
2. Nutrition log entry form (simple: meal, calories, protein, notes)
3. Manual weight/measurement entry
4. SQLite for manual entries (or append to Parquet)
5. Combined views showing all data sources

---

### Sprint 4: Correlations & Insights - ~4-5 hours
**Goal**: Find patterns across metrics

**Deliverables**:
1. Correlation matrix (sleep vs steps, HR vs activity, etc.)
2. "Best day" / "Worst day" analysis
3. Trend detection (improving/declining metrics)
4. Personal records tracking
5. Weekly email/report generation (optional)

---

### Sprint 5+: Advanced Features
- Medical records integration (PDF parsing or manual entry)
- Goal setting and tracking
- Predictive insights (ML-based)
- Mobile-friendly PWA wrapper
- Multi-device sync (if desired)
- Integration with other services (Strava, MyFitnessPal API, etc.)

---

## Fitbit Data Structure Reference

Based on typical Google Takeout Fitbit exports, expect this structure:

```
Fitbit/
├── Global Export Data/
│   ├── heart_rate-YYYY-MM-DD.json      # Intraday HR (1-min resolution)
│   ├── steps-YYYY-MM-DD.json           # Intraday steps
│   ├── sleep-YYYY-MM-DD.json           # Sleep sessions with stages
│   ├── exercise-YYYY-MM-DD.json        # Logged activities
│   ├── altitude-YYYY-MM-DD.json        # Floors/elevation
│   ├── calories-YYYY-MM-DD.json        # Calorie burn
│   ├── distance-YYYY-MM-DD.json        # Distance traveled
│   ├── active_minutes-YYYY-MM-DD.json  # Zone minutes
│   └── ...
├── Physical Activity/
│   ├── steps.csv                       # Daily step totals
│   ├── calories.csv                    # Daily calorie totals
│   └── ...
├── Sleep/
│   └── sleep_score.csv                 # Sleep scores (if available)
└── ...
```

**Important**: The exact structure varies by:
- How long you've had Fitbit
- Which Fitbit device(s) you've used
- When you exported (format has changed over time)
- What features you have (Premium vs free)

**This is why data discovery is Step 1 in Claude Code.**

---

## Configuration Design

```toml
# config.toml

[paths]
raw_data = "data/raw"
processed_data = "data/processed"
logs = "logs"

[fitbit]
timezone = "America/New_York"  # Your local timezone
include_intraday_hr = true     # Can disable if too much data

[dashboard]
default_date_range_days = 30
theme = "dark"

[features]
enable_manual_entry = false    # Enable in Sprint 3
enable_nutrition = false
enable_stretching = false
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Fitbit export format varies | Data discovery first; flexible parsers with fallbacks |
| Large data volumes (years of HR data) | Lazy loading, date-range filtering, optional intraday |
| Schema changes in future sprints | DuckDB handles schema evolution; Parquet is append-friendly |
| Streamlit limitations | Clean separation of UI/analytics; can swap frontend later |
| Data privacy | All local; .gitignore raw data; no cloud dependencies |

---

## Next Steps

1. **Run data discovery in Claude Code** (see CLAUDE_CODE_PROMPT.md)
2. Review discovered schema, adjust ETL design if needed
3. Build Sprint 1
4. Push to GitHub
5. Iterate!

---

## Notes for Future Self

- Keep raw Fitbit export untouched (read-only source of truth)
- Parquet files are the "processed" layer - can always regenerate from raw
- Manual entries go to SQLite (easier for CRUD operations)
- DuckDB queries across Parquet + SQLite seamlessly
- Test with sample data; never commit real health data to GitHub

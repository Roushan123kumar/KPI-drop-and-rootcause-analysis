# 📊 KPI Intelligence System — Drop Detection Dashboard

> A full-stack business intelligence platform built with Python and Streamlit that monitors KPIs in real time, detects performance drops, identifies root causes, and sends automated alerts.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Dataset Details](#5-dataset-details)
6. [System Architecture](#6-system-architecture)
7. [Module-by-Module Breakdown](#7-module-by-module-breakdown)
   - [data_preparation.py](#71-data_preparationpy)
   - [kpi_engine.py](#72-kpi_enginepy)
   - [drop_detection.py](#73-drop_detectionpy)
   - [comparison_engine.py](#74-comparison_enginepy)
   - [root_cause.py](#75-root_causepy)
   - [alert_engine.py](#76-alert_enginepy)
   - [executive_summary.py](#77-executive_summarypy)
   - [simulation_engine.py](#78-simulation_enginepy)
   - [audit_logger.py](#79-audit_loggerpy)
8. [Dashboard Pages & Sections](#8-dashboard-pages--sections)
9. [KPI Calculations — All Formulas](#9-kpi-calculations--all-formulas)
10. [Drop Detection Logic](#10-drop-detection-logic)
11. [Root Cause Analysis](#11-root-cause-analysis)
12. [Alert System](#12-alert-system)
13. [Role-Based Access Control](#13-role-based-access-control)
14. [Live Simulation Engine](#14-live-simulation-engine)
15. [Animated KPI Playback](#15-animated-kpi-playback)
16. [Visualizations Reference](#16-visualizations-reference)
17. [Installation & Setup](#17-installation--setup)
18. [How to Run](#18-how-to-run)
19. [How to Upload Your Own Data](#19-how-to-upload-your-own-data)
20. [Configuration & Thresholds](#20-configuration--thresholds)

---

## 1. Project Overview

The **KPI Intelligence System** is a multi-page Streamlit web application designed for business analysts, data scientists, and managers who want to track sales performance, detect KPI drops automatically, understand the root causes of those drops, and receive alerts before small problems become big ones.

The system operates in two modes:

- **Historical Mode** — analyses existing order data month by month, highlights drop periods, and provides root cause breakdowns by region, category, segment, and product.
- **Live Simulation Mode** — continuously generates synthetic new orders and recalculates all KPIs in real time, simulating what a live production feed would look like.

The platform is designed to be flexible: it accepts the default dataset or any custom CSV/Excel file uploaded by an Admin user. It handles messy column names, mixed date formats, and missing columns automatically.

---

## 2. Key Features

| Feature | Description |
|---|---|
| 📋 Executive Summary | One-screen health overview with status colour, metrics, top region/category, and root cause |
| 📊 Historical Comparison | Daily, weekly, and monthly sales comparisons with drop detection |
| 🔔 Real-Time Alerts | Triggered alerts when KPIs cross configurable thresholds |
| 📧 Email Alerts | Admin-only email dispatch via SMTP when drops are detected |
| 🎯 Threshold Table | Side-by-side comparison of each KPI vs its target threshold |
| 📈 Trend Charts | Monthly Sales & Profit line charts with full history |
| 📹 KPI Playback | Animated stock-market-style chart that builds month by month |
| 📊 Dashboard Viz | Bar charts, area charts, donut charts, scatter plots with drop highlights |
| 🔍 Advanced Analytics | Sub-category drops, region-wise performance, segment analysis |
| 🚚 Shipping Analysis | Scatter plot with linear regression trend for shipping vs sales correlation |
| 🎲 Live Simulation | Real-time order injection with live KPI recalculation (Admin/Analyst only) |
| 🔐 Role-Based Access | Three roles: Admin, Analyst, Viewer — each with different permissions |
| 📝 Audit Logging | All events logged with username, action, and timestamp |

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Web UI, interactive widgets, layout |
| Data Processing | Pandas | Data loading, grouping, aggregation |
| Numerical Computing | NumPy | Array operations, random data generation, polyfit |
| Visualisation | Matplotlib | All charts and graphs |
| Email | smtplib (Python stdlib) | SMTP email alerts |
| Language | Python 3.13 | Core application language |
| Data Format | CSV / Excel (.xlsx, .xls) | Input data formats |
| State Management | Streamlit Session State | Persistent variables across reruns |
| Caching | `@st.cache_data` | Prevents reloading data on every interaction |

---

## 4. Project Structure

```
Main_KPI/
│
├── app.py                        # Entry point — login page and navigation
│
├── pages/
│   └── 1_Live_Dashboard.py       # Main dashboard page (all sections)
│
├── src/
│   ├── data_preparation.py       # CSV loading, column fixing, feature engineering
│   ├── kpi_engine.py             # Monthly KPI calculation
│   ├── drop_detection.py         # KPI drop identification
│   ├── comparison_engine.py      # Daily/weekly/monthly comparisons
│   ├── root_cause.py             # Root cause analysis by dimension
│   ├── alert_engine.py           # Email alert dispatch
│   ├── executive_summary.py      # High-level business summary generation
│   ├── simulation_engine.py      # Fake order generation for live simulation
│   └── audit_logger.py           # Event logging
│
└── data/
    └── train_prepared.csv        # Default dataset
```

---

## 5. Dataset Details

### Default Dataset

The system ships with `train_prepared.csv`, a retail order dataset modelled on the classic Superstore sales structure.

### Raw Input Columns

| Column | Type | Description |
|---|---|---|
| `order_id` | String | Unique identifier for each order (e.g., CA-2017-152156) |
| `order_date` | Date | Date the order was placed |
| `ship_date` | Date | Date the order was shipped |
| `ship_mode` | String | Shipping method (Second Class, Standard Class, etc.) |
| `customer_id` | String | Unique customer identifier |
| `customer_name` | String | Customer full name |
| `segment` | String | Customer segment: Consumer, Corporate, Home Office |
| `country` | String | Country of order |
| `city` | String | City of delivery |
| `state` | String | State of delivery |
| `postal_code` | Float | ZIP/postal code |
| `region` | String | Geographic region: East, West, South, Central |
| `product_id` | String | Unique product identifier |
| `category` | String | Product category: Furniture, Technology, Office Supplies |
| `sub_category` | String | Product sub-category (e.g., Chairs, Phones, Binders) |
| `product_name` | String | Full product name |
| `sales` | Float | Revenue from the order (USD) |
| `profit` | Float | Profit from the order (USD) |
| `quantity` | Integer | Number of units ordered |
| `discount` | Float | Discount applied (0.0 to 1.0) |

### Engineered Columns (added by `data_preparation.py`)

| Column | Formula | Description |
|---|---|---|
| `shipping_days` | `ship_date - order_date` | Days taken to ship |
| `cost` | `sales - profit` | Cost of goods sold |
| `profit_margin_%` | `(profit / sales) × 100` | Percentage margin per order |
| `year_month` | `order_date.dt.to_period("M")` | Year-Month period for grouping |
| `orders` | `groupby(order_date).size()` | Count of orders per day |

### Accepted CSV Format for Custom Uploads

The system accepts CSV or Excel files with flexible column naming. It automatically handles:

- Column names with spaces or hyphens (converted to underscores)
- Mixed case (converted to lowercase)
- Alternative column names such as `Date` → `order_date`, `Revenue` → `sales`, `Net Profit` → `profit`
- Mixed date formats (e.g., `2024-01-15` and `15-01-2024` in the same column)

---

## 6. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     app.py (Login)                       │
│   - Username / Password authentication                   │
│   - Session state: logged_in, role, username             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              1_Live_Dashboard.py                         │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │DataPreparation│   │ KPIEngine    │                   │
│  │ - load CSV    │──▶│ - monthly    │                   │
│  │ - clean cols  │   │   aggregation│                   │
│  │ - engineer    │   └──────┬───────┘                   │
│  │   features    │          │                            │
│  └──────────────┘          ▼                            │
│                    ┌──────────────┐                      │
│                    │DropDetector  │                      │
│                    │ - detect     │                      │
│                    │   drops      │                      │
│                    └──────┬───────┘                      │
│                           │                              │
│              ┌────────────┼────────────┐                 │
│              ▼            ▼            ▼                 │
│   ┌──────────────┐ ┌──────────┐ ┌──────────────┐        │
│   │RootCause     │ │Alert     │ │Executive     │        │
│   │Analyzer      │ │Engine    │ │Summary       │        │
│   │- region      │ │- email   │ │- status      │        │
│   │- category    │ │  alerts  │ │- top KPIs    │        │
│   │- segment     │ └──────────┘ └──────────────┘        │
│   └──────────────┘                                       │
│                                                          │
│   ┌──────────────┐   ┌────────────────┐                 │
│   │Comparison    │   │Simulation      │                 │
│   │Engine        │   │Engine          │                 │
│   │- daily/wkly/ │   │- fake orders   │                 │
│   │  monthly     │   │- live rerun    │                 │
│   └──────────────┘   └────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

**Data flow summary:**

1. User logs in → role is stored in session state
2. `DataPreparation` loads and cleans the CSV
3. `KPIEngine` aggregates orders into monthly KPI summaries
4. `DropDetector` scans the monthly KPIs for drops
5. `RootCauseAnalyzer` drills into the problem month across dimensions
6. `ExecutiveSummary` combines all results into a one-screen overview
7. `ComparisonEngine` handles period-over-period comparisons
8. `AlertEngine` fires emails if thresholds are breached
9. `SimulationEngine` injects new orders and triggers a full rerun of all above steps

---

## 7. Module-by-Module Breakdown

### 7.1 `data_preparation.py`

**Class:** `DataPreparation`

**Purpose:** Loads any CSV or Excel file, standardises column names, parses dates, and engineers derived features that all other modules depend on.

**Step-by-step logic:**

**Step 1 — Column name standardisation**
```python
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")
```
This converts `"Order Date"` → `"order_date"`, `"Sub-Category"` → `"sub_category"`, etc.

**Step 2 — Column alias mapping**

A dictionary maps common alternative names to the expected internal names:
```python
"order_date": ["date", "orderdate", "order_dt", "transaction_date"]
"sales":      ["revenue", "sale_amount", "total_sales", "amount"]
```
If the column `order_date` doesn't exist but `date` does, it is renamed.

**Step 3 — Date parsing**
```python
df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", dayfirst=True)
```
`format="mixed"` allows pandas to handle each row's date format independently, accommodating datasets where some rows use `YYYY-MM-DD` and others use `DD-MM-YYYY`.

**Step 4 — Feature engineering**

| Derived Column | Formula |
|---|---|
| `shipping_days` | `(ship_date - order_date).dt.days` |
| `cost` | `sales - profit` |
| `profit_margin_%` | `(profit / sales) × 100` |
| `discount` | `((1 - normalised_margin) × 0.4).round(2)` |
| `year_month` | `order_date.dt.to_period("M")` |
| `orders` | `groupby(order_date).size()` merged back onto df |

**Step 5 — Safety defaults**

Columns that some CSVs may lack are filled with sensible defaults:
- `segment`: Derived from `category` using a mapping (Furniture→Corporate, Technology→Consumer, Office Supplies→Home Office), or defaults to `"Consumer"`
- `category`, `sub_category`: Default to `"General"`
- `region`: Defaults to `"Unknown"`
- `order_id`: Auto-generated as `ORD-000001`, `ORD-000002`, etc. if missing

**Step 6 — Data cleaning**
```python
df = df.drop_duplicates(subset=["order_id"])
df = df.dropna(subset=["sales", "profit", "order_date"])
```
Removes duplicate orders and rows where critical fields are missing.

---

### 7.2 `kpi_engine.py`

**Class:** `KPIEngine`

**Purpose:** Aggregates the order-level dataframe into a monthly KPI summary table. This is the core table used by almost every other module.

**Input:** Full order dataframe (output of `DataPreparation`)

**Output:** Monthly KPI dataframe with one row per month

**Aggregations performed:**

```python
monthly_kpis = df.groupby("year_month").agg(
    sales             = ("sales",         "sum"),
    profit            = ("profit",        "sum"),
    orders            = ("order_id",      "count"),
    quantity          = ("quantity",      "sum"),
    avg_shipping_days = ("shipping_days", "mean"),
    profit_margin_%   = ("profit_margin_%","mean"),
)
```

Each row in the output represents one calendar month. The result is sorted chronologically before being returned.

---

### 7.3 `drop_detection.py`

**Class:** `DropDetector`

**Purpose:** Scans the monthly KPI table and identifies months where a significant drop occurred in any tracked KPI.

**Method:** `detect_drops()`

**Logic:** For each KPI column (sales, profit, orders, margin, shipping), it computes the month-over-month percentage change:

```
% Change = ((Current Month - Previous Month) / Previous Month) × 100
```

A month is flagged as a drop if this change is more negative than the configured `drop_threshold` (default: -10%).

The method returns a dataframe of all detected drop months, sorted by severity. The most recent drop month is used as the `problem_month` for root cause analysis.

**Drop flag mechanism used in charts:**
```python
kpis["sales_drop"] = kpis["sales"].diff() < 0
```
`.diff()` = `Current - Previous`. If negative, that month is a drop.

---

### 7.4 `comparison_engine.py`

**Class:** `ComparisonEngine`

**Purpose:** Provides period-over-period sales comparisons at three granularities.

**Methods:**

- `daily_comparison(metric)` — compares the most recent day vs the day before
- `weekly_comparison(metric)` — compares the most recent 7-day window vs the previous 7-day window
- `monthly_comparison(metric)` — compares the most recent calendar month vs the previous calendar month

**Return value:** Each method returns a tuple: `(data_slice, pct_change)`

- `data_slice` is a small dataframe with the two periods being compared
- `pct_change` is a single float representing the % change

**Formula:**
```
pct_change = ((Latest Period Total - Previous Period Total) / Previous Period Total) × 100
```

If `pct_change < -drop_threshold`, an alert is triggered for that period.

---

### 7.5 `root_cause.py`

**Class:** `RootCauseAnalyzer`

**Purpose:** When a drop month is detected, this module drills into the data to find which dimension (region, category, sub-category, segment) caused or contributed to the drop.

**Method:** `full_root_cause(problem_month)`

**How it works — step by step:**

**Step 1 — Isolate the problem month's data**
Filter all orders where `year_month == problem_month`.

**Step 2 — Analyse each dimension**
For each dimension (region, category, sub-category, segment), the `_compare_dimension()` helper:
1. Groups the full dataset by `year_month` and the dimension
2. Computes month-over-month % change per group using `.pct_change()`
3. Isolates the problem month's rows
4. Returns the dimension value with the biggest drop

**Step 3 — Identify worst region**
```python
region_analysis = self._compare_dimension("region", problem_month)
worst_region = region_analysis.sort_values("pct_change").iloc[0]["region"]
```

**Step 4 — Analyse segment within worst region**
Filters to only orders in the `worst_region`, then repeats the groupby/pct_change analysis for `segment`.

**Step 5 — Return full root cause dict**
```python
{
    "worst_region":   "South",
    "worst_category": "Furniture",
    "worst_segment":  "Corporate",
    "worst_subcat":   "Tables"
}
```

This dictionary is passed to `ExecutiveSummary` for display and to the dashboard for the Root Cause card.

---

### 7.6 `alert_engine.py`

**Class:** `AlertEngine`

**Purpose:** Sends email alerts when KPI drops are detected.

**Configuration:**
```python
AlertEngine({
    "email": {
        "sender":   "sender@gmail.com",
        "password": "app_password",
        "receiver": "receiver@gmail.com"
    }
})
```

**Method:** `send_email(subject, body)`

Uses Python's built-in `smtplib` library to connect to Gmail's SMTP server (`smtp.gmail.com`, port 587) and send a plain-text email.

**When alerts fire:**
- Daily sales drop > configured drop threshold %
- Weekly sales drop > configured drop threshold %
- Monthly sales drop > configured drop threshold %

Only Admin users can trigger the email send button. Alerts are constructed as a list of strings and joined into the email body.

---

### 7.7 `executive_summary.py`

**Class:** `ExecutiveSummary`

**Purpose:** Generates a concise, one-screen health report of the entire business.

**Method:** `generate()`

**Inputs required:**
- Monthly KPI table (`kpis`)
- Full order dataframe (`df`)
- Detected drops list (`drops`)
- Root cause result dict (`root_result`)

**What it computes:**

| Field | How calculated |
|---|---|
| `overall_status` | Text description: "Business Growing", "Drop Detected", etc. |
| `status_color` | `"green"` / `"red"` / `"yellow"` based on drop presence and margin health |
| `period` | Date range: `min(order_date)` → `max(order_date)` |
| `latest_sales` | `kpis.iloc[-1]["sales"]` |
| `sales_change` | MoM % change of latest month vs previous: `((current - previous) / previous) × 100` |
| `latest_profit` | `kpis.iloc[-1]["profit"]` |
| `profit_change` | MoM % change of profit |
| `latest_orders` | `kpis.iloc[-1]["orders"]` |
| `orders_change` | MoM % change of orders |
| `top_region` | `df.groupby("region")["sales"].sum().idxmax()` |
| `top_category` | `df.groupby("category")["sales"].sum().idxmax()` |
| `root_cause` | From `root_result["worst_region"]` and `root_result["worst_category"]` |
| `drop_status` | Summary string with 🚨 if drops exist, ✅ if clean |

---

### 7.8 `simulation_engine.py`

**Class:** `SimulationEngine`

**Purpose:** Generates batches of realistic fake orders to simulate live incoming data.

**Method:** `generate_fake_orders(n=200)`

**How fake orders are generated:**

1. Samples random rows from the real dataset to use as templates
2. Assigns new random `order_id` values
3. Sets `order_date` and `ship_date` to dates near the present
4. Slightly randomises `sales` and `profit` values by applying a noise factor:
   ```
   fake_sales = real_sales × random_noise   where noise ∈ [0.8, 1.2]
   ```
5. Returns a dataframe of `n` fake orders with the same schema as the real data

**How the simulation loop works:**

1. 200 fake orders are pre-generated as a batch
2. Every simulation tick, the next 3 orders from the batch are appended to `live_df`
3. `KPIEngine` recalculates all monthly KPIs on the updated `live_df`
4. The dashboard reruns via `st.rerun()` after a configurable delay (0.5s – 2s)
5. When all 200 orders are consumed, a new batch of 200 is generated and the loop continues

The `live_df` and simulation state are stored in `st.session_state` so they survive Streamlit reruns.

---

### 7.9 `audit_logger.py`

**Class / Function:** `log_event`

**Purpose:** Records all significant system events to a log file with a timestamp.

**Signature:**
```python
log_event(role, action, detail)
```

**Example events logged:**
- User login / logout
- KPI drop detected (with %)
- Email alert sent
- Data file uploaded

If the audit logger module fails to import (e.g., missing file), the system silently replaces it with a no-op function so the dashboard continues to work:
```python
try:
    from src.audit_logger import log_event
except Exception:
    def log_event(*args, **kwargs): pass
```

---

## 8. Dashboard Pages & Sections

The dashboard is a single Streamlit page (`1_Live_Dashboard.py`) with the following sections rendered top to bottom:

| Section | Title | Visible To |
|---|---|---|
| 1 | Auth Check — redirects to login if not authenticated | All |
| 2 | Executive Summary | All |
| 3 | Historical Data Comparison (Daily / Weekly / Monthly) | All |
| 4 | Real-Time Alerts | Admin, Analyst |
| 5 | Threshold Alerts | All |
| 6 | KPI Threshold Comparison Table | All |
| 7 | Sales & Profit Trend Line Chart | All |
| 8 | KPI History Playback (Animated) | All |
| 9 | Dashboard Visualization — Bar Charts | All |
| 10 | Cumulative Area Charts | All |
| 11 | Sales Breakdown by Category & Region (Donut Charts) | All |
| 12 | Top Affected KPIs — Worst Drop Ever | All |
| 13 | Sales vs Profit Scatter (Margin Health) | All |
| 14 | Sub-Category Sales Drop Detection | All |
| 15 | Region-Wise Sales Performance | All |
| 16 | Segment-Wise Sales & Profit | All |
| 17 | Shipping Days vs Sales Scatter | All |
| 18 | Live Order Simulation | Admin, Analyst |

---

## 9. KPI Calculations — All Formulas

### Monthly KPI Aggregations

```
Monthly Sales       = SUM(sales)           for all orders in that month
Monthly Profit      = SUM(profit)          for all orders in that month
Monthly Orders      = COUNT(order_id)      for all orders in that month
Monthly Quantity    = SUM(quantity)        for all orders in that month
Avg Shipping Days   = MEAN(shipping_days)  for all orders in that month
Avg Profit Margin % = MEAN(profit_margin_%) for all orders in that month
```

### Derived Metrics per Order

```
Shipping Days    = ship_date - order_date              (in calendar days)
Cost             = sales - profit
Profit Margin %  = (profit / sales) × 100
Discount         = (1 - normalised_margin) × 0.4       (proxy discount from margin)
```

### Month-over-Month % Change

```
MoM % Change = ((Current Month Value - Previous Month Value) / Previous Month Value) × 100
```

Implemented in pandas as:
```python
series.pct_change() × 100
```

### Period Comparisons (ComparisonEngine)

```
Daily  % Change  = ((Today's Sales    - Yesterday's Sales)   / Yesterday's Sales)   × 100
Weekly % Change  = ((This Week Sales  - Last Week Sales)     / Last Week Sales)     × 100
Monthly % Change = ((This Month Sales - Last Month Sales)    / Last Month Sales)    × 100
```

### Drop Detection

```
diff = Current Month Value - Previous Month Value

If diff < 0  → DROP  (True)
If diff ≥ 0  → NORMAL (False)
```

### Worst Drop Per KPI

```
Worst Drop % = MIN(all monthly pct_change values) × 100
```

For Shipping Days, the worst is the MAX (an increase in days is bad):
```
Worst Shipping Increase % = MAX(all monthly pct_change values) × 100
```

### Donut Chart Percentage (Category & Region)

```
Category % = (Sum of Sales for Category / Total Sales across all categories) × 100
Region %   = (Sum of Sales for Region   / Total Sales across all regions)    × 100
```

Implemented automatically by Matplotlib's `autopct='%1.1f%%'` on the pie/donut chart.

### Profit Margin Colour Scale (Scatter Chart)

```
Dot colour = f(profit_margin_%)   using the RdYlGn colourmap

Low margin  → Red
Mid margin  → Yellow
High margin → Green
```

No fixed threshold is used; colour is relative to the range of margins in the current dataset.

### Shipping Trend Line (Linear Regression)

```
y = z[0] × x + z[1]

where:
  x = avg_shipping_days
  y = sales
  z = np.polyfit(x, y, degree=1)   ← least-squares linear fit
```

A negative slope means more shipping days correlates with lower sales.

---

## 10. Drop Detection Logic

### How a Month is Classified as a "Drop"

The system uses two separate but related mechanisms:

**Mechanism 1 — Absolute diff (for colouring charts)**

Used in bar charts and line charts to colour individual months red:
```python
kpis["sales_drop"] = kpis["sales"].diff() < 0
```
If the raw value decreased at all vs the previous month → red.

**Mechanism 2 — Percentage threshold (for alerts)**

Used by `DropDetector` and `ComparisonEngine` to trigger alerts:
```python
pct_change = series.pct_change() × 100
if pct_change < -drop_threshold:
    # alert fired
```
Only fires if the drop exceeds the configured threshold (default: 10%).

### Edge Case: First Month

The first row always has `NaN` from `.diff()` and `.pct_change()`. Pandas evaluates `NaN < 0` as `False`, so the first month is always treated as Normal — no false drop alert on startup.

### Severity Tiers (Sub-Category and Region Charts)

```
Drop > 20%        → Red    (severe)
Drop 0% to 20%    → Orange (moderate)
No drop (≥ 0%)    → Green  (growth or stable)
```

---

## 11. Root Cause Analysis

When a drop month is detected, `RootCauseAnalyzer.full_root_cause(problem_month)` runs the following pipeline:

### Step 1 — Regional Analysis

```python
region_monthly = df.groupby(["year_month", "region"])["sales"].sum()
region_monthly["pct_change"] = region_monthly.groupby("region")["sales"].pct_change() × 100
worst_region = region_monthly[region_monthly.year_month == problem_month].sort_values("pct_change").iloc[0]["region"]
```

Finds which region had the worst sales drop in the problem month.

### Step 2 — Category Analysis

Same process applied to `category`:
```python
category_monthly = df.groupby(["year_month", "category"])["sales"].sum()
worst_category = ... # category with worst pct_change in problem_month
```

### Step 3 — Segment Analysis (within worst region)

Filters data to only the `worst_region`, then analyses by `segment`:
```python
region_df = df[df["region"] == worst_region]
segment_monthly = region_df.groupby(["year_month", "segment"])["sales"].sum()
worst_segment = ... # segment with worst pct_change in problem_month
```

### Step 4 — Sub-Category Analysis

Same approach applied to `sub_category` on the full dataset.

### Output

A dictionary containing the four worst-performing dimensions for the problem month:
```python
{
    "worst_region":   "South",
    "worst_category": "Furniture",
    "worst_segment":  "Corporate",
    "worst_subcat":   "Tables"
}
```

This is surfaced in the Executive Summary as the "Root Cause" field.

---

## 12. Alert System

### Two Types of Alerts

**Type 1 — Threshold Alerts (always visible)**

Compares the latest month's KPI values against user-configured thresholds:

| KPI | Condition | Message |
|---|---|---|
| Sales | `latest_sales < sales_threshold` | ⚠️ Sales below threshold |
| Profit | `latest_profit < profit_threshold` | ⚠️ Profit below threshold |
| Orders | `latest_orders < orders_threshold` | ⚠️ Orders below threshold |
| Margin % | `latest_margin < margin_threshold` | ⚠️ Margin below threshold |
| Shipping | `latest_shipping > shipping_threshold` | ⚠️ Shipping too slow |

These display as yellow warnings on screen and require no user action.

**Type 2 — Drop Alerts (Admin/Analyst only)**

Triggered when a period-over-period comparison exceeds the drop threshold:

```python
if pct_change < -drop_threshold:
    triggered_alerts.append(f"🚨 Daily Sales Drop: {pct_change:.2f}%")
```

These display as red error banners. Admin users can then press **📤 Send Email Alert** to dispatch an SMTP email.

### Email Alert Flow

1. Drop detected → alert string appended to `triggered_alerts` list
2. Admin clicks "Send Email Alert"
3. `AlertEngine.send_email(subject, body)` called
4. `smtplib.SMTP("smtp.gmail.com", 587)` connects
5. `starttls()` encrypts the connection
6. `login(sender, password)` authenticates
7. `sendmail()` dispatches the message
8. Success/failure displayed in the UI

---

## 13. Role-Based Access Control

The system implements three access levels, set at login and stored in `st.session_state["role"]`.

| Permission | Admin | Analyst | Viewer |
|---|:---:|:---:|:---:|
| View all dashboard sections | ✅ | ✅ | ✅ |
| View real-time drop alerts | ✅ | ✅ | ❌ |
| Send email alerts | ✅ | ❌ | ❌ |
| Upload custom CSV/Excel | ✅ | ❌ | ❌ |
| Access live simulation | ✅ | ✅ | ❌ |
| Change data source | ✅ | ❌ | ❌ |

If a Viewer reaches a restricted section, an info banner is shown and `st.stop()` halts further rendering:
```python
if role == "Viewer":
    st.info("👁️ Live Simulation is restricted to Admin and Analyst roles")
    st.stop()
```

---

## 14. Live Simulation Engine

The simulation runs as a continuous loop using Streamlit's `st.rerun()` mechanism.

### State Variables (stored in `st.session_state`)

| Variable | Type | Purpose |
|---|---|---|
| `sim_running` | bool | Whether the simulation is currently active |
| `sim_index` | int | Index into the pre-generated fake orders list |
| `sim_all_fake` | DataFrame | Full batch of 200 pre-generated fake orders |
| `live_df` | DataFrame | Real data + all injected fake orders so far |

### Simulation Loop

```
START
│
▼
Generate 200 fake orders → sim_all_fake
Set sim_index = 0
Set live_df = original_df.copy()
│
▼
LOOP:
  Take next 3 orders from sim_all_fake[sim_index : sim_index+3]
  Append to live_df
  Recalculate KPIs on live_df
  Display updated metrics, charts, alerts
  Sleep(sim_delay)         ← 0.5s / 1s / 2s based on speed setting
  st.rerun()               ← triggers next iteration
  sim_index += 3
│
▼
If sim_index >= 200:
  Generate new batch of 200 orders
  Reset sim_index = 0
  Continue loop
```

All charts, metrics, and alerts update on every tick, giving the appearance of a live streaming dashboard.

---

## 15. Animated KPI Playback

The KPI History Playback feature replays the historical data month by month, building a chart incrementally — similar to a stock market ticker.

### How It Works

1. User selects a KPI metric (Sales, Profit, Orders, Margin %, Avg Shipping Days)
2. User clicks **▶️ Play History**
3. `anim_index` is set to 1 in session state
4. Each rerun:
   - Takes `kpis.iloc[:anim_index]` — a growing slice of the monthly data
   - Plots the line chart up to that month
   - Plots the MoM % change bar chart below it
   - Highlights the latest point with a red dot
   - Increments `anim_index` by 1
   - Sleeps for `anim_delay` (0.1s / 0.4s / 0.8s)
   - Calls `st.rerun()`

5. When `anim_index > len(kpis)`, playback ends and the live simulation auto-starts (for Admin/Analyst roles)

### Speed Options

| Setting | Delay per frame |
|---|---|
| Slow | 0.8 seconds |
| Medium | 0.4 seconds |
| Fast | 0.1 seconds |

---

## 16. Visualizations Reference

| Chart | Type | X-axis | Y-axis | Colour logic |
|---|---|---|---|---|
| Sales & Profit Trend | Line | year_month | sales, profit | Fixed: steelblue, green |
| Monthly KPI Bar Charts | Bar | year_month | KPI value | Red if drop, default otherwise |
| Cumulative Area Charts | Area + Line | year_month | sales, profit | Fixed: steelblue, green |
| Sales by Category | Donut (Pie) | — | % of total sales | Matplotlib default |
| Sales by Region | Donut (Pie) | — | % of total sales | Matplotlib default |
| Top Affected KPIs | Horizontal Bar | % change | KPI name | Red if negative, green if positive |
| Sales vs Profit Scatter | Scatter | sales | profit | RdYlGn by profit_margin_% |
| Sub-Category Drop Detection | Horizontal Bar | drop % | sub_category | Red>20%, Orange 0-20%, Green≥0% |
| Region Total Sales | Horizontal Bar | total sales | region | RdYlGn gradient |
| Region Worst Drop | Horizontal Bar | drop % | region | Red>20%, Orange 0-20%, Green≥0% |
| Segment Sales | Donut (Pie) | — | % of total sales | steelblue, orange, green |
| Segment Profit | Horizontal Bar | profit | segment | Green if positive, red if negative |
| Shipping vs Sales | Scatter + Trendline | avg_shipping_days | sales | RdYlGn by sales; red dashed trendline |
| KPI Playback | Line + Bar (animated) | month index | KPI value | Line: KPI colour; Bars: red/green |
| Live KPI Charts | 6-panel Line | year_month | KPI value | Fixed per KPI; red dot on latest |

---

## 17. Installation & Setup

### Prerequisites

- Python 3.10 or higher (tested on Python 3.13)
- pip

### Install Dependencies

```bash
pip install streamlit pandas numpy matplotlib openpyxl
```

Full list of required packages:

```
streamlit
pandas
numpy
matplotlib
openpyxl          # for Excel file support
```

### Gmail App Password Setup (for email alerts)

Standard Gmail passwords do not work with `smtplib`. You need to generate an App Password:

1. Go to your Google Account → Security
2. Enable 2-Step Verification
3. Go to Security → App Passwords
4. Select app: Mail, device: Other (custom name) → Generate
5. Copy the 16-character password into `alert_engine` config in `1_Live_Dashboard.py`

---

## 18. How to Run

```bash
# Navigate to project directory
cd C:\Desktop\DataScience\KPI_Main\Main_KPI

# Run the Streamlit app
python -m streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Login Credentials

Credentials are managed in `app.py`. Default test accounts (update for production):

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin |
| analyst | analyst123 | Analyst |
| viewer | viewer123 | Viewer |

---

## 19. How to Upload Your Own Data

1. Log in as **Admin**
2. In the sidebar, find **📂 Data Source**
3. Select **"Upload Your Own CSV"**
4. Upload a `.csv`, `.xlsx`, or `.xls` file

### Minimum Required Columns

Your file must contain at least these columns (exact names or common alternatives):

| Required | Accepted alternatives |
|---|---|
| `order_date` | `date`, `Date`, `Order Date`, `transaction_date` |
| `sales` | `Sales`, `Revenue`, `revenue`, `amount` |
| `profit` | `Profit`, `net_profit`, `earnings` |

### Optional but Recommended Columns

`ship_date`, `order_id`, `category`, `sub_category`, `region`, `segment`, `quantity`

If any of these are missing, the system fills them with safe defaults automatically.

---

## 20. Configuration & Thresholds

All thresholds are adjustable in the sidebar under **⚙️ KPI Threshold Settings**:

| Setting | Default | Description |
|---|---|---|
| Drop Alert % | 10.0 | Minimum % drop to trigger an alert |
| Sales Threshold | 500.0 | Minimum acceptable monthly sales ($) |
| Profit Threshold | 15,000.0 | Minimum acceptable monthly profit ($) |
| Orders Threshold | 100.0 | Minimum acceptable monthly order count |
| Margin Threshold % | 20.0 | Minimum acceptable profit margin (%) |
| Shipping Threshold | 3.0 | Maximum acceptable average shipping days |

These thresholds are applied live across the threshold alert table, the real-time alert banners, and the live simulation alerts. No code change is required — adjust the sliders and the dashboard responds immediately.

---

*README generated for KPI Intelligence System — Live Dashboard v1.0*
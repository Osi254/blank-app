import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="USC Builds Workforce Analytics",
    layout="wide"
)

st.title("🏗️ USC Builds Workforce Analytics Dashboard")
st.write("Analyze attendance, attrition, and workforce patterns across the USC Builds workforce.")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def color_cycle(n: int):
    cmap = plt.get_cmap("tab10")
    return [cmap(i % 10) for i in range(n)]


# ---------------------------------------------------------
# DATA LOADERS
# ---------------------------------------------------------
@st.cache_data
def load_core_employee_data():
    """Main employee + attendance dataset."""
    df = pd.read_csv("employees_with_attendance.csv", low_memory=False)

    # Parse dates
    for col in ["date_hired", "hire_date", "date_terminated", "date_of_birth"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Effective hire date
    if "date_hired" in df.columns:
        df["hire_effective"] = df["date_hired"]
    elif "hire_date" in df.columns:
        df["hire_effective"] = df["hire_date"]
    else:
        df["hire_effective"] = pd.NaT

    # Termination flag
    if "date_terminated" in df.columns:
        df["terminated_flag"] = df["date_terminated"].notna()
    else:
        df["terminated_flag"] = False

    # Tenure
    today = pd.Timestamp.today().normalize()
    end_date = df["date_terminated"].fillna(today)
    df["tenure_days"] = (end_date - df["hire_effective"]).dt.days
    df["tenure_years"] = df["tenure_days"] / 365.25

    # Early exit flags
    df["early_exit_60"] = df["terminated_flag"] & (df["tenure_days"] <= 60)
    df["early_exit_365"] = df["terminated_flag"] & (df["tenure_days"] <= 365)

    # Age
    if "date_of_birth" in df.columns:
        df["age"] = (today - df["date_of_birth"]).dt.days / 365.25
    else:
        df["age"] = pd.NA

    # Age band
    bins = [0, 25, 35, 45, 55, 65, 120]
    labels = ["<25", "25–34", "35–44", "45–54", "55–64", "65+"]
    df["age_band"] = pd.cut(df["age"], bins=bins, labels=labels, right=False)

    return df


@st.cache_data
def load_leave_hours():
    """
    Leave hours by month.

    Tries a couple of common paths and prints columns for debugging.
    Expects columns like:
      - 'month'  (period or date-like)
      - 'DurationValue'  (hours)
    """
    import os

    possible_paths = [
        "Data/attendance_features.csv",
        "attendance_features.csv",
    ]

    csv_path = None
    for p in possible_paths:
        if os.path.exists(p):
            csv_path = p
            break

    if csv_path is None:
        # Nothing found
        return pd.Series(dtype=float)

    leave_df = pd.read_csv(csv_path, low_memory=False)

    # OPTIONAL: show columns once to confirm what’s inside
    st.write("🔎 attendance_features columns:", list(leave_df.columns))

    # Try to auto-detect column names if they differ slightly
    # Adjust these if your real names are different
    month_col_candidates = ["month", "Month", "month_period"]
    hours_col_candidates = ["DurationValue", "duration", "Hours", "hours"]

    month_col = next((c for c in month_col_candidates if c in leave_df.columns), None)
    hours_col = next((c for c in hours_col_candidates if c in leave_df.columns), None)

    if month_col is None or hours_col is None:
        # Columns not found – bail out gracefully
        return pd.Series(dtype=float)

    # Parse month to monthly period
    leave_df[month_col] = pd.to_datetime(
        leave_df[month_col], errors="coerce"
    ).dt.to_period("M")

    # Group by month and sum hours
    hours_month = (
        leave_df.groupby(month_col)[hours_col].sum().sort_index()
    )

    return hours_month



@st.cache_data
def load_tenure_pay_data():
    """
    Tenure vs pay scatter data.

    Expects:
      - Data/employee_model.csv with: EmployeeID, PayRate, Age, IncidentCount
      - Data/employees_clean.csv with: employee_id, tenure, emp_type

    Adjust file paths/columns as needed to match your pipeline.
    """
    try:
        df_model = pd.read_csv("Data/employee_model.csv", low_memory=False)
        ten = pd.read_csv("Data/employees_clean.csv", low_memory=False)

        df_model["PayRate"] = pd.to_numeric(df_model.get("PayRate"), errors="coerce")
        df_model["Age"] = pd.to_numeric(df_model.get("Age"), errors="coerce")
        df_model["IncidentCount"] = pd.to_numeric(
            df_model.get("IncidentCount"), errors="coerce"
        )

        # Align key
        if "employee_id" in ten.columns:
            ten = ten.rename(columns={"employee_id": "EmployeeID"})

        df = df_model.merge(
            ten[["EmployeeID", "tenure", "emp_type"]],
            on="EmployeeID",
            how="left",
        )

        df["Tenure"] = pd.to_numeric(df.get("tenure"), errors="coerce")
        df = df[(df["PayRate"].notna()) & (df["Tenure"].notna())]
        df = df[df["Tenure"] >= 0]

        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_cluster_incidents_data():
    """
    Age vs incident count by cluster.

    Expects Data/cluster_incidents.csv with:
      - Age
      - IncidentCount
      - cluster3
    """
    try:
        clust = pd.read_csv("Data/cluster_incidents.csv", low_memory=False)
        return clust
    except Exception:
        return pd.DataFrame()


# ---------------------------------------------------------
# LOAD CORE DATA
# ---------------------------------------------------------
df = load_core_employee_data()

trade_label_col = "trade_desc" if "trade_desc" in df.columns else (
    "trade_id" if "trade_id" in df.columns else None
)
emp_id_col = "employee_no" if "employee_no" in df.columns else df.columns[0]

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.header("🔎 Filter Workforce View")

    # Date filter (by hire_effective)
    if df["hire_effective"].notna().any():
        min_date = df["hire_effective"].min().date()
        max_date = df["hire_effective"].max().date()
        start_date, end_date = st.date_input(
            "Hire date range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date,
        )
    else:
        start_date, end_date = None, None

    # Gender filter
    if "sex" in df.columns:
        all_genders = sorted(df["sex"].fillna("Unknown").unique())
        selected_genders = st.multiselect(
            "Gender",
            options=all_genders,
            default=all_genders,
        )
    else:
        selected_genders = None

    # Trade filter
    if trade_label_col:
        all_trades = sorted(df[trade_label_col].fillna("Unknown").unique())
        selected_trades = st.multiselect(
            "Trade",
            options=all_trades,
            default=all_trades,
        )
    else:
        selected_trades = None

    show_raw = st.checkbox("Show filtered data table", value=False)

# Apply filters
df_f = df.copy()

if start_date and end_date:
    mask = df_f["hire_effective"].between(
        pd.to_datetime(start_date),
        pd.to_datetime(end_date)
    )
    df_f = df_f[mask]

if selected_genders is not None and "sex" in df_f.columns:
    df_f = df_f[df_f["sex"].fillna("Unknown").isin(selected_genders)]

if selected_trades is not None and trade_label_col:
    df_f = df_f[df_f[trade_label_col].fillna("Unknown").isin(selected_trades)]

# Optional data preview
if show_raw:
    st.markdown("### 🔍 Filtered Data Snapshot")
    st.dataframe(df_f.head(200))

st.markdown("---")

# ---------------------------------------------------------
# KPI STRIP
# ---------------------------------------------------------
st.subheader("📊 Key Workforce KPIs (Filtered View)")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_headcount = df_f[emp_id_col].nunique()
active_headcount = df_f.loc[~df_f["terminated_flag"], emp_id_col].nunique()

avg_age = df_f["age"].mean(skipna=True) if "age" in df_f.columns else None
avg_pay = df_f["hourly_pay_calc"].mean(skipna=True) if "hourly_pay_calc" in df_f.columns else None
early_exit_rate_365 = df_f["early_exit_365"].mean() if "early_exit_365" in df_f.columns else None

kpi1.metric("Total Headcount", f"{total_headcount:,}")
kpi2.metric("Active Headcount", f"{active_headcount:,}")
kpi3.metric(
    "Avg Age",
    f"{avg_age:.1f} yrs" if (avg_age is not None and pd.notnull(avg_age)) else "N/A"
)
kpi4.metric(
    "Early Exit (≤365 days)",
    f"{early_exit_rate_365 * 100:.1f}%"
    if early_exit_rate_365 is not None
    else "N/A",
)

st.caption("All KPIs above are calculated based on the current filters (date, gender, trade).")
st.markdown("---")

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab_overview, tab_demo, tab_tenure, tab_leaves, tab_pay_risk = st.tabs(
    [
        "📌 Overview",
        "👥 Demographics",
        "⏳ Tenure & Attrition",
        "📅 Leaves & Terminations",
        "💵 Pay & Risk",
    ]
)

# ---------------------------------------------------------
# TAB 1 – OVERVIEW
# ---------------------------------------------------------
with tab_overview:
    st.subheader("Overall Workforce Snapshot")

    col_o1, col_o2 = st.columns(2)

    # Active vs Terminated
    with col_o1:
        st.markdown("**Headcount by Employment Status**")
        if "terminated_flag" in df_f.columns:
            status_counts = df_f["terminated_flag"].map(
                {False: "Active", True: "Terminated"}
            ).value_counts()

            fig, ax = plt.subplots(figsize=(4, 3))
            ax.bar(
                status_counts.index.astype(str),
                status_counts.values,
                color=color_cycle(len(status_counts)),
            )
            ax.set_ylabel("Employees")
            ax.set_title("Active vs Terminated")
            for i, v in enumerate(status_counts.values):
                ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=8)
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Termination status not available.")

    # Tenure distribution
    with col_o2:
        st.markdown("**Tenure Distribution (Years)**")
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.hist(df_f["tenure_years"].dropna(), bins=20, edgecolor="black")
        ax.set_xlabel("Tenure (Years)")
        ax.set_ylabel("Employees")
        ax.set_title("Tenure Distribution")
        st.pyplot(fig, use_container_width=True)

# ---------------------------------------------------------
# TAB 2 – DEMOGRAPHICS
# ---------------------------------------------------------
with tab_demo:
    st.subheader("Demographic Breakdown")

    col_a1, col_a2 = st.columns(2)

    # Age bands
    with col_a1:
        st.markdown("**Age Distribution (Bands)**")
        if df_f["age"].notna().sum() > 0:
            age_band_order = ["<25", "25–34", "35–44", "45–54", "55–64", "65+"]
            age_band_counts = df_f["age_band"].value_counts().reindex(age_band_order)

            fig, ax = plt.subplots(figsize=(4, 3))
            ax.bar(age_band_counts.index.astype(str), age_band_counts.values)
            ax.set_xlabel("Age Band")
            ax.set_ylabel("Employees")
            ax.set_title("Age Distribution")
            for i, v in enumerate(age_band_counts.values):
                if pd.notnull(v):
                    ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=8)
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Age could not be calculated from date_of_birth.")

    # Age histogram
    with col_a2:
        st.markdown("**Age Histogram (Years)**")
        if df_f["age"].notna().sum() > 0:
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.hist(df_f["age"].dropna(), bins=20, edgecolor="black")
            ax.set_xlabel("Age (Years)")
            ax.set_ylabel("Employees")
            ax.set_title("Age Histogram")
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Age could not be calculated.")

    st.markdown("---")

    col_b1, col_b2 = st.columns(2)

    # Gender
    with col_b1:
        st.markdown("**Gender Distribution**")
        if "sex" in df_f.columns:
            g_counts = df_f["sex"].fillna("Unknown").value_counts()

            fig, ax = plt.subplots(figsize=(4, 3))
            ax.bar(
                g_counts.index.astype(str),
                g_counts.values,
                color=color_cycle(len(g_counts)),
            )
            ax.set_xlabel("Gender")
            ax.set_ylabel("Employees")
            ax.set_title("Gender Distribution")
            for i, v in enumerate(g_counts.values):
                ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=8)
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Column 'sex' not found.")

    # Minority / ethnicity
    with col_b2:
        if "minority_desc" in df_f.columns:
            st.markdown("**Minority Status Distribution**")
            m_counts = df_f["minority_desc"].fillna("Unknown").value_counts()

            fig, ax = plt.subplots(figsize=(4, 3))
            ax.bar(
                m_counts.index.astype(str),
                m_counts.values,
                color=color_cycle(len(m_counts)),
            )
            ax.set_xlabel("Minority Status")
            ax.set_ylabel("Employees")
            ax.set_title("Minority Distribution")
            ax.set_xticklabels(m_counts.index.astype(str), rotation=45, ha="right")
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Minority/ethnicity column not available.")

# ---------------------------------------------------------
# TAB 3 – TENURE & ATTRITION
# ---------------------------------------------------------
with tab_tenure:
    st.subheader("Tenure & Attrition Patterns")

    col_d1, col_d2 = st.columns(2)

    # Attrition rate by age band
    with col_d1:
        st.markdown("**Attrition Rate by Age Band**")
        band = df_f.groupby("age_band", dropna=False).agg(
            headcount=(emp_id_col, "nunique"),
            terminations=("terminated_flag", "sum"),
        )
        band["attrition_rate"] = band["terminations"] / band["headcount"]

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(band.index.astype(str), band["attrition_rate"])
        ax.set_xlabel("Age Band")
        ax.set_ylabel("Attrition Rate")
        ax.set_title("Attrition by Age Band")
        st.pyplot(fig, use_container_width=True)

    # Early exit by age band
    with col_d2:
        st.markdown("**Early Exit (≤365 Days) by Age Band**")
        if "early_exit_365" in df_f.columns:
            band_exit = df_f.groupby("age_band", dropna=False).agg(
                headcount=(emp_id_col, "nunique"),
                early_exits=("early_exit_365", "sum"),
            )
            band_exit["exit_rate"] = band_exit["early_exits"] / band_exit["headcount"]

            fig, ax = plt.subplots(figsize=(4, 3))
            ax.bar(band_exit.index.astype(str), band_exit["exit_rate"])
            ax.set_xlabel("Age Band")
            ax.set_ylabel("Early Exit Rate (≤365d)")
            ax.set_title("Early Exit (≤365 Days) by Age Band")
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Early exit (≤365 days) not available.")

# ---------------------------------------------------------
# TAB 4 – LEAVES & TERMINATIONS
# ---------------------------------------------------------
with tab_leaves:
    st.subheader("📅 Leave & Termination Trends")

    # Leave hours by month (external dataset)
    hours_month = load_leave_hours()  # index: PeriodIndex(M) if loader is as defined

    # Terminations by month (from core df)
    if df_f["terminated_flag"].any() and "date_terminated" in df_f.columns:
        term_df = df_f.loc[df_f["terminated_flag"]].copy()
        term_df["month"] = term_df["date_terminated"].dt.to_period("M")
        term_counts = (
            term_df.groupby("month")[emp_id_col].nunique().sort_index()
        )
    else:
        term_counts = pd.Series(dtype=int)

    # 1) Total Leave Hours by Month
    if not hours_month.empty:
        st.markdown("**Total Leave Hours by Month**")

        # convert PeriodIndex -> Timestamp for clean date handling
        x_dates = hours_month.index.to_timestamp()

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(x_dates, hours_month.values, marker="o")

        ax.set_title("Total Leave Hours by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Hours")

        # show every 3rd month label, formatted as YYYY-MM
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
    else:
        st.info(
            "No leave hours data available. "
            "Ensure Data/attendance_features.csv has 'month' and 'DurationValue' columns."
        )

    # 2) Terminations by Month
    if not term_counts.empty:
        st.markdown("**Terminations by Month**")

        x_term_dates = term_counts.index.to_timestamp()

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(x_term_dates, term_counts.values, marker="o")

        ax.set_title("Terminations by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Count")

        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No termination-by-month data available for the current filters.")

    # 3) Combined: Leaves vs Terminations per Month
    # align indices (months) from both series
    if not hours_month.empty or not term_counts.empty:
        all_months = sorted(set(hours_month.index).union(term_counts.index))
        both = pd.DataFrame({
            "leave_hours": hours_month.reindex(all_months),
            "terminations": term_counts.reindex(all_months),
        }).fillna(0)

        if not both.empty and (
            both["leave_hours"].sum() > 0 or both["terminations"].sum() > 0
        ):
            st.markdown("**Leaves vs Terminations per Month**")

            x_both_dates = pd.PeriodIndex(both.index, freq="M").to_timestamp()

            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(x_both_dates, both["leave_hours"], marker="o", label="Leave Hours")
            ax.plot(x_both_dates, both["terminations"], marker="o", label="Terminations")

            ax.set_title("Leaves vs Terminations per Month")
            ax.set_xlabel("Month")
            ax.set_ylabel("Value (Hours / Count)")

            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

            plt.xticks(rotation=45, ha="right")
            ax.legend(frameon=False)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("No combined leave/termination data available to plot.")
    else:
        st.info("No leave or termination data available to build combined trend.")

# ---------------------------------------------------------
# TAB 5 – PAY & RISK
# ---------------------------------------------------------
with tab_pay_risk:
    st.subheader("💵 Pay & Attendance Risk Views")

    df_tp = load_tenure_pay_data()
    clust = load_cluster_incidents_data()

    col_p1, col_p2 = st.columns(2)

    # Tenure vs Pay scatter
    with col_p1:
        st.markdown("**Tenure vs Pay Rate by Employee Type**")
        if not df_tp.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            if "emp_type" in df_tp.columns:
                types = sorted(df_tp["emp_type"].dropna().unique())
            else:
                types = [None]

            for t in types:
                if t is None:
                    sub = df_tp
                    label = "All"
                else:
                    sub = df_tp[df_tp["emp_type"] == t]
                    label = t
                if not sub.empty:
                    ax.scatter(
                        sub["Tenure"],
                        sub["PayRate"],
                        s=25,
                        alpha=0.6,
                        label=label,
                    )

            ax.set_title("Tenure vs Pay Rate by Employee Type")
            ax.set_xlabel("Tenure (years)")
            ax.set_ylabel("Pay rate")
            ax.legend()
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

            if {"Tenure", "PayRate"}.issubset(df_tp.columns):
                corr_tp = (
                    df_tp[["Tenure", "PayRate"]].corr().loc["Tenure", "PayRate"]
                )
                st.caption(f"Correlation between tenure and pay rate: {corr_tp:.3f}")
        else:
            st.info(
                "No tenure/pay data available. Ensure Data/employee_model.csv "
                "and Data/employees_clean.csv exist with the correct columns."
            )

    # Age vs IncidentCount by cluster
    with col_p2:
        st.markdown("**Age vs Attendance Incidents by Cluster**")
        if (
            not clust.empty
            and {"Age", "IncidentCount", "cluster3"}.issubset(clust.columns)
        ):
            fig, ax = plt.subplots(figsize=(6, 4))
            for cid in sorted(clust["cluster3"].unique()):
                sub = clust[clust["cluster3"] == cid]
                ax.scatter(
                    sub["Age"],
                    sub["IncidentCount"],
                    s=25,
                    alpha=0.6,
                    label=f"Cluster {cid}",
                )

            ax.set_title("Age vs Attendance Incidents by Cluster")
            ax.set_xlabel("Age")
            ax.set_ylabel("Incident count")
            ax.legend()
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        else:
            st.info(
                "No cluster incident data available. Ensure Data/cluster_incidents.csv "
                "exists with 'Age', 'IncidentCount', and 'cluster3' columns."
            )

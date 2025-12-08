import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Optional: in multi-page apps, it's usually only on Home.py,
# but it's safe here if you want.
st.set_page_config(
    page_title="USC Builds Workforce Analytics",
    layout="wide"
)

st.title("🏗️ USC Builds Workforce Analytics Dashboard")
st.write("Analyze attendance, attrition, and workforce patterns.")

# ------------------------
# Helper: Color palette
# ------------------------
def color_cycle(n):
    cmap = plt.get_cmap("tab10")
    return [cmap(i % 10) for i in range(n)]

# ------------------------
# Load & transform data
# ------------------------
@st.cache_data
def load_data():
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

    # Tenure (days & years)
    today = pd.Timestamp.today().normalize()
    end_date = df["date_terminated"].fillna(today)
    df["tenure_days"] = (end_date - df["hire_effective"]).dt.days
    df["tenure_years"] = df["tenure_days"] / 365.25

    # Early exit flags
    df["early_exit_60"] = (
        df["terminated_flag"]
        & (df["tenure_days"] <= 60)
    )
    df["early_exit_365"] = (
        df["terminated_flag"]
        & (df["tenure_days"] <= 365)
    )

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


df = load_data()

trade_label_col = "trade_desc" if "trade_desc" in df.columns else (
    "trade_id" if "trade_id" in df.columns else None
)
emp_id_col = "employee_no" if "employee_no" in df.columns else df.columns[0]

# ------------------------
# KPIs
# ------------------------
st.subheader("📊 Key Workforce KPIs")
col1, col2, col3 = st.columns(3)

avg_age = df["age"].mean(skipna=True) if "age" in df.columns else None
avg_pay = df["hourly_pay_calc"].mean(skipna=True) if "hourly_pay_calc" in df.columns else None
early_exit_rate_365 = df["early_exit_365"].mean() if "early_exit_365" in df.columns else None

col1.metric(
    "Avg Age",
    f"{avg_age:.1f}" if (avg_age is not None and pd.notnull(avg_age)) else "N/A"
)
col2.metric(
    "Avg Pay/hr",
    f"${avg_pay:.2f}" if (avg_pay is not None and pd.notnull(avg_pay)) else "N/A"
)
col3.metric(
    "Early Exit (≤365 days)",
    f"{early_exit_rate_365 * 100:.1f}%"
    if early_exit_rate_365 is not None
    else "N/A",
)

st.markdown("---")

# ============================================================
# ROW 1 – Age band distribution & Age histogram
# ============================================================
col_a1, col_a2 = st.columns(2)

with col_a1:
    st.subheader("Age Distribution (Bands)")
    if df["age"].notna().sum() > 0:
        age_band_order = ["<25", "25–34", "35–44", "45–54", "55–64", "65+"]
        age_band_counts = df["age_band"].value_counts().reindex(age_band_order)

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(age_band_counts.index.astype(str), age_band_counts.values)
        ax.set_xlabel("Age Band")
        ax.set_ylabel("Employees")
        ax.set_title("Age Distribution")

        for i, v in enumerate(age_band_counts.values):
            ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=8)

        st.pyplot(fig, use_container_width=False)
    else:
        st.info("Age could not be calculated from date_of_birth.")

with col_a2:
    st.subheader("Age Histogram (Years)")
    if df["age"].notna().sum() > 0:
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.hist(df["age"].dropna(), bins=20, edgecolor="black")
        ax.set_xlabel("Age (Years)")
        ax.set_ylabel("Employees")
        ax.set_title("Age Histogram")
        st.pyplot(fig, use_container_width=False)
    else:
        st.info("Age could not be calculated.")

# ============================================================
# ROW 2 – Gender distribution & Tenure distribution
# ============================================================
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.subheader("Gender Distribution")
    if "sex" in df.columns:
        g_counts = df["sex"].fillna("Unknown").value_counts()

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(g_counts.index.astype(str), g_counts.values,
               color=color_cycle(len(g_counts)))
        ax.set_xlabel("Gender")
        ax.set_ylabel("Employees")
        ax.set_title("Gender Distribution")
        st.pyplot(fig, use_container_width=False)
    else:
        st.info("Column 'sex' not found.")

with col_b2:
    st.subheader("Tenure Distribution (Years)")
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.hist(df["tenure_years"].dropna(), bins=20, edgecolor="black")
    ax.set_xlabel("Tenure (Years)")
    ax.set_ylabel("Employees")
    ax.set_title("Tenure Distribution")
    st.pyplot(fig, use_container_width=False)

# ============================================================
# ROW 3 – Headcount by Trade & Early Exit (≤60 days) by Trade
# ============================================================
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("Headcount by Trade (Top 15)")
    if trade_label_col:
        trade_counts = (
            df[trade_label_col].fillna("Unknown").value_counts().head(15)
        )
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(trade_counts.index.astype(str), trade_counts.values,
               color=color_cycle(len(trade_counts)))
        ax.set_xlabel("Trade")
        ax.set_ylabel("Employees")
        ax.set_title("Headcount by Trade")
        ax.set_xticklabels(trade_counts.index.astype(str), rotation=45, ha="right")
        st.pyplot(fig, use_container_width=False)
    else:
        st.info("No trade column found.")

with col_c2:
    st.subheader("Early Exit Rate (≤60 Days) by Trade")
    if trade_label_col:
        early = (
            df.groupby(trade_label_col)
            .agg(
                headcount=(emp_id_col, "nunique"),
                early_exits=("early_exit_60", "sum"),
            )
        )
        early["rate"] = early["early_exits"] / early["headcount"]
        early = early.sort_values("rate", ascending=False).head(15)

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(early.index.astype(str), early["rate"],
               color=color_cycle(len(early)))
        ax.set_xlabel("Trade")
        ax.set_ylabel("Early Exit Rate")
        ax.set_title("Early Exit (≤60 Days) by Trade")
        ax.set_xticklabels(early.index.astype(str), rotation=45, ha="right")
        st.pyplot(fig, use_container_width=False)
    else:
        st.info("Cannot compute early exit by trade (no trade column).")

# ============================================================
# ROW 4 – Attrition & Early Exit (≤365) by Age Band
# ============================================================
col_d1, col_d2 = st.columns(2)

with col_d1:
    st.subheader("Attrition Rate by Age Band")
    band = df.groupby("age_band").agg(
        headcount=(emp_id_col, "nunique"),
        terminations=("terminated_flag", "sum"),
    )
    band["attrition_rate"] = band["terminations"] / band["headcount"]

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(band.index.astype(str), band["attrition_rate"])
    ax.set_xlabel("Age Band")
    ax.set_ylabel("Attrition Rate")
    ax.set_title("Attrition by Age Band")
    st.pyplot(fig, use_container_width=False)

with col_d2:
    st.subheader("Early Exit (≤365 Days) by Age Band")
    if "early_exit_365" in df.columns:
        band_exit = df.groupby("age_band").agg(
            headcount=(emp_id_col, "nunique"),
            early_exits=("early_exit_365", "sum"),
        )
        band_exit["exit_rate"] = band_exit["early_exits"] / band_exit["headcount"]

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(band_exit.index.astype(str), band_exit["exit_rate"])
        ax.set_xlabel("Age Band")
        ax.set_ylabel("Early Exit Rate (≤365d)")
        ax.set_title("Early Exit (≤365 Days) by Age Band")
        st.pyplot(fig, use_container_width=False)
    else:
        st.info("Early exit (≤365 days) not available.")

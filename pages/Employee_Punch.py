import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path


st.set_page_config(page_title="Employee Punch Clock", layout="centered")

st.title("🕒 Employee Punch In / Punch Out")

# ------------------------
# Config
# ------------------------
DATA_PATH = Path("Data/employee_punches.csv")  # adjust if needed


# ------------------------
# Helpers
# ------------------------
def load_punches():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(
            columns=[
                "Employee ID",
                "Name",
                "Action",
                "Timestamp",
                "Date",
                "End-of-Day Report",
            ]
        )


def save_punch(employee_id, employee_name, action, notes=""):
    df = load_punches()

    now = datetime.now()
    row = {
        "Employee ID": employee_id,
        "Name": employee_name,
        "Action": action,  # <-- changed to match column name
        "Timestamp": now.isoformat(timespec="seconds"),
        "Date": now.date().isoformat(),
        "End-of-Day Report": notes,
    }

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)  # ensure folder exists
    df.to_csv(DATA_PATH, index=False)
    return row


# ------------------------
# Punch Form
# ------------------------
st.subheader("Punch Form")

col1, col2 = st.columns(2)
with col1:
    employee_id = st.text_input("Employee ID", placeholder="e.g., 12345")
with col2:
    employee_name = st.text_input("Name", placeholder="e.g., John Doe")

notes = st.text_area("Notes (optional)", placeholder="Add a comment if needed...", height=60)

if "last_action" not in st.session_state:
    st.session_state.last_action = None
if "last_row" not in st.session_state:
    st.session_state.last_row = None

col_in, col_out = st.columns(2)

with col_in:
    punch_in = st.button("✅ Punch In", use_container_width=True)
with col_out:
    punch_out = st.button("🚪 Punch Out", use_container_width=True)

if punch_in or punch_out:
    if not employee_id or not employee_name:
        st.error("Please enter both Employee ID and Name before punching.")
    else:
        action = "IN" if punch_in else "OUT"
        row = save_punch(employee_id, employee_name, action, notes)
        st.session_state.last_action = action
        st.session_state.last_row = row

        st.success(
            f"Recorded {action} for {employee_name} (ID: {employee_id}) at {row['Timestamp']}."
            #                        ^---------------------------^
        )

        if notes:
            st.info(f"End-of-Day Report: {notes}")

st.markdown("---")

# ------------------------
# Show today's punches for this employee
# ------------------------
st.subheader("Today's Punches")

df = load_punches()

if not df.empty:
    today = datetime.now().date().isoformat()

    # Filter by today and (optional) employee
    mask = df["date"] == today
    if employee_id:
        mask &= df["employee_id"].astype(str) == str(employee_id)

    df_today = df[mask].sort_values("timestamp", ascending=True)

    if df_today.empty:
        st.write("No punches recorded today yet.")
    else:
        st.dataframe(df_today.reset_index(drop=True))
else:
    st.write("No punch data recorded yet.")

import streamlit as st
import pandas as pd
from pathlib import Path
from auth import get_role

role = get_role()
if role is None:
    st.stop()

st.title("🕒 Punch Clock")

if role == "employee":
    st.caption("Employee view")
elif role == "hr":
    st.caption("HR view (you can see extra options here)")

st.title("Peer Feedback")

FILE_PATH = Path("employee_feedback.csv")

name = st.text_input("Employee name")

st.write("Rate this employee from 1 (low) to 10 (high):")
q1 = st.slider("Quality of work", 1, 10, 5)
q2 = st.slider("Teamwork & collaboration", 1, 10, 5)
q3 = st.slider("Reliability & attendance", 1, 10, 5)
q4 = st.slider("Safety & compliance", 1, 10, 5)

comments = st.text_area("Optional comments")

if st.button("Save feedback"):
    if not name.strip():
        st.error("Please enter a name.")
    else:
        new_row = pd.DataFrame({
            "employee_name": [name],
            "q1_quality": [q1],
            "q2_teamwork": [q2],
            "q3_reliability": [q3],
            "q4_safety": [q4],
            "comments": [comments],
        })

        if FILE_PATH.exists():
            new_row.to_csv(FILE_PATH, mode="a", header=False, index=False)
        else:
            new_row.to_csv(FILE_PATH, mode="w", header=True, index=False)

        st.success("✅ Feedback saved.")
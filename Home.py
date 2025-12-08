import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from auth import get_role


# ------------------------
# USC BUILDS LOGO + HEADER (clean + small logo)
# ------------------------

st.set_page_config(
    page_title="USC Builds Workforce Analytics",
    layout="wide"
)

# --- Header layout ---
col_logo, col_title = st.columns([0.4, 4])   # smaller first column

with col_logo:
    st.image("Tompkins_Profile_Logo_(1).png", width=80)  # small logo top-left

with col_title:
    st.markdown(
        """
        <h1 style='margin-bottom:0;'>USC Builds Workforce Analytics Dashboard</h1>
        <p style='font-size:16px; margin-top:4px;'>
            Analyze attendance, attrition, and workforce patterns.
        </p>
        """,
        unsafe_allow_html=True
    )

# ------------------------
# Load Data
# ------------------------
df = pd.read_csv("employees_with_attendance.csv", low_memory=False)



# ------------------------
# PASSWORD PROTECTION
# ------------------------

import streamlit as st

st.set_page_config(page_title="USC Builds – Home", layout="wide")
st.title("USC Builds Workforce App")

st.write("Choose a workflow below:")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/Analysis.py", label="📊 Workforce Analysis")
with col2:
    st.page_link("pages/HR_Job_Sites.py", label="🧑‍💼 HR – Job Sites")
with col3:
    st.page_link("pages/Find_Jobs_Near_Me.py", label="🧰 Find Jobs Near Me")


import streamlit as st
from auth import get_role

st.set_page_config(page_title="USC Builds Workforce Analytics", layout="wide")

role = get_role()
if role is None:
    st.stop()

st.title("🏗️ USC Builds Workforce Analytics")

if role == "employee":
    st.info("You are logged in as Employee. Limited view.")
elif role == "hr":
    st.success("You are logged in as HR. Full access.")


# streamlit run Home.py --server.address=0.0.0.0 --server.port=8501
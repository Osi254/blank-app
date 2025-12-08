# pages/HR_Job_Sites.py
import streamlit as st
import os
import sys
from auth import get_role

role = get_role()
if role is None:
    st.stop()

if role != "hr":
    st.error("⛔ This page is only available to HR.")
    st.stop()

st.title("🏗️ Job Sites (HR View Only)")

# Make the project root importable when running from /pages
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from utils_locations import load_job_sites, save_job_sites, geocode_zip

import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR – Job Sites", layout="wide")

st.title("HR – Manage Job Sites & Trades Needed")

st.write(
    "Use this page to add construction sites that need workers and specify the "
    "trade and number of workers required."
)

df = load_job_sites()

with st.form("add_site_form"):
    st.subheader("Add / Update Job Site")

    col1, col2 = st.columns(2)
    with col1:
        site_name = st.text_input("Site Name*")
        address = st.text_input("Street Address*", placeholder="123 Main St")
        city = st.text_input("City*")
    with col2:
        state = st.text_input("State*", max_chars=2, placeholder="NY")
        zip_code = st.text_input("ZIP Code*", max_chars=10)
        trade = st.text_input("Trade Needed*", placeholder="Electrician, Carpenter, etc.")
        needed_workers = st.number_input(
            "Number of Workers Needed*", min_value=1, step=1
        )

    submitted = st.form_submit_button("Save Job Site")

    if submitted:
        if not (site_name and address and city and state and zip_code and trade):
            st.error("Please fill in all required fields (*)")
        else:
            lat, lon = geocode_zip(zip_code)
            if lat is None:
                st.error("Could not geocode that ZIP code. Please check and try again.")
            else:
                new_row = {
                    "site_name": site_name,
                    "address": address,
                    "city": city,
                    "state": state.upper(),
                    "zip_code": zip_code,
                    "trade": trade,
                    "needed_workers": needed_workers,
                    "latitude": lat,
                    "longitude": lon,
                }

                df = df._append(new_row, ignore_index=True)
                save_job_sites(df)
                st.success(f"Saved job site: {site_name} ({zip_code})")

st.subheader("Current Job Sites in System")
if df.empty:
    st.info("No job sites have been added yet.")
else:
    st.dataframe(df)

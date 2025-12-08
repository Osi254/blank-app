# pages/Find_Jobs_Near_Me.py
import os
import sys
import streamlit as st
import pandas as pd

# -------------------------
# REMOVE ALL AUTH / SECURITY
# -------------------------

# Make the project root importable when running from /pages
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from utils_locations import load_job_sites, geocode_zip, haversine

st.set_page_config(page_title="Find Job Sites Near Me", layout="wide")

st.title("Find Job Sites Near Me")

st.write(
    "Enter your ZIP code to see job sites closest to you, including the trade "
    "needed at each site."
)

df_sites = load_job_sites()

if df_sites.empty:
    st.warning("No job sites are currently available. Please check back later.")
    st.stop()

col_input, col_filter = st.columns([2, 1])
with col_input:
    user_zip = st.text_input("Your ZIP Code*", max_chars=10)
with col_filter:
    max_distance_km = st.slider(
        "Max Distance (km)", min_value=5, max_value=200, value=50, step=5
    )

search_btn = st.button("Find Jobs Near Me")

if search_btn:
    if not user_zip:
        st.error("Please enter a ZIP code.")
    else:
        user_lat, user_lon = geocode_zip(user_zip)
        if user_lat is None:
            st.error("Could not locate that ZIP code. Please double-check it.")
        else:
            # Compute distance to each site
            df = df_sites.copy()
            df["distance_km"] = df.apply(
                lambda row: haversine(
                    user_lat, user_lon, row["latitude"], row["longitude"]
                ),
                axis=1,
            )

            df = df.sort_values("distance_km")
            df_near = df[df["distance_km"] <= max_distance_km]

            if df_near.empty:
                st.info(
                    f"No job sites found within {max_distance_km} km of ZIP {user_zip}."
                )
            else:
                st.subheader("Nearest Job Sites")
                st.caption(
                    f"Showing job sites within {max_distance_km} km of ZIP {user_zip}, "
                    "sorted by distance."
                )

                cols_to_show = [
                    "site_name",
                    "trade",
                    "needed_workers",
                    "address",
                    "city",
                    "state",
                    "zip_code",
                    "distance_km",
                ]
                df_display = df_near[cols_to_show].copy()
                df_display["distance_km"] = df_display["distance_km"].round(1)

                st.dataframe(df_display)

                # 2D map of nearby sites + user location
                st.subheader("Map View (2D)")

                map_df_sites = df_near[["latitude", "longitude", "site_name"]].copy()
                map_df_sites.rename(
                    columns={"latitude": "lat", "longitude": "lon"}, inplace=True
                )
                map_df_sites["type"] = "Job Site"

                map_user = pd.DataFrame(
                    [
                        {
                            "lat": user_lat,
                            "lon": user_lon,
                            "site_name": "You",
                            "type": "Your Location",
                        }
                    ]
                )

                map_df = pd.concat([map_df_sites, map_user], ignore_index=True)

                st.map(map_df[["lat", "lon"]])

                st.caption(
                    "Blue points show job sites; the additional point marks your location."
                )

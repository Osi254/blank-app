import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ====== PROBLEM STATEMENT ======
st.subheader("About")

st.markdown(
    """
    USC Builds operates in a fast-growing, public-sector–driven construction market across Upstate New York.  
    Despite strong demand, the business faces **high workforce volatility**, driven by:
    - Inconsistent **attendance** in key ZIP codes  
    - **Early exits** within the first 60 days, especially in field roles  
    - Low **retention** in critical, high-incident locations  

    These challenges create:
    - Scheduling risk and project delays  
    - Higher hiring and training costs  
    - Difficulty building a stable, community-based workforce  

    This platform was built to turn those challenges into **actionable insights** — so USC can
    **see risk early, intervene quickly, and plan confidently**.
    """
)

# ====== BUSINESS MODEL / VALUE PROPOSITION ======
st.subheader("💼 Business Model & Value Proposition")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        **Who this platform serves**
        - USC Builds leadership & executives  
        - HR & People Operations  
        - Project managers and site supervisors  

        **What the app delivers**
        - Attrition risk insights by **age, tenure, pay band, trade, and ZIP**
        - Visibility into **attendance incidents, leave spikes, and seasonal patterns**
        - Scenario views for **pay-floor changes, commute-adjusted staffing, and retention programs**
        """
    )

with col2:
    st.markdown(
        """
        **How it creates value**
        - Reduces costly **early exits** in key trades (Laborers, Finishers, Carpenters)  
        - Supports **pay-floor decisions** by quantifying how low wages drive attrition  
        - Highlights **high-risk ZIP codes** so commute and scheduling can be redesigned  
        - Turns raw HR and timecard data into a simple, repeatable **decision-support tool**  

        The long-term vision is to operate this as an internal
        **workforce strategy engine** for USC Builds — and, over time,
        as a scalable analytics product that can be extended to other
        community-focused contractors.
        """
    )

# ====== HOW TO USE THE APP ======
st.subheader("📊 What You Can Do in This App")

st.markdown(
    """
    - Explore **attendance and leave patterns** by month, ZIP, and employee segment  
    - Analyze **attrition drivers** across age, pay, tenure, and trade  
    - Identify **high-risk groups** for targeted retention initiatives  
    - Support **90-day roadmaps** and workforce planning with real data  

    Each page in the app is designed to answer a specific business question:
    > *Where are we losing people, why are they leaving, and what levers actually move the needle?*
    """
)

# ====== TEAM SECTION ======
st.subheader("👥 Project Team")

st.markdown("This platform was developed by the USC Builds analytics team at Simon Business School:")

team_cols = st.columns(3)

with team_cols[0]:
    st.markdown(
        """
        **Kavita Adha**  
        `kadha@Simon.rochester.edu`  

        **Mishika Bhandari**  
        `mbhanda6@Simon.rochester.edu`
        """
    )

with team_cols[1]:
    st.markdown(
        """
        **Omkarsinh Rana**  
        `orana@Simon.rochester.edu`  

        **Osigbemhe Ikhanoba**  
        `oikhanob@Simon.rochester.edu`
        """
    )

with team_cols[2]:
    st.markdown(
        """
        **Tanjina Moon**  
        `tmoon@Simon.rochester.edu`  

        **Omkar Sheth**  
        `osheth@Simon.rochester.edu`
        """
    )

st.markdown(
    """
    <br>
    <p style="font-size:0.9rem; color:#777;">
        Together, this team combined market research, HR analytics, and predictive modeling
        to build a platform that helps USC Builds turn workforce volatility into a strategic advantage.
    </p>
    """,
    unsafe_allow_html=True,
)
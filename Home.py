import streamlit as st
from pathlib import Path
from auth import get_role  # 👈 use the shared auth logic

# --------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------
st.set_page_config(
    page_title="USC Builds Workforce Analytics Dashboard",
    page_icon="🏗️",
    layout="wide",
)

# --------------------------------------------------------------------
# STYLES
# --------------------------------------------------------------------
st.markdown(
    """
    <style>
        .main-header {
            font-size: 40px;
            font-weight: 800;
            margin-bottom: 0;
        }
        .sub-header {
            font-size: 18px;
            color: #d0d0d0;
            margin-top: 4px;
            margin-bottom: 32px;
        }
        .login-card {
            padding: 1.5rem;
            border-radius: 0.75rem;
            background-color: #111318;
            border: 1px solid #2a2e35;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------
col_logo, col_title = st.columns([0.5, 4])

with col_logo:
    logo_path = Path("Tompkins_Profile_Logo_(1).png")
    if logo_path.exists():
        st.image(str(logo_path), width=90)
    else:
        st.write("🏗️")

with col_title:
    st.markdown(
        "<div class='main-header'>USC Builds Workforce Analytics Dashboard</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Analyze attendance, attrition, and workforce patterns.</div>",
        unsafe_allow_html=True,
    )
    



# --------------------------------------------------------------------
# LOGIN – CLEAN VERSION (NO LOCK ICON, NO MESSAGES)
# --------------------------------------------------------------------
login_col, _ = st.columns([2, 3])

from auth import get_role  # still uses your EMPLOYEE_PASSWORD and HR_PASSWORD

with login_col:
 

    # get_role() handles checking EMPLOYEE_PASSWORD / HR_PASSWORD
    role = get_role()

    if role is None:
        st.info("Enter password to continue.")  # Clean + professional, no HR warning
    else:
        st.success(f"✅ Logged in as **{role}**.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------------------------
# WORKFLOW LINKS – ROLE-BASED
# --------------------------------------------------------------------
st.markdown("#### Choose a workflow below:")

if role is None:
    st.warning(
        "Workflows are hidden until you log in. "
        "Enter the correct password above to unlock navigation."
    )
else:
    # Role flags
    is_hr = role == "HR"
    is_employee = role == "Employee"

    # HR gets everything, Employee gets a subset
    # Row 1
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)

    with r1c1:
        st.page_link(
            "pages/About.py",
            label="📘 About",
            help="Overview of the USC Builds Workforce Analytics Capstone app.",
        )

    with r1c2:
        if is_hr:
            st.page_link(
                "pages/Analysis.py",
                label="📊 Workforce Analysis",
                help="Attendance, attrition, and workforce KPIs. (HR only)",
            )
        else:
            st.write("📊 Workforce Analysis\n\n_(HR only)_")

    with r1c3:
        st.page_link(
            "pages/Employee_Punch.py",
            label="⏱️ Employee Punch",
            help="Clock-in and clock-out module for workers.",
        )

    with r1c4:
        st.page_link(
            "pages/Feedback.py",
            label="📝 Feedback",
            help="Capture qualitative feedback from employees and supervisors.",
        )

    st.write("")

    # Row 2
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)

    with r2c1:
        st.page_link(
            "pages/Find_Jobs_Near_Me.py",
            label="📍 Find Jobs Near Me",
            help="Search for nearby job sites using ZIP code and distance.",
        )

    with r2c2:
        if is_hr:
            st.page_link(
                "pages/HR_Job_Sites.py",
                label="🗂️ HR – Job Sites",
                help="Manage and inspect construction job sites. (HR only)",
            )
        else:
            st.write("🗂️ HR – Job Sites\n\n_(HR only)_")

    with r2c3:
        st.page_link(
            "pages/Training_Path.py",
            label="🎓 Training Path",
            help="Recommended training and career development paths.",
        )

    with r2c4:
        st.empty()

# --------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------
st.markdown("---")
st.caption(
    "USC Builds Workforce Analytics • Simon Business School Capstone Project • Built with Streamlit."
)
# 

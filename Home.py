import streamlit as st
from pathlib import Path

# --------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------
st.set_page_config(
    page_title="USC Builds Workforce Analytics Dashboard",
    page_icon="🏗️",
    layout="wide",
)

# --------------------------------------------------------------------
# SIMPLE PASSWORD (CHANGE THIS OR USE SECRETS)
# --------------------------------------------------------------------
DEFAULT_PASSWORD = "uscbuilds"  # change this

def get_app_password() -> str:
    try:
        return st.secrets.get("app_password", DEFAULT_PASSWORD)
    except Exception:
        return DEFAULT_PASSWORD


if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False


def check_password():
    entered = st.session_state.get("password_input", "")
    if not entered:
        st.warning("Please enter a password.")
        return
    if entered == get_app_password():
        st.session_state.is_authenticated = True
        st.success("Login successful. You can now access all pages from the sidebar.")
    else:
        st.session_state.is_authenticated = False
        st.error("Incorrect password. Please try again.")


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
        .login-box {
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

st.markdown("### USC Builds Workforce App")

# --------------------------------------------------------------------
# WORKFLOW LINKS – ALL ICONS / ALL PAGES
#   This assumes your pages are named:
#   pages/About.py
#   pages/Analysis.py
#   pages/Employee_Punch.py
#   pages/Feedback.py
#   pages/Find_Jobs_Near_Me.py
#   pages/HR_Job_Sites.py
#   pages/Training_Path.py
# --------------------------------------------------------------------
st.markdown("#### Choose a workflow below:")

# Row 1: About, Analysis, Employee Punch, Feedback
r1c1, r1c2, r1c3, r1c4 = st.columns(4)

with r1c1:
    st.page_link(
        "pages/About.py",
        label="📘 About",
        help="Overview of the USC Builds Workforce Analytics Capstone app.",
    )

with r1c2:
    st.page_link(
        "pages/Analysis.py",
        label="📊 Workforce Analysis",
        help="Attendance, attrition, and workforce KPIs.",
    )

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

st.write("")  # spacer

# Row 2: Find Jobs Near Me, HR Job Sites, Training Path
r2c1, r2c2, r2c3, r2c4 = st.columns(4)

with r2c1:
    st.page_link(
        "pages/Find_Jobs_Near_Me.py",
        label="📍 Find Jobs Near Me",
        help="Search for nearby job sites using ZIP code and distance.",
    )

with r2c2:
    st.page_link(
        "pages/HR_Job_Sites.py",
        label="🗂️ HR – Job Sites",
        help="Manage and inspect construction job sites.",
    )

with r2c3:
    st.page_link(
        "pages/Training_Path.py",
        label="🎓 Training Path",
        help="Recommended training and career development paths.",
    )

with r2c4:
    st.empty()  # keeps layout balanced

st.write("")

# --------------------------------------------------------------------
# LOGIN
# --------------------------------------------------------------------
st.markdown("## 🔐 Login")

with st.container():
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.write("Enter password to unlock sensitive HR analytics pages.")

    st.text_input(
        "Enter password",
        type="password",
        key="password_input",
        placeholder="••••••••",
    )
    st.button("Login", on_click=check_password)

    if st.session_state.is_authenticated:
        st.success("✅ Access granted. Use the left sidebar to switch pages.")
    else:
        st.info(
            "Access is limited until you log in. Contact the capstone team if you need credentials."
        )

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------
st.markdown("---")
st.caption(
    "USC Builds Workforce Analytics • Simon Business School Capstone Project • Built with Streamlit."
)


# streamlit run Home.py --server.address 0.0.0.0 --server.port 8501

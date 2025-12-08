import streamlit as st

def _get_secret(name: str, default: str) -> str:
    try:
        return st.secrets[name]
    except Exception:
        return default

# 👉 Defaults: Employee = "123", HR = "hrsuperpass"
EMPLOYEE_PASSWORD = _get_secret("EMPLOYEE_PASSWORD", "123")
HR_PASSWORD = _get_secret("HR_PASSWORD", "hrsuperpass")


def get_role():
    """Role-based login with a Try Again button for wrong passwords."""
    # If already logged in, just return the saved role
    if "role" in st.session_state:
        return st.session_state["role"]

    # Init state
    if "login_error" not in st.session_state:
        st.session_state.login_error = False
    if "login_attempt" not in st.session_state:
        st.session_state.login_attempt = 0

    st.markdown("### 🔐 Login")

    # Change the input key when user clicks "Try Again" so box resets
    input_key = f"password_input_{st.session_state.login_attempt}"

    password = st.text_input(
        "Enter password",
        type="password",
        key=input_key,
    )

    # Login button
    if st.button("Login"):
        if password == EMPLOYEE_PASSWORD:
            st.session_state["role"] = "Employee"
            st.session_state.login_error = False
            st.rerun()

        elif password == HR_PASSWORD:
            st.session_state["role"] = "HR"
            st.session_state.login_error = False
            st.rerun()

        else:
            st.session_state.login_error = True

    # If wrong password → show error + Try Again button
    if st.session_state.login_error:
        st.error("❌ Incorrect password")

        if st.button("🔄 Try Again"):
            st.session_state.login_attempt += 1
            st.session_state.login_error = False
            st.rerun()

    return None



import streamlit as st
import pandas as pd

st.set_page_config(page_title="Employee Training Path", layout="wide")

st.title("Career Path Simulator")
st.write(
    """
    Track how an employee can progress from **Surveyor** to a higher role using 
    training programs, and compare training strategies using simple game-theory logic.
    """
)

# ---------------------------------------------------------
# 1. Define a simple career ladder for a Surveyor
# ---------------------------------------------------------

career_path = [
    {
        "level": 1,
        "job_title": "Surveyor",
        "skills": ["Site surveying", "Blueprint reading", "Basic safety"],
        "required_trainings": ["OSHA Safety Basics", "Intro to Site Surveying"],
        "avg_time_years": 0,  # starting point
        "salary_index": 1.0,
    },
    {
        "level": 2,
        "job_title": "Field Engineer",
        "skills": ["Layout control", "RFI documentation", "Material tracking"],
        "required_trainings": ["Field Engineering 101", "Construction Documentation"],
        "avg_time_years": 1.5,
        "salary_index": 1.3,
    },
    {
        "level": 3,
        "job_title": "Assistant Project Manager",
        "skills": ["Scheduling", "Subcontractor coordination", "Cost tracking"],
        "required_trainings": [
            "Project Scheduling (Primavera/MS Project)",
            "Cost Control Fundamentals",
        ],
        "avg_time_years": 3,
        "salary_index": 1.7,
    },
    {
        "level": 4,
        "job_title": "Project Manager",
        "skills": ["Client management", "Budget ownership", "Risk management"],
        "required_trainings": [
            "Advanced Project Management",
            "Contracts & Risk in Construction",
        ],
        "avg_time_years": 5,
        "salary_index": 2.2,
    },
]

path_df = pd.DataFrame(career_path)

# ---------------------------------------------------------
# 2. Inputs – employee & target role
# ---------------------------------------------------------

with st.sidebar:
    st.header("🎯 Employee Setup")

    employee_name = st.text_input("Employee Name", "John Doe")
    employee_id = st.text_input("Employee ID (optional)", "E-001")

    current_role = "Surveyor"  # fixed starting point for now
    st.markdown(f"**Current Role:** `{current_role}`")

    target_role = st.selectbox(
        "Target Role",
        options=path_df["job_title"].tolist()[1:],  # everything above Surveyor
        index=2,  # defaults to Assistant PM (0-based) or change to 2 for Project Manager
    )

    risk_preference = st.slider(
        "Risk Preference (0 = very risk-averse, 1 = very risk-taking)",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.1,
    )

    planning_horizon_years = st.slider(
        "Planning Horizon (years)", 1, 10, 5
    )

# ---------------------------------------------------------
# 3. Build the path from Surveyor to target role
# ---------------------------------------------------------

# Filter from Surveyor up to target
start_idx = path_df[path_df["job_title"] == current_role].index[0]
end_idx = path_df[path_df["job_title"] == target_role].index[0]

path_slice = path_df.loc[start_idx : end_idx].reset_index(drop=True)

st.subheader(f"📍 Career Path: {current_role} → {target_role}")

col_summary, col_path = st.columns([1, 2])

with col_summary:
    num_jobs = path_slice.shape[0]
    total_years = path_slice["avg_time_years"].iloc[-1] - path_slice["avg_time_years"].iloc[0]
    total_salary_index = path_slice["salary_index"].iloc[-1]

    st.metric("Number of Roles in Path", num_jobs)
    st.metric("Approx. Years to Target", f"{total_years:.1f} years")
    st.metric("Target Salary Index", f"{total_salary_index:.1f}x from starting point")

    st.write(
        f"**{employee_name}** will move through **{num_jobs} roles** to reach **{target_role}**, "
        f"with an estimated timeline of **~{total_years:.1f} years** assuming steady progress."
    )

with col_path:
    display_df = path_slice.copy()
    display_df["skills"] = display_df["skills"].apply(lambda x: ", ".join(x))
    display_df["required_trainings"] = display_df["required_trainings"].apply(
        lambda x: ", ".join(x)
    )
    st.dataframe(
        display_df[
            ["level", "job_title", "skills", "required_trainings", "avg_time_years", "salary_index"]
        ].rename(
            columns={
                "level": "Level",
                "job_title": "Job Title",
                "skills": "Key Skills",
                "required_trainings": "Required Trainings",
                "avg_time_years": "Avg Time (Years)",
                "salary_index": "Salary Index",
            }
        ),
        use_container_width=True,
    )

st.markdown("---")

# ---------------------------------------------------------
# 4. Game-theory-inspired training strategies
# ---------------------------------------------------------
st.subheader("🎮 Training Strategy Game (Fast Track vs Safe Track)")

st.write(
    """
    We compare two simple strategies for this employee:
    
    - **Fast Track**: Heavier training load now, higher promotion speed, but more burnout risk.  
    - **Safe Track**: Balanced workload, slower promotions, lower risk.
    
    We use a simple payoff model depending on:
    - Time to reach target role  
    - Probability of successfully completing trainings  
    - Burnout risk (penalty if risk preference is low)
    """
)

# Define simple payoffs (normalized)
# These are toy numbers just to make the logic concrete.
strategy_data = [
    {
        "strategy": "Fast Track",
        "expected_years_to_target": max(total_years * 0.7, 1.0),   # faster
        "promotion_probability": 0.8,
        "burnout_risk": 0.6,  # higher
    },
    {
        "strategy": "Safe Track",
        "expected_years_to_target": total_years * 1.1,            # slower
        "promotion_probability": 0.65,
        "burnout_risk": 0.25,  # lower
    },
]

strategies_df = pd.DataFrame(strategy_data)

# Simple payoff function:
# payoff = + (weight on prob * promotion_probability)
#          - (weight on time * expected_years_to_target / planning_horizon)
#          - (weight on burnout * burnout_risk)
#
# Risk-averse (risk_preference small) -> burnout penalty is high
# Risk-taking (risk_preference high) -> burnout penalty is lower, speed & promotion more attractive

def compute_payoff(row, risk_pref, horizon_years):
    # Normalize horizon to avoid blowing up value
    time_penalty = row["expected_years_to_target"] / max(horizon_years, 1)

    # Weights shift with risk preference
    w_prob = 0.5 + 0.2 * risk_pref          # more risk-taking -> more weight on promotion probability
    w_time = 0.3 + 0.2 * risk_pref          # risk-takers also care more about speed
    w_burnout = 0.5 - 0.4 * risk_pref       # risk-averse -> high burnout penalty

    payoff = (
        w_prob * row["promotion_probability"]
        - w_time * time_penalty
        - w_burnout * row["burnout_risk"]
    )
    return payoff

strategies_df["payoff"] = strategies_df.apply(
    lambda r: compute_payoff(r, risk_preference, planning_horizon_years), axis=1
)

best_strategy_row = strategies_df.loc[strategies_df["payoff"].idxmax()]

col_left, col_right = st.columns(2)

with col_left:
    st.write("### Strategy Comparison")
    st.dataframe(
        strategies_df[
            [
                "strategy",
                "expected_years_to_target",
                "promotion_probability",
                "burnout_risk",
                "payoff",
            ]
        ]
        .rename(
            columns={
                "strategy": "Strategy",
                "expected_years_to_target": "Expected Years to Target",
                "promotion_probability": "Promotion Probability",
                "burnout_risk": "Burnout Risk",
                "payoff": "Utility (Payoff)",
            }
        )
        .style.format(
            {
                "Expected Years to Target": "{:.1f}",
                "Promotion Probability": "{:.0%}",
                "Burnout Risk": "{:.0%}",
                "Utility (Payoff)": "{:.3f}",
            }
        ),
        use_container_width=True,
    )

with col_right:
    st.write("### Recommended Strategy")

    st.success(
        f"For **{employee_name}** with a risk preference of **{risk_preference:.1f}**, "
        f"the recommended training strategy is:\n\n"
        f"👉 **{best_strategy_row['strategy']}**"
    )

    st.write(
        f"- Expected years to reach **{target_role}**: "
        f"**{best_strategy_row['expected_years_to_target']:.1f} years**\n"
        f"- Promotion probability: **{best_strategy_row['promotion_probability']:.0%}**\n"
        f"- Burnout risk: **{best_strategy_row['burnout_risk']:.0%}**\n"
    )

st.markdown("---")
st.caption(
    "This is a simplified model – in a real system, you’d plug in actual training data, "
    "historical promotion rates, and performance metrics."
)

import streamlit as st
import pandas as pd
import random

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Employee Training Path",
    layout="wide",
    page_icon="🎓",
)

st.title("🎓 Career Path Simulator")

st.write(
    """
    Run a **Quick Skill Check**and see the recommended **Training Strategy** .
    """
)

# -------------------------------------------------
# 1. CAREER LADDERS (FIELD, CARPENTRY, PLUMBING)
#    (In production, this could come from career_paths.csv)
# -------------------------------------------------
career_path_data = [
    # FIELD / MANAGEMENT LADDER
    {
        "ladder": "Field Management",
        "level": 1,
        "job_title": "Surveyor",
        "skills": ["Site surveying", "Blueprint reading", "Basic safety"],
        "required_trainings": ["OSHA Safety Basics", "Intro to Site Surveying"],
        "avg_time_years": 0.0,
        "salary_index": 1.0,
    },
    {
        "ladder": "Field Management",
        "level": 2,
        "job_title": "Field Engineer",
        "skills": ["Layout control", "RFI documentation", "Material tracking"],
        "required_trainings": ["Field Engineering 101", "Construction Documentation"],
        "avg_time_years": 1.5,
        "salary_index": 1.3,
    },
    {
        "ladder": "Field Management",
        "level": 3,
        "job_title": "Assistant Project Manager",
        "skills": ["Scheduling", "Subcontractor coordination", "Cost tracking"],
        "required_trainings": [
            "Project Scheduling (Primavera/MS Project)",
            "Cost Control Fundamentals",
        ],
        "avg_time_years": 3.0,
        "salary_index": 1.7,
    },
    {
        "ladder": "Field Management",
        "level": 4,
        "job_title": "Project Manager",
        "skills": ["Client management", "Budget ownership", "Risk management"],
        "required_trainings": [
            "Advanced Project Management",
            "Contracts & Risk in Construction",
        ],
        "avg_time_years": 5.0,
        "salary_index": 2.2,
    },

    # CARPENTRY LADDER
    {
        "ladder": "Carpentry",
        "level": 1,
        "job_title": "Carpenter Apprentice",
        "skills": ["Basic framing", "Hand tools", "Jobsite safety"],
        "required_trainings": ["Carpentry Safety", "Intro to Framing"],
        "avg_time_years": 0.0,
        "salary_index": 1.0,
    },
    {
        "ladder": "Carpentry",
        "level": 2,
        "job_title": "Carpenter Journeyman",
        "skills": ["Advanced framing", "Reading plans", "Crew coordination"],
        "required_trainings": ["Advanced Carpentry", "Blueprint Reading"],
        "avg_time_years": 2.0,
        "salary_index": 1.4,
    },
    {
        "ladder": "Carpentry",
        "level": 3,
        "job_title": "Carpenter Foreman",
        "skills": ["Crew leadership", "Quality control", "Daily planning"],
        "required_trainings": ["Field Leadership Basics", "Quality in Carpentry"],
        "avg_time_years": 4.0,
        "salary_index": 1.8,
    },
    {
        "ladder": "Carpentry",
        "level": 4,
        "job_title": "General Superintendent – Carpentry",
        "skills": ["Multi-crew coordination", "Schedule control", "Site logistics"],
        "required_trainings": ["Superintendent Bootcamp", "Advanced Scheduling"],
        "avg_time_years": 6.0,
        "salary_index": 2.3,
    },

    # PLUMBING LADDER
    {
        "ladder": "Plumbing",
        "level": 1,
        "job_title": "Plumber Apprentice",
        "skills": ["Basic piping", "Tool handling", "Safety & PPE"],
        "required_trainings": ["Plumbing Safety", "Intro to Piping"],
        "avg_time_years": 0.0,
        "salary_index": 1.0,
    },
    {
        "ladder": "Plumbing",
        "level": 2,
        "job_title": "Plumber Journeyman",
        "skills": ["Pipe installation", "Reading plumbing plans", "Code compliance"],
        "required_trainings": ["Plumbing Codes", "Advanced Piping"],
        "avg_time_years": 2.5,
        "salary_index": 1.5,
    },
    {
        "ladder": "Plumbing",
        "level": 3,
        "job_title": "Plumbing Foreman",
        "skills": ["Crew scheduling", "Material planning", "Inspection prep"],
        "required_trainings": ["Field Leadership – Plumbing", "Material Management"],
        "avg_time_years": 4.5,
        "salary_index": 1.9,
    },
    {
        "ladder": "Plumbing",
        "level": 4,
        "job_title": "General Superintendent – Plumbing",
        "skills": ["Multiple crews", "Budget input", "Coordination with GC"],
        "required_trainings": ["Superintendent Bootcamp", "Contracts Basics"],
        "avg_time_years": 6.5,
        "salary_index": 2.4,
    },
]

path_df = pd.DataFrame(career_path_data)

# NOTE: In production you could move this to:
# career_paths.csv with columns:
# ladder, level, job_title, skills (pipe-separated), required_trainings (pipe-separated),
# avg_time_years, salary_index


# -------------------------------------------------
# 2. SIDEBAR – EMPLOYEE + ROLE SELECTION
# -------------------------------------------------
with st.sidebar:
    st.header("🎯 Employee Setup")

    employee_name = st.text_input("Employee name", "John Doe")
    employee_id = st.text_input("Employee ID (optional)", "E-001")

    all_roles = path_df["job_title"].tolist()
    current_role = st.selectbox("Current role", options=all_roles, index=0)

    current_row = path_df[path_df["job_title"] == current_role].iloc[0]
    current_ladder = current_row["ladder"]
    current_level = current_row["level"]

    # Only allow target roles within the same ladder above current level
    allowed_targets = path_df[
        (path_df["ladder"] == current_ladder) & (path_df["level"] > current_level)
    ]["job_title"].tolist()

    if not allowed_targets:
        st.error(
            "There is no higher role defined above this one yet in this ladder. "
            "Add more roles to the data to unlock new paths."
        )
        st.stop()

    target_role = st.selectbox(
        "Target role",
        options=allowed_targets,
        index=len(allowed_targets) - 1,
        help=f"Target within the {current_ladder} ladder.",
    )

    risk_preference = st.slider(
        "Risk comfort (0 = very cautious, 1 = loves stretch goals)",
        0.0,
        1.0,
        0.4,
        0.1,
    )

    planning_horizon_years = st.slider(
        "Planning horizon (years)",
        1,
        10,
        5,
    )

# -------------------------------------------------
# 3. BUILD PATH FROM CURRENT → TARGET
# -------------------------------------------------
# Filter this ladder and order by level
ladder_df = path_df[path_df["ladder"] == current_ladder].sort_values("level")

start_idx = ladder_df[ladder_df["job_title"] == current_role].index[0]
end_idx = ladder_df[ladder_df["job_title"] == target_role].index[0]

path_slice = ladder_df.loc[start_idx:end_idx].reset_index(drop=True)

num_levels = path_slice.shape[0]
start_years = path_slice["avg_time_years"].iloc[0]
end_years = path_slice["avg_time_years"].iloc[-1]
total_years = end_years - start_years
target_salary_index = (
    path_slice["salary_index"].iloc[-1] / path_slice["salary_index"].iloc[0]
)

base_years = start_years

# -------------------------------------------------
# 4. QUICK SKILL CHECK (5 QUESTIONS, ONE AT A TIME)
#    In production, move questions to skill_questions.csv:
#    ladder, target_role, question_id, question, option_a, option_b, option_c, option_d,
#    correct_option (A/B/C/D), explanation, empathy_success, empathy_fail
# -------------------------------------------------

st.subheader("🧠 Quick Skill Check")

st.write(
    f"Short quiz (5 questions) to test readiness for **{target_role}** "
    f"in the **{current_ladder}** ladder."
)

# ---- Question bank in code (could be loaded from CSV) ----
# Each entry is a dict with question, options, answer, explanation, empathy messages.
question_bank = {
    "Field Engineer": [
        {
            "question": "On a typical day, what is a Field Engineer MOST likely doing?",
            "options": [
                "Reviewing layout and setting control points",
                "Negotiating the prime contract with the client",
                "Running payroll for the whole company",
                "Designing the corporate website",
            ],
            "answer": "Reviewing layout and setting control points",
            "explanation": "Field Engineers live in layout, RFIs, and site coordination.",
            "success": [
                "Nice — you’re already thinking like a Field Engineer.",
                "Strong answer. Layout and control points are key.",
            ],
            "fail": [
                "Close. Field Engineers are all about layout and site details.",
                "Good try. Think about who manages drawings and field questions.",
            ],
        },
        {
            "question": "Which document do Field Engineers touch ALL the time?",
            "options": [
                "RFIs (Requests for Information)",
                "Tax returns",
                "Travel expense policies",
                "Brand guidelines",
            ],
            "answer": "RFIs (Requests for Information)",
            "explanation": "RFIs clear up questions between field and design.",
            "success": [
                "Exactly. RFIs are part of your daily diet as a FE.",
                "Correct — RFIs are a core part of site communication.",
            ],
            "fail": [
                "Almost. RFIs are what connect field issues to design.",
                "Not quite. Field Engineers live in RFIs and drawings.",
            ],
        },
        {
            "question": "A trade foreman flags a conflict in the drawings. What do you do first?",
            "options": [
                "Review the drawings and create an RFI if needed",
                "Tell them to just build it anyway",
                "Ignore it and hope it disappears",
                "Escalate straight to the CEO",
            ],
            "answer": "Review the drawings and create an RFI if needed",
            "explanation": "Good Field Engineers make sure conflicts get documented and resolved.",
            "success": [
                "Good call — document it and push it through the right channel.",
                "Exactly. That’s how you de-risk field issues.",
            ],
            "fail": [
                "Careful. Ignoring or bypassing process causes rework later.",
                "Not quite. You want the issue documented and clarified.",
            ],
        },
        {
            "question": "Which metric best shows you’re winning as a Field Engineer?",
            "options": [
                "Few layout errors and rework calls",
                "Number of times you stay late",
                "Amount of coffee consumed",
                "How many emails you send",
            ],
            "answer": "Few layout errors and rework calls",
            "explanation": "Quality layout reduces rework and stress for everyone.",
            "success": [
                "Nice. Less rework = strong field engineering.",
                "Exactly. Clean layout = fewer headaches.",
            ],
            "fail": [
                "Not quite. Impact matters more than hours or emails.",
                "Good effort. Think quality and rework, not noise.",
            ],
        },
        {
            "question": "Who do you work with MOST closely as a Field Engineer?",
            "options": [
                "Superintendent and trade foremen",
                "Bank tellers",
                "Graphic designers",
                "Call center agents",
            ],
            "answer": "Superintendent and trade foremen",
            "explanation": "Field Engineers sit between superintendents, trades, and design.",
            "success": [
                "Correct — you live next to supers and foremen.",
                "Exactly. You’re part of the field operations core.",
            ],
            "fail": [
                "Not quite. Think boots-on-the-ground leadership.",
                "Close. Field Engineers spend time with supers and foremen.",
            ],
        },
    ],
    "Assistant Project Manager": [
        {
            "question": "What is a core responsibility of an Assistant Project Manager?",
            "options": [
                "Tracking schedule updates and subcontractor progress",
                "Pouring concrete personally",
                "Drafting structural calculations",
                "Running the company cafeteria",
            ],
            "answer": "Tracking schedule updates and subcontractor progress",
            "explanation": "APMs live in schedules, costs, and coordination.",
            "success": [
                "Yes — that’s APM 101.",
                "Correct. You’re thinking like a project manager in training.",
            ],
            "fail": [
                "Almost. APMs focus heavily on schedule and subs.",
                "Not quite. Look for coordination and tracking.",
            ],
        },
        {
            "question": "An invoice from a subcontractor looks higher than expected. Your move?",
            "options": [
                "Compare it to the contract and work completed",
                "Approve it immediately to stay friends",
                "Throw it away",
                "Forward it without looking",
            ],
            "answer": "Compare it to the contract and work completed",
            "explanation": "APMs protect project costs and align invoices with scope.",
            "success": [
                "Nice. That’s cost control thinking.",
                "Exactly. Contracts and progress should match the invoice.",
            ],
            "fail": [
                "Careful. Blind approvals kill margin.",
                "Not quite. You want to match invoice to contract and work.",
            ],
        },
        {
            "question": "Which meeting is the APM MOST likely to run?",
            "options": [
                "Subcontractor coordination meeting",
                "Executive board meeting",
                "Company-wide town hall",
                "Holiday party planning",
            ],
            "answer": "Subcontractor coordination meeting",
            "explanation": "APMs own daily/weekly coordination with subs.",
            "success": [
                "Correct — that’s your arena as an APM.",
                "Exactly. You’re the traffic controller for subs.",
            ],
            "fail": [
                "Close. Think of the person in charge of aligning subs.",
                "Not quite. APMs are in the weeds with subs, not the board.",
            ],
        },
        {
            "question": "RFI turnaround times are slipping. What’s a smart APM move?",
            "options": [
                "Flag the issue, track RFIs, and push for priorities",
                "Ignore it; it will fix itself",
                "Blame the trades",
                "Complain in group chat only",
            ],
            "answer": "Flag the issue, track RFIs, and push for priorities",
            "explanation": "APMs keep information flowing to protect schedule.",
            "success": [
                "Nice — that’s proactive APM behavior.",
                "Exactly. You manage the information pipeline.",
            ],
            "fail": [
                "Careful. Waiting usually hurts the schedule.",
                "Not quite. APMs jump on bottlenecks.",
            ],
        },
        {
            "question": "Which tool would an APM use MOST?",
            "options": [
                "Project schedule (Primavera/MS Project)",
                "Arc welding machine",
                "Paint sprayer",
                "Lathe",
            ],
            "answer": "Project schedule (Primavera/MS Project)",
            "explanation": "APMs live in schedules and cost tracking tools.",
            "success": [
                "Correct — that’s your dashboard.",
                "Exactly. Schedules are your steering wheel.",
            ],
            "fail": [
                "Close, but APMs aren’t running tools in the field.",
                "Not quite. APMs spend more time in schedules than on equipment.",
            ],
        },
    ],
    "Project Manager": [
        {
            "question": "What is the Project Manager ultimately accountable for?",
            "options": [
                "Safety, schedule, budget, and client outcome",
                "Only what happens at night on site",
                "Picking paint colors",
                "Scheduling cafeteria menus",
            ],
            "answer": "Safety, schedule, budget, and client outcome",
            "explanation": "PMs own the whole job — cost, time, safety, client.",
            "success": [
                "Exactly. That’s the PM seat.",
                "Correct — full project accountability.",
            ],
            "fail": [
                "Close. Think end-to-end project responsibility.",
                "Not quite. PMs own the big four: cost, time, safety, client.",
            ],
        },
        {
            "question": "A PM’s best use of time in a crisis is usually to…",
            "options": [
                "Re-align priorities and unblock the team",
                "Personally install piping",
                "Design site logos",
                "Hide in the office",
            ],
            "answer": "Re-align priorities and unblock the team",
            "explanation": "PMs clear roadblocks and keep the team moving.",
            "success": [
                "Nice — leadership mode.",
                "Exactly. PMs remove obstacles, not just tasks.",
            ],
            "fail": [
                "Careful. PMs shouldn’t disappear into technical tasks.",
                "Not quite. The PM’s job is to unblock others.",
            ],
        },
        {
            "question": "Which meeting does the PM absolutely need to be sharp in?",
            "options": [
                "Owner/Client progress meeting",
                "Office birthday planning",
                "Breakroom gossip",
                "Fantasy football draft",
            ],
            "answer": "Owner/Client progress meeting",
            "explanation": "PMs own the relationship and message to the client.",
            "success": [
                "Correct. That’s where trust is built.",
                "Exactly. PMs speak for the job to the client.",
            ],
            "fail": [
                "Not quite. Think client, not internal fun.",
                "Close. The PM is the voice of the project to the owner.",
            ],
        },
        {
            "question": "Margin is dropping on the job. What should the PM do?",
            "options": [
                "Dig into cost reports and forecast, then act",
                "Ignore it and hope for good luck",
                "Blame one random trade",
                "Buy everyone pizza",
            ],
            "answer": "Dig into cost reports and forecast, then act",
            "explanation": "PMs protect margin by understanding and acting on cost data.",
            "success": [
                "Nice — eyes on cost and forecast.",
                "Exactly. You protect the job’s financial health.",
            ],
            "fail": [
                "Careful. Margin doesn’t fix itself.",
                "Not quite. PMs must understand and act on cost reports.",
            ],
        },
        {
            "question": "Who are PMs constantly balancing?",
            "options": [
                "Client, trades, internal team, and executives",
                "Only themselves",
                "Only the concrete supplier",
                "Only IT support",
            ],
            "answer": "Client, trades, internal team, and executives",
            "explanation": "PMs juggle multiple stakeholders every week.",
            "success": [
                "Correct — that’s the stakeholder circus.",
                "Exactly. PMs translate across all groups.",
            ],
            "fail": [
                "Close. Think bigger than one group.",
                "Not quite. PMs sit at the center of all stakeholders.",
            ],
        },
    ],
    "Carpenter Foreman": [
        {
            "question": "What is a Carpenter Foreman mainly responsible for?",
            "options": [
                "Leading the carpentry crew and hitting daily goals",
                "Designing the building architecture",
                "Running company payroll",
                "Managing IT systems",
            ],
            "answer": "Leading the carpentry crew and hitting daily goals",
            "explanation": "Foremen turn plans into daily execution on site.",
            "success": [
                "Exactly — crew + daily production.",
                "Nice. You’re thinking like a front-line leader.",
            ],
            "fail": [
                "Not quite. Foremen lead crews, not office systems.",
                "Close. Focus on crew leadership and output.",
            ],
        },
        {
            "question": "A good Foreman checks what at the start of the day?",
            "options": [
                "Crew, scope for the day, materials, and safety",
                "Cafeteria menu",
                "Weather in another country",
                "Stock market",
            ],
            "answer": "Crew, scope for the day, materials, and safety",
            "explanation": "Good days start with clear scope, tools, and safe setup.",
            "success": [
                "Correct — that’s a strong start-up routine.",
                "Exactly. That’s how you prevent chaos.",
            ],
            "fail": [
                "Almost. Think about what keeps work flowing smoothly.",
                "Not quite. Foremen own scope, crew, and safety checks.",
            ],
        },
        {
            "question": "Which KPI matters most to a Carpenter Foreman?",
            "options": [
                "Daily production vs. plan",
                "Number of memes sent",
                "Size of their office",
                "How often they change hard hats",
            ],
            "answer": "Daily production vs. plan",
            "explanation": "Foremen live in production vs. schedule.",
            "success": [
                "Nice — that’s the number that tells the story.",
                "Correct. Output vs. plan is everything.",
            ],
            "fail": [
                "Not quite. Think output, not noise.",
                "Close. Look for production vs. planned work.",
            ],
        },
        {
            "question": "A new carpenter is struggling. Best response?",
            "options": [
                "Coach them on the task and safety, then check back",
                "Yell and send them home",
                "Ignore it",
                "Give them an unrelated task forever",
            ],
            "answer": "Coach them on the task and safety, then check back",
            "explanation": "Foremen build people, not just buildings.",
            "success": [
                "Exactly. Coaching builds a stronger crew.",
                "Nice — that’s how you grow talent safely.",
            ],
            "fail": [
                "Careful. Fear doesn’t build skill.",
                "Not quite. Coaching beats ignoring or yelling.",
            ],
        },
        {
            "question": "Who does the Carpenter Foreman talk to most?",
            "options": [
                "Their crew and the superintendent",
                "Bank tellers",
                "Marketing team",
                "Software developers",
            ],
            "answer": "Their crew and the superintendent",
            "explanation": "Foremen are the bridge between crew and site leadership.",
            "success": [
                "Correct — you sit between crew and super.",
                "Exactly. You’re the voice of your crew.",
            ],
            "fail": [
                "Not quite. Think field-facing relationships.",
                "Close. Foremen connect crew to supers.",
            ],
        },
    ],
    "Plumbing Foreman": [
        {
            "question": "What is a Plumbing Foreman’s main job?",
            "options": [
                "Lead the plumbing crew and keep installs on schedule",
                "Design company logos",
                "Approve all company bonuses",
                "Clean the parking lot",
            ],
            "answer": "Lead the plumbing crew and keep installs on schedule",
            "explanation": "Plumbing Foremen own crew performance and schedule.",
            "success": [
                "Exactly. Crew + schedule is your world.",
                "Nice — that’s a foreman mindset.",
            ],
            "fail": [
                "Not quite. Think crew leadership and installs.",
                "Close. Focus on plumbing work and schedule.",
            ],
        },
        {
            "question": "Inspection is tomorrow. What should you focus on?",
            "options": [
                "Checking work against code and plans",
                "Picking music for the radio",
                "Buying new shoes",
                "Redesigning the logo",
            ],
            "answer": "Checking work against code and plans",
            "explanation": "Passing inspection starts with code-compliant installs.",
            "success": [
                "Correct — that’s how you avoid fails.",
                "Exactly. Code and plans first.",
            ],
            "fail": [
                "Careful. Failed inspections cost time and money.",
                "Not quite. Think about what inspectors care about.",
            ],
        },
        {
            "question": "Which material issue should a Plumbing Foreman watch hardest?",
            "options": [
                "Running low on pipe/fittings that block tomorrow’s work",
                "Color of office chairs",
                "Number of coffee pods",
                "Sticker designs",
            ],
            "answer": "Running low on pipe/fittings that block tomorrow’s work",
            "explanation": "Material gaps kill production.",
            "success": [
                "Nice — that’s the bottleneck to avoid.",
                "Correct. Materials drive tomorrow’s progress.",
            ],
            "fail": [
                "Not quite. Think what stops tomorrow’s work.",
                "Close. Focus on materials tied to planned tasks.",
            ],
        },
        {
            "question": "Your crew finishes early. Best move?",
            "options": [
                "Prep tomorrow’s work area and materials",
                "Send everyone home without planning",
                "Do nothing",
                "Start a random task with no plan",
            ],
            "answer": "Prep tomorrow’s work area and materials",
            "explanation": "Good foremen use slack time to get ahead.",
            "success": [
                "Exactly — tomorrow starts today.",
                "Nice. That’s proactive leadership.",
            ],
            "fail": [
                "Not quite. Use extra time to get ahead, not coast.",
                "Close. Think about making tomorrow smoother.",
            ],
        },
        {
            "question": "Who do you coordinate with to avoid clashes in ceilings?",
            "options": [
                "Other trade foremen and the superintendent",
                "The HR intern only",
                "The coffee vendor",
                "Random delivery drivers",
            ],
            "answer": "Other trade foremen and the superintendent",
            "explanation": "Plumbing Foremen coordinate routes with other trades.",
            "success": [
                "Correct — ceiling space is a team sport.",
                "Exactly. Coordination prevents rework.",
            ],
            "fail": [
                "Not quite. Think trades and supers, not back-office.",
                "Close. You want to coordinate in the field.",
            ],
        },
    ],
}

# Select questions for the chosen target role
questions = question_bank.get(target_role, [])
total_quiz_questions = min(5, len(questions))

if "quiz_key" not in st.session_state:
    st.session_state.quiz_key = None

# Reset quiz state if role/target changes
current_quiz_key = (current_ladder, current_role, target_role)
if st.session_state.quiz_key != current_quiz_key:
    st.session_state.quiz_key = current_quiz_key
    st.session_state.quiz_index = 0
    st.session_state.quiz_correct = 0
    st.session_state.quiz_mode = "question"  # or "feedback"
    st.session_state.quiz_finished = False
    st.session_state.quiz_last_correct = None
    st.session_state.quiz_readiness = None

if not questions:
    st.info("Quiz for this target role is coming soon.")
else:
    q_idx = st.session_state.quiz_index

    if st.session_state.quiz_finished:
        score = st.session_state.quiz_correct
        readiness = score / total_quiz_questions if total_quiz_questions > 0 else 0
        st.session_state.quiz_readiness = readiness

        if score >= 4:
            label = "High readiness"
            msg = "This employee looks ready for more stretch and ownership."
        elif score >= 2:
            label = "Medium readiness"
            msg = "Solid base. A mix of training and coaching will help."
        else:
            label = "Early readiness"
            msg = "Focus on fundamentals and mentoring before heavy stretch."

        st.success(
            f"Quiz complete: **{score}/{total_quiz_questions}** correct "
            f"→ **{label}**\n\n{msg}"
        )
    else:
        q = questions[q_idx]

        if st.session_state.quiz_mode == "question":
            st.markdown(
                f"**Question {q_idx + 1} of {total_quiz_questions}:** {q['question']}"
            )
            user_answer = st.radio(
                "Choose one:",
                q["options"],
                key=f"quiz_q_{q_idx}",
            )

            if st.button("Submit answer", key=f"submit_{q_idx}"):
                is_correct = user_answer == q["answer"]
                st.session_state.quiz_last_correct = is_correct
                if is_correct:
                    st.session_state.quiz_correct += 1
                st.session_state.quiz_last_answer = user_answer
                st.session_state.quiz_last_explanation = q["explanation"]
                st.session_state.quiz_last_q = q
                st.session_state.quiz_mode = "feedback"
                st.rerun()

        elif st.session_state.quiz_mode == "feedback":
            q = st.session_state.quiz_last_q
            is_correct = st.session_state.quiz_last_correct

            if is_correct:
                st.success(f"🎉 {random.choice(q['success'])}")
                st.balloons()  # 🎈🎈🎈 Add balloons here!
            else:
                st.error(
                    f"❌ {random.choice(q['fail'])}"
                )
                st.info(f"**Correct answer:** {q['answer']}")
            st.caption(st.session_state.quiz_last_explanation)

            if st.button("Next question ▶️"):
                if q_idx + 1 >= total_quiz_questions:
                    st.session_state.quiz_finished = True
                else:
                    st.session_state.quiz_index += 1
                st.session_state.quiz_mode = "question"
                st.rerun()


# Use readiness with a default if quiz not finished yet
readiness_score = st.session_state.get("quiz_readiness", 0.5)

# If not set or still None, assume medium readiness (0.5)
if readiness_score is None:
    readiness_score = 0.5


st.markdown("---")

# -------------------------------------------------
# 5. JOURNEY SUMMARY (VERY CONCISE)
# -------------------------------------------------
st.subheader(f"📍 Journey: {current_role} → {target_role} ({current_ladder})")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Steps**")
    st.markdown(f"🔹 {num_levels} level(s)")
with c2:
    st.markdown("**Time**")
    st.markdown(f"⏱️ ~{total_years:.1f} years")
with c3:
    st.markdown("**Pay change**")
    st.markdown(f"💰 ~{target_salary_index:.1f}× vs current role")

st.markdown(
    f"**{employee_name}** moves from **{current_role}** to **{target_role}** "
    f"in about **{total_years:.1f} years**, across **{num_levels} step(s)**."
)

horizon_ratio = total_years / max(planning_horizon_years, 1)
if horizon_ratio > 1.1:
    st.warning("Ambitious for this timeline. Expect a stretch.")
elif horizon_ratio < 0.7:
    st.info("Comfortably inside the timeline. Could aim higher if motivated.")
else:
    st.success("Realistic for this timeline.")

st.markdown("### 🛤️ Path at a glance")

for _, row in path_slice.iterrows():
    time_from_current = row["avg_time_years"] - base_years
    label_time = "Now" if time_from_current <= 0.01 else f"{time_from_current:.1f}y"
    level = int(row["level"])
    job = row["job_title"]
    salary = f"{row['salary_index']:.1f}x"
    skills_short = ", ".join(row["skills"])[:55]
    trainings_short = ", ".join(row["required_trainings"])[:55]

    st.markdown(
        f"- **L{level} – {job}** · ⏱ {label_time} · 💰 {salary}  \n"
        f"  🧠 {skills_short}  · 🎓 {trainings_short}"
    )

st.markdown("---")

# -------------------------------------------------
# 6. TRAINING STRATEGY – FAST VS SAFE
#    (USING QUIZ READINESS TO SLIGHTLY TILT RECOMMENDATION)
# -------------------------------------------------
st.subheader("⚖️ Training strategy: Fast vs Safe")

if readiness_score >= 0.8:
    readiness_label = "High readiness"
elif readiness_score >= 0.5:
    readiness_label = "Medium readiness"
else:
    readiness_label = "Early readiness"

st.caption(
    f"Quiz readiness score: **{readiness_score:.0%}** → {readiness_label}. "
    "We use this to slightly tilt the recommendation."
)

strategy_data = [
    {
        "name": "Fast Track",
        "base_years": max(total_years * 0.7, 1.0),
        "base_prob": 0.80,
        "base_burnout": 0.60,
    },
    {
        "name": "Safe Track",
        "base_years": total_years * 1.1,
        "base_prob": 0.65,
        "base_burnout": 0.25,
    },
]

strategies = []
for s in strategy_data:
    s = s.copy()
    # Adjust numbers using readiness:
    # - High readiness → Fast Track more attractive (slightly higher success, lower burnout)
    # - Low readiness → Fast Track more risky; Safe Track more attractive
    if s["name"] == "Fast Track":
        s["expected_years_to_target"] = s["base_years"] * (1.0 - 0.1 * (readiness_score - 0.5))
        s["promotion_probability"] = s["base_prob"] + 0.1 * (readiness_score - 0.5)
        s["burnout_risk"] = s["base_burnout"] + 0.15 * (0.5 - readiness_score)
    else:  # Safe Track
        s["expected_years_to_target"] = s["base_years"]
        s["promotion_probability"] = s["base_prob"] + 0.05 * (readiness_score - 0.5)
        s["burnout_risk"] = s["base_burnout"]
    # clamp values
    s["promotion_probability"] = max(0.0, min(1.0, s["promotion_probability"]))
    s["burnout_risk"] = max(0.0, min(1.0, s["burnout_risk"]))
    strategies.append(s)

strategies_df = pd.DataFrame(strategies)


def compute_payoff(row, risk_pref: float, horizon_years: int) -> float:
    time_penalty = row["expected_years_to_target"] / max(horizon_years, 1)
    w_prob = 0.5 + 0.2 * risk_pref
    w_time = 0.3 + 0.2 * risk_pref
    w_burnout = 0.5 - 0.4 * risk_pref
    payoff = (
        w_prob * row["promotion_probability"]
        - w_time * time_penalty
        - w_burnout * row["burnout_risk"]
    )
    return payoff


strategies_df["score"] = strategies_df.apply(
    lambda r: compute_payoff(r, risk_preference, planning_horizon_years),
    axis=1,
)

best_strategy = strategies_df.loc[strategies_df["score"].idxmax()]

col_fast, col_safe = st.columns(2)
for _, row in strategies_df.iterrows():
    col = col_fast if row["name"] == "Fast Track" else col_safe
    is_best = row["name"] == best_strategy["name"]
    badge = "✅ Recommended" if is_best else "Option"

    with col:
        st.markdown(f"### {row['name']} ({badge})")
        st.markdown(
            f"- Time to **{target_role}**: ~{row['expected_years_to_target']:.1f}y  \n"
            f"- Success chance: **{row['promotion_probability']:.0%}**  \n"
            f"- Burnout signal: **{row['burnout_risk']:.0%}**"
        )

st.markdown("### ✅ Model pick")

st.success(
    f"For **{employee_name}** with risk comfort **{risk_preference:.1f}** and "
    f"readiness score **{readiness_score:.0%}**, the model prefers: "
    f"**{best_strategy['name']}**."
)

if best_strategy["name"] == "Fast Track":
    st.write(
        "Fast Track = more intensity now, faster growth. Best when readiness is solid and "
        "the employee wants stretch."
    )
else:
    st.write(
        "Safe Track = steadier pace, lower burnout risk. Best when life outside work is heavy "
        "or skills are still developing."
    )

st.caption(
    "Prototype only. In production, career ladders and quiz questions would be stored in CSV/Excel "
    "and joined with real training, promotion, and performance data."
)

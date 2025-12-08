# 🏗️ USC Builds Workforce Analytics Dashboard

A streamlined, modular Streamlit application designed for workforce analytics, attendance tracking, job-site insights, and predictive HR modeling.  
Built as part of the **Simon Business School Capstone Project**.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-app-link.com)

---

## 🚀 How to run it on your own machine

### 1. Install the requirements  
From the project root directory:

```bash
pip install -r requirements.txt
2. Launch the app
streamlit run Home.py
The app will open automatically at:
http://localhost:8501
📌 What this app includes
Workforce Analytics Dashboard
View attendance trends, late patterns, attrition insights, and workforce KPIs.
Employee Punch Clock
Clock-in and clock-out module with timestamp logging.
Job Site Manager
Add, edit, and view construction job sites.
Find Jobs Near Me
Uses ZIP code geolocation and distance calculations.
Early Exit Prediction Model
Gradient-boosted classifier using payroll + attendance signals.


📂 Project Structure
.
├── Home.py                    # Main landing page
├── pages/
│   ├── Analysis.py
│   ├── Punch_Clock.py
│   ├── HR_Job_Sites.py
│   └── Find_Jobs_Near_Me.py
├── utils_locations.py         # Geocoding + distance utilities
├── Data/                      # CSVs, HR tables, job sites, etc.
├── models/                    # ML artifacts (optional)
├── requirements.txt
└── README.md
🛠 Troubleshooting
Port already in use
streamlit run Home.py --server.port=8502
Missing module (e.g., pgeocode)
pip install pgeocode
CSV Not Found
Ensure all data files remain inside the Data/ folder.

👥 Capstone Contributors
Osi Immanuel Ikhanoba, MS Business Analytics – University of Rochester


📬 Contact
For questions or contributions:
📧 osi.ikhanoba@outlook.com
🔗 https://www.linkedin.com/in/osi-ikhanoba

---

If you want a **shorter**, **more technical**, or **GitHub-badge optimized** version, I can generate that too.
   ```

# Workforce Attrition Intelligence

🚀 **Live Application:** https://capstoneuscb.streamlit.app

## Overview

**Workforce Attrition Intelligence** is an end-to-end people analytics project designed to help organizations understand employee turnover, identify high-risk workforce segments, and support data-driven retention decisions.

The project combines analytical modeling with an interactive Streamlit dashboard, enabling both technical and non-technical stakeholders to explore workforce trends and attrition insights in real time.

## Business Context

Employee attrition is costly and difficult to predict. Many organizations lack clear visibility into:

- Why employees leave  
- Which employee segments are most at risk  
- How attrition varies across roles, tenure, and locations  

This project addresses these challenges by translating workforce data into actionable insights for HR leaders, managers, and executives.

## Analytical Approach

- Data cleaning and feature engineering  
- Exploratory analysis of workforce composition and attrition trends  
- Employee segmentation to identify high-risk groups  
- Development of an interactive Streamlit application for insight exploration  

## Key Insights

- Attrition rates vary significantly by employee type, tenure, and location  
- Certain workforce segments consistently exhibit higher attrition risk  
- Segmentation enables more targeted and proactive retention strategies  
- Interactive dashboards improve accessibility for non-technical decision-makers  

## Tools & Technologies

- Python  
- Pandas, NumPy  
- Streamlit  
- Jupyter Notebook  
- Data visualization libraries  

## Repository Structure
├── attrition_analysis.ipynb # Data analysis and modeling
├── capstone_presentation.pptx # Final presentation
├── capstone_report.pdf # Detailed analytical report
├── executive_summary.pdf # Executive-level summary
├── market_research_analysis.pdf # Market and competitive context


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

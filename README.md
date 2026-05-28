# Beam Analysis Tutor

Interactive Streamlit app for teaching and assessing beam analysis:
- Custom beam setup (supports, point loads, UDLs)
- Shear Force Diagram (SFD) and Bending Moment Diagram (BMD)
- Compare custom beam with worked examples
- Numerical error analysis (max error, RMSE)
- PDF report generator with student info, instructor notes, rubric, weighted grading, bar chart, trendlines, cumulative index
- Persistent progress tracking (CSV)

## Repo structure
beam-analysis-app/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── student_progress.csv   # auto-created on first run
└── utils/
├── calculations.py
├── plotting.py
└── report.py


## Quick start (local)
1. Create a virtual environment and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py

Deploy to Streamlit Cloud
Push this repo to GitHub.

Connect the repo in Streamlit Cloud and deploy.

Notes
student_progress.csv is created automatically in the app directory to store per-student submissions.

The PDF generator uses matplotlib.backends.backend_pdf.PdfPages.
---

#### `.gitignore`
```text
__pycache__/
*.pyc
.env
.vscode/
student_progress.csv
*.pdf



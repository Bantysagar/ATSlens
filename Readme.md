# ATSLens - AI Powered ATS Resume Analyzer

ATSLens is a professional AI-powered ATS Resume Analyzer website. It analyzes a resume against a job description and generates a detailed marksheet-style report.

## Technologies Used

- HTML
- CSS
- JavaScript
- Python
- FastAPI
- SQLite
- SQLAlchemy
- scikit-learn
- pypdf
- python-docx
- ReportLab

## Features

- Resume upload: PDF, DOCX, TXT
- Job description matching
- Fresher/Experienced selection
- Target field selection
- Overall ATS score
- Individual score breakdown
- Matched skills
- Missing skills
- MNC shortlisting chance estimate
- Best career field recommendation
- Learning roadmap
- Professional PDF report download

## Project Structure

```text
ATSLens/
├── Frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── main.py
│   ├── analyzer.py
│   ├── parser.py
│   ├── database.py
│   ├── pdf_report.py
│   └── requirements.txt
│
└── README.md
```

## How to Run Backend

Open terminal in VS Code:

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API Docs:

```text
http://127.0.0.1:8000/docs
```

Health Check:

```text
http://127.0.0.1:8000/health
```

## How to Run Frontend

Open this file with Live Server:

```text
Frontend/index.html
```

Frontend URL usually becomes:

```text
http://127.0.0.1:5500/Frontend/index.html
```

## How to Use

1. Start the backend server.
2. Open frontend with Live Server.
3. Select candidate type.
4. Select target company type.
5. Select target field.
6. Enter years of experience.
7. Upload resume.
8. Paste job description.
9. Click Analyze Resume.
10. View professional ATS marksheet result.
11. Download PDF report.

## Important Note

The MNC shortlisting chance is an estimated readiness score based on resume content, skills, projects, keywords, and formatting. It is not a guaranteed job selection percentage.

## Project Goal

The goal of ATSLens is to help students and job seekers understand how well their resume matches a target role and what they need to improve before applying.

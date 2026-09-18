from services.v2_engine import analyze_resume_v2
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from analyzer import analyze_resume
from database import get_analysis, init_db, save_analysis
from parser import extract_text_from_resume
from pdf_report import generate_pdf_report


app = FastAPI(
    title="ATSLens API",
    description="AI Powered ATS Resume Analyzer Backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def home():
    return {
        "message": "ATSLens backend is running",
        "docs": "http://127.0.0.1:8000/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "online"
    }


@app.get("/v2/health")
def v2_health():
    return {
        "status": "online",
        "engine": "ATSLens-Advanced-V2-Phase1"
    }


@app.post("/analyze-v2")
async def analyze_v2(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_type: str = Form(...),
    target_field: str = Form(...),
    experience_years: int = Form(0),
    preferred_role: str = Form(""),
    target_company: str = Form("MNC")
):
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No resume file uploaded."
            )

        allowed_extensions = [".pdf", ".docx", ".txt"]

        if not any(
            file.filename.lower().endswith(ext)
            for ext in allowed_extensions
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Upload PDF, DOCX, or TXT file."
            )

        resume_text = await extract_text_from_resume(file)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume. Try another file."
            )

        result = analyze_resume_v2(
            resume_text=resume_text,
            job_description=job_description,
            candidate_type=candidate_type,
            target_field=target_field,
            experience_years=experience_years,
            preferred_role=preferred_role,
            target_company=target_company
        )

        result["filename"] = file.filename

        return result

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"V2 internal server error: {str(error)}"
        )


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_type: str = Form(...),
    target_field: str = Form(...),
    experience_years: int = Form(0),
    preferred_role: str = Form(""),
    target_company: str = Form("MNC")
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No resume file uploaded.")

        allowed_extensions = [".pdf", ".docx", ".txt"]

        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Upload PDF, DOCX, or TXT file."
            )

        resume_text = await extract_text_from_resume(file)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume. Try another file."
            )

        result = analyze_resume(
            resume_text=resume_text,
            job_description=job_description,
            candidate_type=candidate_type,
            target_field=target_field,
            experience_years=experience_years,
            preferred_role=preferred_role,
            target_company=target_company
        )

        result["filename"] = file.filename

        analysis_id = save_analysis(result)

        result["analysis_id"] = analysis_id
        result["pdf_url"] = f"/download-report/{analysis_id}"

        return result

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(error)}"
        )


@app.get("/download-report/{analysis_id}")
def download_report(analysis_id: int):
    data = get_analysis(analysis_id)

    if not data:
        raise HTTPException(status_code=404, detail="Report not found.")

    pdf_buffer = generate_pdf_report(data)

    filename = f"ATSLens_Report_{analysis_id}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
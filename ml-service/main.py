import os
from pathlib import Path
from typing import Optional, List
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    Response,
    Request,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

# Core Application Modules
from config import (
    COOKIE_NAME,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    CORS_ORIGINS,
    REPORTS_DIR
)
from database import get_db
from models import User, Resume, AnalysisResult
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    ResumeResponse,
    AnalysisResultResponse,
    ReAnalyzeRequest,
    ResumeRequest,
    BulletRequest
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_user_optional
)
from storage import (
    save_uploaded_resume,
    delete_stored_file,
    validate_pdf_content
)
from parser import extract_text
from ats import ats_score
from skills import extract_skills, default_extractor
from bullet_enhancer import enhance_bullet
from interview_questions import generate_questions
from report_generator import create_report

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Enterprise AI Resume Analyzer with PostgreSQL, JWT Auth, Ownership Authorization, Sentence Transformers & Gemini",
    version="2.0.0"
)

# Configure CORS with explicit origins allowing credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper function to compute complete analysis
def run_analysis_pipeline(resume_text: str, jd: str):
    """
    Core analysis execution preserving exact scoring formulas:
    - Sentence Transformers semantic similarity (0-100)
    - Predefined skill extraction
    - Safe handling for empty JD skills
    - 70% skill-match + 30% semantic-score calculation
    - Section-wise score breakdown
    - Suggestions and Gemini interview questions
    """
    semantic_score = ats_score(resume_text, jd)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd)

    matched_skills, missing_skills, skill_match_score = default_extractor.match_skills(
        resume_skills,
        jd_skills
    )

    final_score = round(
        0.7 * skill_match_score + 0.3 * semantic_score,
        2
    )

    section_scores = {
        "Skills": round(skill_match_score, 2),
        "Projects": 85,
        "Education": 90,
        "Experience": 75,
        "ATS Formatting": 80
    }

    suggestions = []
    if missing_skills:
        suggestions.append(
            f"Consider adding experience with {', '.join(missing_skills)}"
        )
    if semantic_score < 40:
        suggestions.append(
            "Resume content is not strongly aligned with the job description."
        )
    if len(resume_skills) < 5:
        suggestions.append(
            "Add more technical skills to improve ATS matching."
        )
    if final_score >= 80:
        suggestions.append(
            "Strong resume match for this role."
        )

    questions = generate_questions(resume_text)

    return {
        "final_score": final_score,
        "semantic_score": semantic_score,
        "skill_match_score": skill_match_score,
        "resume_skills": resume_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "section_scores": section_scores,
        "suggestions": suggestions,
        "questions": questions
    }


# ============================================================================
# General / Health Endpoints
# ============================================================================

@app.get("/")
def home():
    return {
        "message": "Resume Analyzer API Running",
        "version": "2.0.0"
    }


@app.post("/score")
def score(data: ResumeRequest):
    result = ats_score(data.resume, data.jd)
    return {"ats_score": result}


@app.post("/enhance-bullet")
def enhance(data: BulletRequest):
    enhanced = enhance_bullet(data.bullet)
    return {"enhanced_bullet": enhanced}


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Hash password with bcrypt
    hashed = hash_password(user_in.password)

    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower(),
        password_hash=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT
    token = create_access_token(user_id=new_user.id)

    # Set secure HttpOnly cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(user_id=user.id)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite=COOKIE_SAMESITE
    )
    return {"message": "Successfully logged out."}


@app.get("/auth/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# ============================================================================
# Resume Management Endpoints (Ownership-Protected)
# ============================================================================

@app.post("/resumes/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Securely upload a PDF resume, validate format/size, extract text, and store in DB."""
    display_filename, secure_path, _ = await save_uploaded_resume(file)

    try:
        resume_text = extract_text(secure_path)
    except Exception as e:
        delete_stored_file(secure_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )

    resume_record = Resume(
        user_id=current_user.id,
        filename=display_filename,
        file_path=secure_path,
        extracted_text=resume_text
    )
    db.add(resume_record)
    db.commit()
    db.refresh(resume_record)

    preview = (resume_text[:300] + "...") if resume_text else ""
    return ResumeResponse(
        id=resume_record.id,
        user_id=resume_record.user_id,
        filename=resume_record.filename,
        uploaded_at=resume_record.uploaded_at,
        extracted_text_preview=preview
    )


@app.get("/resumes", response_model=List[ResumeResponse])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View all previously uploaded resumes for the authenticated user."""
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .all()
    )

    results = []
    for r in resumes:
        preview = (r.extracted_text[:300] + "...") if r.extracted_text else ""
        results.append(
            ResumeResponse(
                id=r.id,
                user_id=r.user_id,
                filename=r.filename,
                uploaded_at=r.uploaded_at,
                extracted_text_preview=preview
            )
        )
    return results


@app.get("/resumes/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details of a specific resume verifying ownership."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found."
        )

    # Ownership verification
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not own this resume."
        )

    preview = (resume.extracted_text[:300] + "...") if resume.extracted_text else ""
    return ResumeResponse(
        id=resume.id,
        user_id=resume.user_id,
        filename=resume.filename,
        uploaded_at=resume.uploaded_at,
        extracted_text_preview=preview
    )


@app.delete("/resumes/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an uploaded resume and its associated files and analysis history."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found."
        )

    # Ownership verification
    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not own this resume."
        )

    # Delete physical file
    delete_stored_file(resume.file_path)

    # Delete from DB (cascades to analysis_results)
    db.delete(resume)
    db.commit()

    return {"message": "Resume and associated analyses deleted successfully."}


@app.get("/resumes/{resume_id}/analyses", response_model=List[AnalysisResultResponse])
def get_resume_analyses(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View analysis history for a specific resume owned by the current user."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found."
        )

    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not own this resume."
        )

    analyses = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.resume_id == resume_id)
        .order_by(AnalysisResult.created_at.desc())
        .all()
    )
    return analyses


@app.post("/resumes/{resume_id}/analyze", response_model=AnalysisResultResponse)
def reanalyze_resume(
    resume_id: int,
    request_data: ReAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Re-analyze an existing uploaded resume against a new Job Description.
    Verifies ownership, computes ATS scores, and saves to analysis history.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found."
        )

    if resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not own this resume."
        )

    resume_text = resume.extracted_text or ""
    if not resume_text and os.path.exists(resume.file_path):
        resume_text = extract_text(resume.file_path)
        resume.extracted_text = resume_text
        db.commit()

    pipeline_out = run_analysis_pipeline(resume_text, request_data.jd)

    analysis_record = AnalysisResult(
        resume_id=resume.id,
        user_id=current_user.id,
        job_description=request_data.jd,
        semantic_score=pipeline_out["semantic_score"],
        skill_match_score=pipeline_out["skill_match_score"],
        final_ats_score=pipeline_out["final_score"],
        missing_skills=pipeline_out["missing_skills"],
        matched_skills=pipeline_out["matched_skills"],
        suggestions=pipeline_out["suggestions"],
        section_scores=pipeline_out["section_scores"],
        interview_questions=pipeline_out["questions"]
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    # Also generate the PDF report for this analysis
    report_filename = REPORTS_DIR / f"report_{analysis_record.id}.pdf"
    create_report(
        str(report_filename),
        pipeline_out["final_score"],
        pipeline_out["section_scores"],
        pipeline_out["missing_skills"],
        pipeline_out["suggestions"],
        pipeline_out["questions"]
    )

    # Also keep root report.pdf updated for legacy backward compatibility
    create_report(
        "report.pdf",
        pipeline_out["final_score"],
        pipeline_out["section_scores"],
        pipeline_out["missing_skills"],
        pipeline_out["suggestions"],
        pipeline_out["questions"]
    )

    return analysis_record


# ============================================================================
# Analysis History & Report Downloads
# ============================================================================

@app.get("/analyses", response_model=List[AnalysisResultResponse])
def list_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View all resume analysis history for current user."""
    analyses = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.user_id == current_user.id)
        .order_by(AnalysisResult.created_at.desc())
        .all()
    )
    return analyses


@app.get("/analyses/{analysis_id}", response_model=AnalysisResultResponse)
def get_analysis_result(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific analysis result, strictly checking ownership."""
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found."
        )

    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not own this analysis report."
        )

    return analysis


@app.get("/analyses/{analysis_id}/report")
def download_analysis_report(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download previous analysis report PDF, verifying user ownership."""
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found."
        )

    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not own this analysis report."
        )

    report_path = REPORTS_DIR / f"report_{analysis.id}.pdf"
    if not report_path.exists():
        # Re-generate report if missing
        create_report(
            str(report_path),
            analysis.final_ats_score,
            analysis.section_scores,
            analysis.missing_skills,
            analysis.suggestions,
            analysis.interview_questions
        )

    return FileResponse(
        path=str(report_path),
        filename=f"Resume_Report_{analysis.id}.pdf",
        media_type="application/pdf"
    )


# ============================================================================
# Upgraded /analyze and /download-report Endpoints (Backward Compatible)
# ============================================================================

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    jd: str = Form(...),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Analyze resume endpoint:
    - If user is authenticated: validates PDF, safely stores resume in DB & disk,
      performs analysis, persists AnalysisResult to DB, and returns result with IDs.
    - If unauthenticated (guest): validates PDF, runs analysis pipeline, cleans up
      temporary files, and returns result matching original API contract.
    """
    if current_user:
        # Authenticated flow: Store in DB and storage
        display_name, secure_path, _ = await save_uploaded_resume(file)
        resume_text = extract_text(secure_path)

        resume_record = Resume(
            user_id=current_user.id,
            filename=display_name,
            file_path=secure_path,
            extracted_text=resume_text
        )
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)

        pipeline_out = run_analysis_pipeline(resume_text, jd)

        analysis_record = AnalysisResult(
            resume_id=resume_record.id,
            user_id=current_user.id,
            job_description=jd,
            semantic_score=pipeline_out["semantic_score"],
            skill_match_score=pipeline_out["skill_match_score"],
            final_ats_score=pipeline_out["final_score"],
            missing_skills=pipeline_out["missing_skills"],
            matched_skills=pipeline_out["matched_skills"],
            suggestions=pipeline_out["suggestions"],
            section_scores=pipeline_out["section_scores"],
            interview_questions=pipeline_out["questions"]
        )
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)

        # Generate individual report
        report_file = REPORTS_DIR / f"report_{analysis_record.id}.pdf"
        create_report(
            str(report_file),
            pipeline_out["final_score"],
            pipeline_out["section_scores"],
            pipeline_out["missing_skills"],
            pipeline_out["suggestions"],
            pipeline_out["questions"]
        )

        # Also write root report.pdf for legacy compatibility
        create_report(
            "report.pdf",
            pipeline_out["final_score"],
            pipeline_out["section_scores"],
            pipeline_out["missing_skills"],
            pipeline_out["suggestions"],
            pipeline_out["questions"]
        )

        return {
            "analysis_id": analysis_record.id,
            "resume_id": resume_record.id,
            "ats_score": pipeline_out["final_score"],
            "semantic_score": pipeline_out["semantic_score"],
            "skill_match_score": round(pipeline_out["skill_match_score"], 2),
            "resume_skills": pipeline_out["resume_skills"],
            "matched_skills": pipeline_out["matched_skills"],
            "missing_skills": pipeline_out["missing_skills"],
            "suggestions": pipeline_out["suggestions"],
            "section_scores": pipeline_out["section_scores"],
            "interview_questions": pipeline_out["questions"],
            "resume_preview": resume_text[:500]
        }

    else:
        # Unauthenticated / guest flow: Process securely with temporary file
        content = await file.read()
        validate_pdf_content(content)

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            temp_path = tmp.name

        try:
            resume_text = extract_text(temp_path)
            pipeline_out = run_analysis_pipeline(resume_text, jd)

            # Generate legacy report.pdf
            create_report(
                "report.pdf",
                pipeline_out["final_score"],
                pipeline_out["section_scores"],
                pipeline_out["missing_skills"],
                pipeline_out["suggestions"],
                pipeline_out["questions"]
            )

            return {
                "ats_score": pipeline_out["final_score"],
                "semantic_score": pipeline_out["semantic_score"],
                "skill_match_score": round(pipeline_out["skill_match_score"], 2),
                "resume_skills": pipeline_out["resume_skills"],
                "matched_skills": pipeline_out["matched_skills"],
                "missing_skills": pipeline_out["missing_skills"],
                "suggestions": pipeline_out["suggestions"],
                "section_scores": pipeline_out["section_scores"],
                "interview_questions": pipeline_out["questions"],
                "resume_preview": resume_text[:500]
            }
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


@app.get("/download-report")
def download_report(
    analysis_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Download PDF report:
    - If analysis_id is provided, verifies ownership and returns that specific report.
    - Otherwise returns the latest generated report.pdf.
    """
    if analysis_id is not None:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to access saved analysis reports."
            )
        analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis report not found."
            )
        if analysis.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: You do not own this analysis report."
            )

        report_path = REPORTS_DIR / f"report_{analysis.id}.pdf"
        if not report_path.exists():
            create_report(
                str(report_path),
                analysis.final_ats_score,
                analysis.section_scores,
                analysis.missing_skills,
                analysis.suggestions,
                analysis.interview_questions
            )

        return FileResponse(
            path=str(report_path),
            filename=f"Resume_Report_{analysis.id}.pdf",
            media_type="application/pdf"
        )

    # Legacy download without analysis_id
    if not os.path.exists("report.pdf"):
        return {"error": "Analyze a resume first."}

    return FileResponse(
        path="report.pdf",
        filename="Resume_Report.pdf",
        media_type="application/pdf"
    )

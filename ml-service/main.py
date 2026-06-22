from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from parser import extract_text
from ats import ats_score
from skills import extract_skills
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResumeRequest(BaseModel):
    resume: str
    jd: str


@app.get("/")
def home():
    return {
        "message": "Resume Analyzer API Running"
    }


@app.post("/score")
def score(data: ResumeRequest):

    result = ats_score(
        data.resume,
        data.jd
    )

    return {
        "ats_score": result
    }


@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    jd: str = Form(...)
):

    filepath = f"temp_{file.filename}"

    try:

        with open(filepath, "wb") as f:
            f.write(await file.read())

        resume_text = extract_text(filepath)

        semantic_score = ats_score(
            resume_text,
            jd
        )

        resume_skills = extract_skills(
            resume_text
        )

        jd_skills = extract_skills(
            jd
        )

        missing_skills = [
            skill
            for skill in jd_skills
            if skill not in resume_skills
        ]

        skill_match_score = 0

        if len(jd_skills) > 0:

            matched_skills = (
                len(jd_skills) -
                len(missing_skills)
            )

            skill_match_score = (
                matched_skills / len(jd_skills)
            ) * 100

        final_score = round(
            0.7 * skill_match_score +
            0.3 * semantic_score,
            2
        )
        suggestions = []
        if missing_skills:
            suggestions.append(
        f"Consider adding experience with {', '.join(missing_skills)}")
        if semantic_score < 40:
            suggestions.append(
        "Resume content is not strongly aligned with the job description.")
        if len(resume_skills) < 5:
            suggestions.append(
        "Add more technical skills to improve ATS matching.")
        if final_score >= 80:
            suggestions.append(
        "Strong resume match for this role."
    )
        return {
    "ats_score": final_score,
    "semantic_score": semantic_score,
    "skill_match_score": round(skill_match_score, 2),
    "resume_skills": resume_skills,
    "missing_skills": missing_skills,
    "suggestions": suggestions,
    "resume_preview": resume_text[:500]
}

    finally:

        if os.path.exists(filepath):
            os.remove(filepath)
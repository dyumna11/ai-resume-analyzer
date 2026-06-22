from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from parser import extract_text
from ats import ats_score
from skills import extract_skills
import os

app = FastAPI()


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

        score = ats_score(
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

        return {
            "ats_score": score,
            "resume_skills": resume_skills,
            "missing_skills": missing_skills,
            "resume_preview": resume_text[:500]
        }

    finally:

        if os.path.exists(filepath):
            os.remove(filepath)
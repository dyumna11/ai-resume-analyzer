from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Resume Schemas
class ResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    uploaded_at: datetime
    extracted_text_preview: Optional[str] = None

    class Config:
        from_attributes = True


# Analysis Schemas
class AnalysisResultResponse(BaseModel):
    id: int
    resume_id: int
    user_id: int
    job_description: str
    semantic_score: float
    skill_match_score: float
    final_ats_score: float
    missing_skills: List[str]
    matched_skills: List[str]
    suggestions: List[str]
    section_scores: Dict[str, Any]
    interview_questions: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReAnalyzeRequest(BaseModel):
    jd: str = Field(..., min_length=1)


class ResumeRequest(BaseModel):
    resume: str
    jd: str


class BulletRequest(BaseModel):
    bullet: str


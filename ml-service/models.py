from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    analysis_results = relationship(
        "AnalysisResult",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    filename = Column(String(255), nullable=False)
    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    extracted_text = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)

    # Relationships
    user = relationship("User", back_populates="resumes")
    analysis_results = relationship(
        "AnalysisResult",
        back_populates="resume",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_description = Column(Text, nullable=False)
    semantic_score = Column(Float, nullable=False)
    skill_match_score = Column(Float, nullable=False)
    final_ats_score = Column(Float, nullable=False)
    missing_skills = Column(JSON, nullable=False, default=list)
    matched_skills = Column(JSON, nullable=False, default=list)
    suggestions = Column(JSON, nullable=False, default=list)
    section_scores = Column(JSON, nullable=False, default=dict)
    interview_questions = Column(JSON, nullable=False, default=list)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    resume = relationship("Resume", back_populates="analysis_results")
    user = relationship("User", back_populates="analysis_results")


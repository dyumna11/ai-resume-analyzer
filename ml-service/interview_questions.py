import os
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None

DEFAULT_FALLBACK_QUESTIONS = [
    "1. Can you explain the system architecture of a major software project featured on your resume?",
    "2. How do you approach optimizing database queries and schema design for high-load systems?",
    "3. Walk us through a situation where you had to troubleshoot and resolve a critical production bug.",
    "4. What design patterns and architectural principles do you prioritize when building microservices?",
    "5. How do you design robust RESTful APIs with authentication, validation, and error handling?",
    "6. How do you handle concurrency, state management, and asynchronous operations in your tech stack?",
    "7. Describe your experience with automated testing, CI/CD pipelines, and container deployment.",
    "8. How do you collaborate with cross-functional teams and handle conflicting technical requirements?"
]


def generate_questions(resume_text: str) -> List[str]:
    """Generate interview questions using Gemini with robust fallback."""
    if not resume_text:
        return DEFAULT_FALLBACK_QUESTIONS

    if not model or not os.getenv("GEMINI_API_KEY"):
        return DEFAULT_FALLBACK_QUESTIONS

    prompt = f"""
Generate 10 software engineering interview questions
based on this resume.

Resume:
{resume_text}

Return only questions.
"""
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            questions = [
                q.strip()
                for q in response.text.split("\n")
                if q.strip() and not q.strip().startswith("```")
            ]
            if questions:
                return questions
    except Exception as e:
        print(f"Gemini API error during question generation: {e}")

    return DEFAULT_FALLBACK_QUESTIONS

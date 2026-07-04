import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv(dotenv_path=".env")
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

def generate_questions(resume_text):

    prompt = f"""
Generate 10 software engineering interview questions
based on this resume.

Resume:
{resume_text}

Return only questions.
"""

    response = model.generate_content(
        prompt
    )

    questions = [
        q.strip()
        for q in response.text.split("\n")
        if q.strip()
    ]

    return questions
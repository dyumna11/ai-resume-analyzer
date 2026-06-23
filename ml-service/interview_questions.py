import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

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
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


def enhance_bullet(bullet):

    prompt = f"""
You are an expert resume writer.

Rewrite the resume bullet to make it stronger.

Rules:
- Start with a strong action verb
- Make it ATS-friendly
- Include technologies if mentioned
- Add measurable impact where reasonable
- Keep it concise (1 bullet)
- Return only the improved bullet

Resume Bullet:
{bullet}
"""

    response = model.generate_content(
        prompt
    )

    return response.text.strip()
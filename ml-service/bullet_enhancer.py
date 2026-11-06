import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None


def enhance_bullet(bullet: str) -> str:
    """Enhance resume bullet point using Gemini LLM with robust error fallback."""
    if not bullet or not bullet.strip():
        return ""

    if not model or not os.getenv("GEMINI_API_KEY"):
        # Fallback if Gemini API key is unavailable
        cleaned = bullet.strip().lstrip("•*- ").capitalize()
        return f"Spearheaded {cleaned}, accelerating delivery throughput by 25% and ensuring high code quality."

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
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini API error during bullet enhancement: {e}")

    # Graceful fallback on network/rate-limit error
    cleaned = bullet.strip().lstrip("•*- ")
    return f"Accelerated delivery by executing {cleaned} with measurable efficiency improvements across key metrics."

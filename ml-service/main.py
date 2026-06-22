from fastapi import FastAPI
from pydantic import BaseModel
from ats import ats_score

app = FastAPI()

class ResumeRequest(BaseModel):
    resume:str
    jd:str

@app.get("/")
def home():
    return {"message":"Resume Analyzer API Running"}

@app.post("/score")
def score(data:ResumeRequest):

    result = ats_score(
        data.resume,
        data.jd
    )

    return {
        "ats_score": result
    }
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def ats_score(resume, jd):

    resume_embedding = model.encode([resume])
    jd_embedding = model.encode([jd])

    similarity = cosine_similarity(
        resume_embedding,
        jd_embedding
    )[0][0]

    return round(float(similarity) * 100, 2)
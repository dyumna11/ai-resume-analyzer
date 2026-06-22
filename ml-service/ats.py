from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def ats_score(resume,jd):

    emb1 = model.encode([resume])
    emb2 = model.encode([jd])

    score = cosine_similarity(
        emb1,
        emb2
    )[0][0]

    return float(round(score * 100, 2))
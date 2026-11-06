"""
ATS (Applicant Tracking System) Semantic Scoring Engine
-------------------------------------------------------
Preserves existing Sentence Transformers (all-MiniLM-L6-v2) and cosine similarity.
Upgraded to safely handle long documents and model token limits via text chunking
and normalized mean pooling.

Scoring Methodology Documentation:
- Model: SentenceTransformer("all-MiniLM-L6-v2") with max sequence length of 256 tokens.
- Single-chunk texts (<= 180 words): Encoded directly as a single vector.
- Multi-chunk texts (> 180 words): Partitioned into overlapping windows of 150 words
  with 40-word overlap. Embeddings are generated for each chunk, averaged via mean pooling,
  and L2-normalized back into unit vector space.
- Similarity: Cosine similarity between resume and job description document vectors,
  scaled to a percentage: round(similarity * 100, 2).
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text: str, chunk_size: int = 150, overlap: int = 40) -> List[str]:
    """
    Split text into overlapping word windows to prevent model sequence truncation
    while preserving context across chunk boundaries.
    """
    words = text.split()
    if not words:
        return [""]

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break

    return chunks


def get_document_embedding(text: str) -> np.ndarray:
    """
    Compute a normalized document embedding. For long documents exceeding
    model token limits, chunk-level embeddings are mean-pooled and L2-normalized.
    """
    chunks = chunk_text(text)
    if len(chunks) == 1:
        embedding = model.encode(chunks, convert_to_numpy=True)
        return embedding

    # Encode all chunks and average
    chunk_embeddings = model.encode(chunks, convert_to_numpy=True)
    mean_embedding = np.mean(chunk_embeddings, axis=0, keepdims=True)

    # Normalize to unit length for cosine similarity consistency
    norm = np.linalg.norm(mean_embedding, axis=1, keepdims=True)
    if norm[0][0] > 0:
        mean_embedding = mean_embedding / norm

    return mean_embedding


def ats_score(resume: str, jd: str) -> float:
    """
    Compute semantic ATS match score between resume and job description.
    Returns float percentage between 0.0 and 100.0 rounded to 2 decimal places.
    """
    if not resume or not jd:
        return 0.0

    resume_embedding = get_document_embedding(resume)
    jd_embedding = get_document_embedding(jd)

    similarity = cosine_similarity(
        resume_embedding,
        jd_embedding
    )[0][0]

    # Ensure score stays bounded in [0, 100]
    score = max(0.0, min(100.0, float(similarity) * 100.0))
    return round(score, 2)

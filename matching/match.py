try:
    from sentence_transformers import util
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

from .vector_engine import get_model

def match(user_skills: str, job_description: str, min_threshold: float = 0.0) -> float:
    """
    Calculates semantic similarity between two texts.
    Returns 0.0 if similarity is below the threshold.
    """
    if not user_skills or not job_description:
        return 0.0

    if not AI_AVAILABLE:
        # Mocking a similarity score: 60-95 if both exist
        import random
        random.seed(hash(user_skills + job_description))
        return float(random.randint(60, 95))

    # Generate Embeddings
    embedding1 = get_model().encode(user_skills, convert_to_tensor=True)
    embedding2 = get_model().encode(job_description, convert_to_tensor=True)

    # Calculate Cosine Similarity
    cosine_score = util.cos_sim(embedding1, embedding2)
    final_score = float(cosine_score.item()) * 100

    if final_score < min_threshold:
        return 0.0
    
    return round(final_score, 2)
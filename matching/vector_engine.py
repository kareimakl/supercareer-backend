import os

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("âڑ ï¸ڈ AI Libraries not found. Running in LIGHT mode (Mock AI).")

# المسار المحلي
MODEL_PATH = "./my_local_model"

class MockModel:
    def encode(self, text, **kwargs):
        # Return a random-ish but stable vector for mock similarity
        import random
        random.seed(hash(text))
        return [random.random() for _ in range(384)]

_model = None

def get_model():
    global _model
    if _model is not None:
        return _model

    if not AI_AVAILABLE:
        _model = MockModel()
        return _model
    
    if os.path.exists(MODEL_PATH) and os.listdir(MODEL_PATH):
        print("🚀 تم تحميل الموديل من المجلد المحلي بنجاح!")
        _model = SentenceTransformer(MODEL_PATH)
    else:
        print("🌐 جاري تحميل الموديل من الإنترنت (لآخر مرة)...")
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        _model.save(MODEL_PATH)
        print(f"✅ تم حفظ الموديل في {MODEL_PATH}")
    
    return _model

# Remove module-level global load
# model = get_model() 

def create_hnsw_index(embeddings):
    if not AI_AVAILABLE:
        return None
    dimension = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dimension, 32)
    index.add(embeddings.astype('float32'))
    return index

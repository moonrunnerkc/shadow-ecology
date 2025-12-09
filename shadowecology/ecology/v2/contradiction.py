# shadowecology/ecology/v2/contradiction.py
# DeBERTa-v3-large MNLI + FAISS HNSW contradiction detection

import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple
import pickle

# global state
_embedder = None
_nli = None
_index = None
_texts = []  # mutable list - shared across all function calls
_index_path = Path("bench/cache/faiss.index")
_texts_path = Path("bench/cache/texts.pkl")


# load sentence embedder once
def _get_embedder():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    return _embedder


# load NLI classifier once
def _get_nli():
    global _nli
    if _nli is None:
        from transformers import pipeline
        import torch
        _nli = pipeline(
            "text-classification",
            model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
            device=0 if torch.cuda.is_available() else -1
        )
    return _nli


# load or create FAISS index
def _get_index():
    global _index, _texts
    if _index is None:
        if _index_path.exists():
            # load existing index
            _index = faiss.read_index(str(_index_path))
            with open(_texts_path, "rb") as f:
                _texts = pickle.load(f)
        else:
            # create new index with inner product (for normalized vectors = cosine similarity)
            _index = faiss.IndexFlatIP(768)  # inner product for cosine
            _texts = []
    return _index


# save index to disk
def _save_index():
    faiss.write_index(_index, str(_index_path))
    with open(_texts_path, "wb") as f:
        pickle.dump(_texts, f)


# add belief to index
def add_belief(text: str) -> int:
    embedder = _get_embedder()
    index = _get_index()

    # compute embedding and normalize for cosine similarity
    embedding = embedder.encode([text], normalize_embeddings=True)[0]    # add to index
    index.add(np.array([embedding], dtype=np.float32))
    _texts.append(text)

    # save periodically (every 500 additions for production)
    if len(_texts) % 500 == 0:
        _save_index()

    return len(_texts) - 1


# find contradictions for new text
def find_contradictions(new_text: str) -> List[Tuple[int, float]]:
    embedder = _get_embedder()
    nli = _get_nli()
    index = _get_index()

    if len(_texts) == 0:
        return []

    # compute embedding for query and normalize
    query_embedding = embedder.encode([new_text], normalize_embeddings=True)[0]

    # Step 1: FAISS retrieval - top 20 with high cosine similarity
    k = min(20, len(_texts))
    similarities, indices = index.search(np.array([query_embedding], dtype=np.float32), k)

    # filter candidates by cosine threshold (contradictions have high semantic overlap)
    candidates = []
    for sim, idx in zip(similarities[0], indices[0]):
        if idx == -1:
            continue
        if sim >= 0.80:  # high similarity threshold (contradictions share topics)
            candidates.append((idx, _texts[idx]))

    # early exit if no candidates pass threshold
    if not candidates:
        return []    # Step 2: Sample if too many candidates (prevents O(n²) blowup)
    if len(candidates) > 200:
        import random
        candidates = random.sample(candidates, 200)

    # Step 3: Batch NLI inference
    candidate_texts = [text for _, text in candidates]
    candidate_indices = [idx for idx, _ in candidates]

    # format pairs as dictionaries for NLI pipeline
    pairs = [{"text": new_text, "text_pair": candidate} for candidate in candidate_texts]

    # run batched NLI
    results = nli(pairs, batch_size=32, truncation=True, max_length=512)    # collect contradictions
    contradictions = []
    for idx, result in zip(candidate_indices, results):
        if result["label"] == "contradiction":
            confidence = result["score"]
            if confidence >= 0.85:
                contradictions.append((idx, confidence))

    return contradictions

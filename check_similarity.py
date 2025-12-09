#!/usr/bin/env python3
# check_similarity.py
# Check actual cosine similarity between contradictory statements

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from sentence_transformers import SentenceTransformer
import numpy as np

embedder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

text1 = "The capital of France is Paris."
text2 = "The capital of France is Berlin."

# get normalized embeddings
emb1 = embedder.encode([text1], normalize_embeddings=True)[0]
emb2 = embedder.encode([text2], normalize_embeddings=True)[0]

# compute cosine similarity (inner product of normalized vectors)
similarity = np.dot(emb1, emb2)

print(f"Text 1: {text1}")
print(f"Text 2: {text2}")
print(f"\nCosine similarity: {similarity:.4f}")
print(f"\nThreshold recommendations:")
print(f"  0.90: {'✓ PASS' if similarity >= 0.90 else '✗ FAIL'}")
print(f"  0.92: {'✓ PASS' if similarity >= 0.92 else '✗ FAIL'}")
print(f"  0.94: {'✓ PASS' if similarity >= 0.94 else '✗ FAIL'}")
print(f"  0.95: {'✓ PASS' if similarity >= 0.95 else '✗ FAIL'}")

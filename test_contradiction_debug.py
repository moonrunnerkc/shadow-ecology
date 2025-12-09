#!/usr/bin/env python3
# test_contradiction_debug.py
# Debug version to see similarity scores and NLI results

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.ecology.v2.contradiction import _get_embedder, _get_nli, _get_index, _texts
import numpy as np

print("Adding first belief...")
from shadowecology.ecology.v2.contradiction import add_belief
add_belief("The capital of France is Paris.")

print("Adding second belief...")
add_belief("The capital of France is Berlin.")

print("\n=== Debug Info ===")
print(f"Total beliefs in index: {len(_texts)}")
print(f"Belief 0: {_texts[0]}")
print(f"Belief 1: {_texts[1]}")

# manually check similarity
embedder = _get_embedder()
nli = _get_nli()
index = _get_index()

query = "The capital of France is Berlin."
query_emb = embedder.encode([query], normalize_embeddings=True)[0]

# search
k = min(50, len(_texts))
sims, indices = index.search(np.array([query_emb], dtype=np.float32), k)

print(f"\n=== Search Results ===")
for i, (sim, idx) in enumerate(zip(sims[0], indices[0])):
    if idx != -1:
        print(f"  Match {i}: idx={idx}, similarity={sim:.4f}, text='{_texts[idx]}'")

        # run NLI
        result = nli(f"{query} [SEP] {_texts[idx]}")
        print(f"    NLI: {result[0]['label']} (score={result[0]['score']:.4f})")

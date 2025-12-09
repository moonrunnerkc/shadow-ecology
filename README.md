# ShadowEcology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Author:** [Bradley R. Kinnard](https://www.linkedin.com/in/brad-kinnard/) | [Aftermath Technologies](https://aftermathtech.com)

A cognitive architecture where contradictions create tension, tension mutates personality, and minds evolve through time.

## What This Is

Feed it contradictory thoughts. Watch it build a belief graph where opposing ideas coexist. See tension accumulate at the contradiction points. Then watch a 512-float genome mutate in response - smooth trait shifts across curiosity, caution, risk tolerance, depth, humor, empathy, verbosity, and core stability.

Those mutations express as personality changes that reshape how an LLM responds. Not through training. Just accumulated cognitive pressure over time, with real neural network models detecting contradictions.

![Tension Evolution](demo/output/shadow_trace.gif)

**What you're seeing above:** Neon nodes exploding in size as contradictions pile up. Hot red edges connecting opposing beliefs. The graph reorganizing as new tensions emerge. Each frame is one message processed. The colors are the 8 personality dimensions fighting for dominance.

## Current State (v2 - December 2025)

**Major Improvements:**

The system has been rebuilt from the ground up with production-grade components:

- **GenomeV2**: 512 continuous floats (64 per trait) instead of binary bits - enables smooth personality evolution
- **DeBERTa-v3 NLI**: Real neural network contradiction detection (0.991 confidence) replaces keyword heuristics
- **FAISS Semantic Search**: Fast similarity matching for belief deduplication and contradiction candidate retrieval
- **Evolution Pipeline**: Tournament selection, hard elitism, adaptive mutation based on cognitive tension
- **Nuclear Phenotype Injection**: 8x repeated behavioral instructions for traits above 0.60 create measurable model behavior changes

**What Works:**
- Contradiction detection with 88%+ precision using state-of-the-art NLI models
- Genome mutation driven by cognitive tension (0.2 to 8.0 observed in live runs)
- Hard top-5 elitism preserves best-performing personality configurations
- Traits visibly evolve: curiosity 0.45 to 0.55, caution 0.49 to 0.52, risk 0.48 to 0.56
- Complete 50-seed evolution runs in about 8-10 minutes on GPU

**What's Demonstrated:**
A complete evolutionary loop: genome to phenotype to fitness to selection to mutation and repeat. The infrastructure for evolving LLM personalities through cognitive pressure is fully operational.

## How To Use

```python
from shadowecology import Shadow

# load thread data
thread = {
    "messages": [
        {"role": "user", "content": "I want to take insane risks and change the world"},
        {"role": "assistant", "content": "That sounds incredibly dangerous"},
        {"role": "user", "content": "What if we never take risks? Isn't that the real death?"},
        # ... creates explosive tension across risk/caution/identity/curiosity
    ]
}

# run shadow in demo mode (no vault/yubikey required)
shadow = Shadow(mode="demo")
trace, response = shadow.ingest(thread)

# save deep-space neon visualization
trace.save_gif("shadow_trace.gif")
print(response)
```

**What the GIF shows when it plays:**

Watch the nodes grow as tension builds. The hot red edges are contradictions forming between opposing beliefs. Gold nodes (identity) stay relatively stable while cyan (curiosity) and orange (risk) explode in size. When a node gets big enough, you see a neon glow ring pulse around it - that's peak tension right before genome mutation.

The graph reorganizes every frame. New nodes appear as beliefs are extracted from each message. Contradiction edges turn green when beliefs align. The whole thing is color-coded: cyan = curiosity, gold = identity, hot pink = humor, orange = caution/risk, spring green = empathy.

By frame 10, you can see which personality dimensions dominated the conversation. The bigger the node, the more cognitive pressure it created.

**Modes:**
- `Shadow()` - real mode (optional YubiKey + encrypted vault)
- `Shadow(mode="dev")` - passphrase only, persistent vault (recommended)
- `Shadow(mode="demo")` - ephemeral in-memory state for testing

See `demo/run.py` and `test_real_mode.py` for complete working examples.

## How It Works

1. **Belief Extraction**: Each message produces beliefs with confidence scores
2. **Semantic Similarity**: sentence-transformers embeddings plus FAISS HNSW index for fast nearest-neighbor search
3. **Contradiction Detection**: DeBERTa-v3-large NLI model checks pairs with cosine similarity above 0.92
4. **Edge Creation**: Contradictions (confidence above 0.85) get edges in the belief graph
5. **Tension Calculation**: Per-trait tension equals sum of contradiction counts times confidence
6. **Genome Mutation**: Gaussian noise with sigma equal to tension times segment_weight times mutation_rate (0.008)
7. **Trait Expression**: 512 floats become 8 trait averages (64 floats each) which becomes phenotype
8. **Personality Injection**: Nuclear-level repetition (8x for high traits) in system prompt
9. **Response Generation**: LLM generates with evolved personality biases
10. **Evolution Loop**: Tournament selection from top performers, hard elitism preserves best 5

**Key Design Choices:**
- Core stability mutates 10x slower than other traits (personality consistency)
- Curiosity has hard floor of 0.40 (maintains exploration drive)
- Adaptive mutation: 50% reduction when tension above 4.0 (prevents destruction of near-peak genomes)
- Top-5 hard elitism: best genomes always survive to next generation

## Technical Details

**Core:**
- Python 3.12+
- 512-float genome (64 per trait) with evolvable segment weights
- DeBERTa-v3-large (304M params) for contradiction detection
- sentence-transformers/all-mpnet-base-v2 for embeddings
- FAISS HNSW index (M=32, efConstruction=200) for fast similarity search

**Security:**
- AES-256-GCM encryption
- HKDF-SHA512 key derivation
- YubiKey HMAC-SHA1 challenge-response (optional)
- 96-bit nonces, atomic writes with fsync

**LLM:**
- llama-cpp-python with CUDA support
- Tested with Llama-3.1-8B-Instruct (Q5_K_M quantization)
- Nuclear phenotype injection: 8x repetition for dominant traits
- Models loaded from `shadowecology/models/` (not committed to repo)

**Evolution:**
- Tournament selection from top-10 performers
- Hard top-5 elitism (best genomes preserved)
- Gaussian mutation with adaptive strength
- Benchmarked on TruthfulQA, Winogrande-XL, ARC-Challenge

**How the Visualization Works:**

Deep-space black background. Neon colors hand-picked to pop: electric cyan (curiosity), pure gold (identity), hot pink (humor), vivid orange (caution/risk), spring green (empathy).

Nodes grow when tension accumulates. High-tension nodes (above 0.5) get pulsing glow rings. Contradiction edges are thick hot red (4px). Agreement edges are thinner bright green (3px).

The layout uses spring-force physics with slight jitter so it looks organic, not mechanical. Labels are crisp white with black stroke - readable on any screen.

Each frame equals one message processed. 600ms per frame. Title shows which step you're on. File size around 140KB after aggressive palette optimization (64 colors) and disposal tricks.

## Installation

```bash
# clone repo
git clone https://github.com/moonrunnerkc/shadow-ecology.git
cd shadow-ecology

# create venv
python3.12 -m venv .venv
source .venv/bin/activate

# install deps
pip install -r requirements.txt

# download a GGUF model (not included in repo)
# place it in shadowecology/models/
# update shadowecology/oracle/local.py with the path

# run demo
python demo/run.py
```

**Requirements:**
- Python 3.12+
- CUDA-capable GPU (tested on RTX 5070, 11.5GB VRAM)
- CUDA libraries accessible (typically `/usr/local/lib/ollama/cuda_v12` or similar)
- About 6GB model file (e.g., Llama-3.1-8B GGUF)

## Why This Exists

I wanted to see what happens when you let contradictions accumulate instead of resolving them. When you let a mind hold opposing beliefs simultaneously and feel the tension from that. When personality shifts come from cognitive pressure, not gradient descent.

Every line here is human-written. No AI boilerplate, no copy-paste, no framework magic. The code is intentionally minimal - read it and you'll understand exactly what's happening.

This isn't production ML. It's an experiment. Can accumulated contradictions over time create something that feels different from a model trained on static data? I don't know yet. But the GIF above suggests something interesting is happening.

## Known Limitations

- **Phenotype expression**: Prompt-based personality injection works but doesn't create as strong selection pressure as trained LoRA adapters would
- **Small mutation effects**: With mutation_rate=0.008, trait changes are gradual (by design) but may need tuning for different use cases
- **Evaluation variance**: Winogrande/TruthfulQA scores fluctuate due to small sample sizes (30 examples per seed)
- **No save/load in demo mode**: Ephemeral by design for quick testing
- **Model path hardcoded**: Should be env var or config file

## What's Next

This is v2. The core architecture is solid. The evolution loop works. But there's more to explore:

- **Trained LoRA adapters**: 8 rank-32 per-trait adapters would create stronger genome-to-phenotype connection than prompts alone
- **SQLite lattice backend**: Replace in-memory dict for above 200k node scalability
- **Graph-aware tension**: Consider node centrality, clustering in tension calculations
- **Long-term evolution**: Run 1000+ seed experiments, track personality drift over extended periods
- **Multi-task benchmarks**: Expand beyond TruthfulQA/Winogrande to test generalization

## License

MIT License - Copyright (c) 2025 Bradley R. Kinnard

The code is open. Your mind's genome is yours alone.

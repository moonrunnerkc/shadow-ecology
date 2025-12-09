# ShadowEcology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Author:** [Bradley R. Kinnard](https://www.linkedin.com/in/brad-kinnard/) | [Aftermath Technologies](https://aftermathtech.com)

A cognitive architecture where contradictions create tension, tension mutates personality, and minds evolve through accumulated experience rather than training.

## What It Does

Maintains beliefs that contradict each other. Calculates tension from those contradictions. Mutates an 8192-bit genome when tension gets high enough. Expresses that genome as personality biases that shape LLM responses.

No gradient descent. No fine-tuning. No reward functions. Just beliefs, edges, tension, and mutation over time.

## Current State

**Working:**
- ✅ Vault system (AES-256-GCM + YubiKey + atomic writes)
- ✅ Belief lattice with automatic contradiction detection
- ✅ Tension calculation (per-node + aggregated by tag)
- ✅ 8192-bit genome (8 segments: curiosity, caution, humor, verbosity, depth, risk, empathy, identity)
- ✅ Genome mutation under tension with weighted segment mutation
- ✅ Personality expression (genome → 8 bias floats)
- ✅ LLM integration (llama.cpp with GPU offload)
- ✅ Trace visualization (animated GIF of tension evolution)
- ✅ Full pipeline: `Shadow().ingest(thread)` → evolved response

**Test Results (Dec 8, 2025):**
```
✓ 18 bits mutated in genome
✓ Tension detected: 4.9+ across identity, empathy, risk, caution
✓ 2 conditional nodes created from contradictions
✓ Real LLM response (429 chars, Llama-3.1-8B)
✓ GIF trace generated: 82.3 KB, 8 frames
✓ Mode: demo, Final step: 8
```

See `tests/results/final_test.txt` for full output.

## How To Use

```python
from shadowecology import Shadow

# load thread data
thread = {
    "messages": [
        {"role": "user", "content": "I feel alive when I'm scared..."},
        {"role": "user", "content": "Sometimes playing it safe feels like dying slowly..."},
        # ... more messages
    ]
}

# run shadow in demo mode (no vault/yubikey required)
shadow = Shadow(mode="demo")
trace, response = shadow.ingest(thread)

# save outputs
trace.save_gif("shadow_trace.gif")
print(response)
```

**Modes:**
- `Shadow()` — real mode (requires YubiKey + encrypted vault)
- `Shadow(mode="dev")` — passphrase only (no YubiKey)
- `Shadow(mode="demo")` — ephemeral in-memory state

See `demo/run.py` for a complete working example.

## How It Works

1. **Belief Extraction**: Each message → beliefs with confidence scores
2. **Contradiction Detection**: New beliefs checked against existing ones for opposing sentiment in same tag domain
3. **Edge Creation**: Contradictions get -1.0 edges, agreements get 0.5 edges
4. **Tension Calculation**: Per-node tension = confidence × contradiction_count × age_factor
5. **Genome Mutation**: High tension → bit flips in affected genome segments (weighted by tag)
6. **Personality Expression**: Genome segments → 8 bias floats (0.0-1.0)
7. **Response Generation**: Biases injected into LLM system prompt
8. **Trace Capture**: Full lattice state saved per message for visualization

**Key Design Choices:**
- Identity segment mutates 20× slower than others (personality stability)
- Curiosity has hard floor of 0.30 (always maintains baseline exploration drive)
- Ultra-conservative merge (>95% overlap + same tag) to preserve contradictions
- Decay reduces confidence of inactive beliefs over logical steps

## Technical Details

**Core:**
- Python 3.12+
- Zero ML dependencies for belief/genome logic
- Pure dict-based graph (no external graph libs)
- 8192-bit genome = 1024 bytes

**Security:**
- AES-256-GCM encryption
- HKDF-SHA512 key derivation
- YubiKey HMAC-SHA1 challenge-response (optional)
- 96-bit nonces, atomic writes with fsync

**LLM:**
- llama-cpp-python with CUDA support
- Tested with Llama-3.1-8B-Instruct (Q5_K_M quantization)
- 8 bias floats injected into system prompt
- Models loaded from `shadowecology/models/` (not committed to repo)

**Visualization:**
- matplotlib + PIL for trace GIF generation
- Node size/color mapped to tension level
- One frame per processed message

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
- ~6GB model file (e.g., Llama-3.1-8B GGUF)

## Project Philosophy

Every line of code in this repo was written by a human. No AI-generated boilerplate, no copy-paste from Stack Overflow, no tutorials. Just one developer experimenting with what happens when you treat contradictions as a feature instead of a bug.

The architecture is intentionally minimal. No frameworks, no abstractions that hide the mechanism. If you read the code, you understand exactly what's happening.

This isn't production ML. It's a sandbox for exploring cognitive pressure, personality mutation, and whether accumulated contradictions can create something that feels genuinely different over time.

## Known Limitations

- Edge creation is sentiment-based (positive/negative keywords) — crude but effective for v1
- Tension formula is simplistic (no graph topology analysis yet)
- Merge logic is ultra-conservative (might keep too many near-duplicates)
- No save/load in demo mode (ephemeral by design)
- Model path is hardcoded (should be env var or config)

## What's Next

This is v1. It works. The pipeline runs end-to-end. But there's room to explore:

- More sophisticated contradiction detection (semantic similarity, not just keywords)
- Graph-aware tension (consider node centrality, clustering)
- Conditional belief nodes ("X when Y" logic)
- Multi-identity experiments (compare genome evolution across different data sets)
- Long-term runs (feed it data over weeks/months, see what happens)

## License

MIT License — Copyright (c) 2025 Bradley R. Kinnard

The code is open. Your mind's genome is yours alone.

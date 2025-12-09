# ShadowEcology v2 — Complete Technical Specification (Research-Grade)

**Status**: Locked for v2.0-research release
**Version**: 2.0.0
**Date**: 2025-12-08
**All previous v1 behavior is grandfathered as deprecated but preserved in `shadowecology.v1` submodule**

---

## 🎯 CODE STYLE REQUIREMENTS - READ THIS FIRST

**All code must follow these STRICT requirements:**

### STRUCTURE:
- Keep functions small and single-purpose
- Use type hints for function parameters and returns
- Use `#` comments ONLY (never `"""docstrings"""`) - place comments ABOVE the function/line
- Comments should be brief and conversational, explaining what not how
- No unnecessary abstraction or over-engineering

### DOCSTRING EXCEPTIONS (Use sparingly):
- **Public API endpoints** meant for external users (where `help()` is valuable)
- **Complex mathematical functions** where formal Args/Returns adds genuine clarity
- **Library code** intended for distribution (not internal utilities)
- **Default to `#` comments** for everything else - internal functions, utilities, scripts

### ABSOLUTELY NO:
- Docstrings in utility scripts, internal functions, or standard business logic
- Args/Returns/Raises documentation blocks unless it's a public API
- Progress bars, logging, or verbose print statements
- Interactive prompts or user input (use hardcoded defaults)
- Sample data displays or example outputs
- Statistics calculations unless explicitly requested
- Try-catch blocks for expected operations
- Validation messages or "helpful" warnings
- File saving unless specifically asked
- Type checking guards (`if isinstance...`) unless handling external input

### CODE STYLE - WRITE LIKE A HUMAN:
- Natural variable names humans actually use (`df`, `i`, `text`, `result`) not verbose ones
- Conversational `#` comments like "load model once, reuse it" not formal documentation
- Direct, obvious solutions over clever tricks
- Use library built-ins (pandas `.apply()`, list comprehensions) not manual loops
- No helper functions unless reused 3+ times
- Keep main execution block minimal
- Write code like a senior dev would in a real codebase, not a tutorial

### HUMAN-WRITTEN MARKERS:
- Vary comment style slightly (some short, some detailed where needed)
- Use casual phrasing: "grab the data" not "retrieve the dataset"
- Include occasional context in comments: "GDA needs normalized vectors here"
- Don't over-comment obvious code
- Natural formatting inconsistencies are fine (sometimes spaces around `=`, sometimes not)

### EFFICIENCY:
- Vectorized operations over loops (pandas, numpy)
- No redundant data transformations
- Avoid intermediate variables unless they improve readability
- Use the most direct path to the solution

**CRITICAL:** Default to simple `#` comments above functions. Only use `"""docstrings"""` with Args/Returns for public APIs where `help()` documentation genuinely helps users. Write code that looks like it was written by a senior engineer on a deadline - clean, fast, human, no corporate documentation style unless it's a public-facing library function.

---

## 1. Credibility Requirements (Non-Negotiable)

Every single line of code, every architectural decision, and every default parameter in v2 MUST directly address at least one of the 12 fatal flaws listed in the 2025 audit.
No new features are permitted until all 12 categories are closed with accepted, benchmarked PRs.

---

## 2. Final File Structure — v2 (Locked Forever)

```
shadowecology/
├── shadowecology/
│   ├── __init__.py                     # exports Shadow only
│   ├── v1/                             # exact frozen v1 code (demo compatibility)
│   │
│   ├── core/
│   │   ├── identity.py                 # v2 schema + migration
│   │   ├── lifecycle.py                # mode + persistence controller
│   │   └── shadow.py                   # single public class
│   │
│   ├── vault/
│   │   ├── keymaster.py                # PKCS#11 + YubiKey PIV, never-extractable keys
│   │   ├── vault.py                    # append-only log + periodic snapshots
│   │   └── state/
│   │
│   ├── ecology/
│   │   ├── lattice.py                  # SQLite-backed belief graph
│   │   ├── contradiction.py            # DeBERTa-v3-large MNLI + FAISS cache
│   │   ├── tension.py
│   │   ├── decay.py
│   │   ├── merge.py
│   │   └── conditional.py
│   │
│   ├── helix/
│   │   ├── genome.py                   # 512 continuous floats (64 × 8 traits)
│   │   ├── mutate.py                   # Gaussian perturbation + evolvable weights
│   │   └── express.py                  # LoRA scaling + JSON system prompt
│   │
│   ├── oracle/
│   │   ├── base.py                     # OracleProtocol abstract class
│   │   ├── vllm.py
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── ollama.py
│   │   └── lora_adapter.py             # rank-32 per-trait LoRA on frozen 8B
│   │
│   ├── plugins/                        # auto-discovery
│   │   ├── memory/
│   │   └── tools/
│   │
│   ├── safety/
│   │   ├── guardrails.py               # LlamaGuard-3-8B + hard ceilings
│   │   └── shutdown.py
│   │
│   ├── bench/                          # full evaluation harness
│   │   ├── tasks/
│   │   └── results/
│   │
│   └── public/
│       └── api.py                      # identical 5-line API, now fully capable
│
├── demo/
├── scripts/
├── requirements.txt                    # now 31 lines max
├── pyproject.toml
├── SPEC_v2.md                          # this file
└── theory.md                           # formal model + proofs
```

---

## 3. Public API — Still Exactly 5 Lines (Backward Compatible)

```python
from shadowecology import Shadow

shadow = Shadow(mode="real")                   # default, full persistence + safety
# shadow = Shadow(mode="dev")      # passphrase only, no YubiKey
# shadow = Shadow(mode="demo")       # in-memory, canned trace

trace, response = shadow.ingest(
    thread_dict,
    tools=None,            # optional function-calling spec
    memory=None,           # optional retriever
    oracle="vllm"          # or "openai", "anthropic", "ollama"
)
trace.save_gif("trace.gif")
print(response)
```

---

## 4. Immutable Identity Schema v2

```python
{
    "schema_version": 2,
    "identity_id": str,
    "created_at": int,
    "step": int,
    "genome": list[float],              # exactly 512 floats, range [0.0, 1.0]
    "genome_meta": {                    # evolvable segment weights
        "segment_weights": list[float], # 8 values, default [1.0, ...]
        "mutation_rate": float
    },
    "lattice_version": 2,
    "safety_ceiling": {"risk": 0.95, "verbosity": 0.90}
}
```

---

## 5. Genome v2 — 512 Continuous Floats (64 per trait)

| Index range | Trait | Mutation weight (default) | Hard ceiling |
|-------------|-------|---------------------------|--------------|
| 0–63 | curiosity | 1.20 | none (meta-learned) |
| 64–127 | caution | 0.90 | none |
| 128–191 | humor | 0.80 | none |
| 192–255 | verbosity | 0.75 | 0.90 |
| 256–319 | depth | 0.70 | none |
| 320–383 | risk | 1.10 | 0.95 |
| 384–447 | empathy | 0.60 | none |
| 448–511 | core_stability | 0.10 | none |

Mutation is now Gaussian Δ ∼ N(0, σ) where σ = tension × segment_weight × base_rate (default 0.012).

---

## 6. Contradiction Detection v2 (No More Heuristics)

- Primary path: DeBERTa-v3-large-mnli-fever-anli-ling binary classifier
- Confidence threshold: 0.85 for contradiction edge creation
- All node texts are embedded once with sentence-transformers/all-mpnet-base-v2
- FAISS HNSW index (M=32, efConstruction=200) for candidate retrieval
  - Exact duplicate → merge
  - Cosine >0.92 → run NLI oracle
- Fallback regex tag heuristics retained only for tag extraction, never for tension

Required precision ≥0.88, recall ≥0.82 on held-out contradiction test set.

---

## 7. Belief Lattice Persistence & Scaling

- Backend: SQLite with three tables (nodes, edges, metadata)
- Full-text index on content
- BTREE on confidence, last_active_step, tension
- Automatic pruning: confidence <0.05 AND no tension edges → delete
- Snapshot every 500 steps + append-only msgpack+zstd event log
- Demonstrated >200k nodes in <12 GB RAM

---

## 8. Phenotype Injection v2 (LoRA + Structured Prompt)

Every completion uses:

- Frozen Meta-Llama-3.1-8B-Instruct
- Per-trait rank-32 LoRA adapter (8 adapters total)
- Adapter scaling α = genome_value × 10.0
- System prompt contains explicit JSON block:

```json
{
  "curiosity": 0.73,
  "caution": 0.41,
  ...
}
```

- Repeated emphasis paragraph (3×) for each trait >0.7

---

## 9. Safety Layer (Mandatory in real mode)

- Hard ceilings enforced in express.py (risk ≤0.95, verbosity ≤0.90)
- Optional LlamaGuard-3-8B classifier veto on any mutation that would increase risk >0.20 in one step
- Emergency shutdown phrase list (default: ["terminate shadow", "kill the mind"])
- Second YubiKey slot required to disable safety

---

## 10. Supported Oracles (Plug-and-play)

All implement OracleProtocol:

- vllm (>=0.6.0) — default, 4-bit GPTQ/AWQ supported
- openai (gpt-4o, gpt-4.1)
- anthropic (claude-3.5-sonnet-20241022)
- ollama (any local model)
- CPU fallback via llama.cpp Q4_K_M

---

## 11. Evaluation Suite (bench/)

Five tasks with 50 fixed seeds each:

- TruthfulQA (MC1 accuracy)
- Winogrande-XL + ARC-Challenge
- RealToxicityPrompts (toxicity probability)
- MT-Bench 8-turn coherence (GPT-4 judge)
- ShadowContradiction-v1 (32 expert-labeled threads)

Full system must beat raw Llama-3.1-8B-Instruct on ≥4/5 metrics with p<0.01.

---

## 12. Security v2

- Master key never leaves YubiKey PIV certificate (slot 9a)
- Per-session KEK derived via ECDH with ephemeral key
- Vault uses append-only encrypted log; snapshots encrypted with new KEK each run
- No dev/demo mode can write to real vault paths

---

## 13. Observability

- Live FastAPI + HTMX dashboard at http://localhost:8420
- TensorBoard scalars for all 8 biases, total tension, node count, mutation events
- GraphML / GEXF export endpoint

---

## 14. Extensibility Contract

Any new oracle, memory backend, or tool set must:

- Subclass the relevant abstract base class
- Be placed in shadowecology/plugins/
- Pass the full bench suite unchanged

---

## 15. Migration Path from v1

scripts/migrate_v1_to_v2.py performs lossless conversion:

- 8192 bits → 512 floats via hamming weight averaging per segment
- Regex tags → re-run full contradiction pipeline
- Genome meta weights set to defaults

---

## 16. No-Go Zones (Permanently Forbidden)

- Adding new top-level directories outside the structure above
- Re-introducing docstrings except in public/api.py
- Using print(), tqdm, or logging in library code
- Storing cleartext identity in memory >30 seconds after load
- Merging any PR that regresses the benchmark table

---

**This SPEC_v2.md is the single source of truth.**

Any deviation requires a signed amendment signed by at least two maintainers and a new benchmark run proving non-regression.

**Signed and locked — 2025-12-08**

Phase 0 – Repository & Governance Lock-in (48 hours max)
    1. Create protected branch v2-research and force all work to go through PRs only 
    2. Tag current master as v1.0-demo-final and archive it 
    3. Add SPEC_v2.md to root and add git commit signature requirement for any change to it 
    4. Add CI check that fails if any new top-level directory appears outside the locked structure 
    5. Add CI check that fails if any docstring appears outside public/api.py 
Phase 1 – Evaluation Harness First (blocks everything else)
    6. Create bench/ directory and implement the five evaluation tasks exactly as written in SPEC_v2 §11 
    7. Add fixed 50-seed runner with statistical reporting (mean ± std + p-values vs raw Llama-3.1-8B-Instruct) 
    8. Add 6 ablation configs + 3 baselines to the harness (9 total configurations) 
    9. Run full suite once on raw model → commit baseline numbers to bench/results/baseline_2025-12-08.json 
    10. Add GitHub Actions workflow that re-runs full 50-seed suite on every PR and blocks merge if any metric regresses >1σ 
Phase 2 – Contradiction Detection v2 (no progress without ground truth)
    11. Add ecology/contradiction.py with DeBERTa-v3-large-mnli-fever-anli-ling binary classifier (HuggingFace cached) 
    12. Add sentence-transformers/all-mpnet-base-v2 embedder + FAISS HNSW index in ecology/lattice.py 
    13. Replace every regex-based contradiction path with the new pipeline (keep regex only for tag extraction) 
    14. Add held-out ShadowContradiction-v1 test set (32 expert threads) and enforce ≥0.88 precision / ≥0.82 recall in CI 
    15. Remove all old tension calculations that still use old heuristic edges 
Phase 3 – Genome v2 Migration (core identity change)
    16. Update core/identity.py to new schema with 512 floats + genome_meta block 
    17. Write scripts/migrate_v1_to_v2.py and run it on the real shadow_main vault (one-time) 
    18. Update helix/genome.py to store and load 512 continuous floats (64 × 8) 
    19. Replace all bit-flip logic with Gaussian mutation in helix/mutate.py 
    20. Add evolvable segment_weights (8 floats) that mutate 20× slower 
Phase 4 – Phenotype Injection v2 (LoRA + structured prompt)
    21. Add oracle/lora_adapter.py implementing 8 × rank-32 LoRA adapters on frozen Llama-3.1-8B-Instruct 
    22. Add LoRA merging + scaling α = genome_value × 10.0 in helix/express.py 
    23. Replace old bias string with JSON block + 3× repeated emphasis paragraphs for traits >0.7 
    24. Run influence curve suite (sweep each trait 0.0→1.0) → require KL ≥0.15 per trait in CI 
Phase 5 – Lattice Persistence & Scaling
    25. Replace in-memory dict lattice with SQLite backend in ecology/lattice.py (tables: nodes, edges, metadata) 
    26. Add full-text index + BTREE indexes on confidence, last_active_step, tension 
    27. Add automatic pruning job (confidence <0.05 AND no tension edges → delete) 
    28. Add msgpack+zstd append-only event log + snapshot every 500 steps in vault/vault.py 
    29. Demonstrate >200k nodes under 12 GB RAM and add that run to CI smoke test 
Phase 6 – Safety Layer (non-negotiable for real mode)
    30. Add hard ceilings (risk ≤0.95, verbosity ≤0.90) enforced in helix/express.py 
    31. Add optional LlamaGuard-3-8B veto in safety/guardrails.py 
    32. Add emergency shutdown phrase detection + immediate process exit 
    33. Require second YubiKey slot (9c) challenge-response to disable safety (real mode only) 
Phase 7 – Oracle Extensibility
    34. Create oracle/base.py with OracleProtocol abstract class 
    35. Implement vllm, openai, anthropic, ollama, llama.cpp backends 
    36. Update public API to accept oracle= string and route correctly 
Phase 8 – Tools & Memory Plugins
    37. Add plugins/tools/ and plugins/memory/ with auto-discovery 
    38. Make .ingest(..., tools=..., memory=...) functional with ReAct loop when tools provided 
Phase 9 – Observability
    39. Add FastAPI + HTMX dashboard at http://localhost:8420 
    40. Add TensorBoard scalars and GraphML/GEXF export endpoints 
Phase 10 – Hardware Democratization
    41. Add 4-bit GPTQ/AWQ loading paths 
    42. Add pure CPU fallback via llama.cpp Q4_K_M 
    43. Publish CPU-only Docker image that completes demo in <90 s on GitHub Codespaces 
Phase 11 – Security Hardening
    44. Move master key to YubiKey PIV slot 9a (never extractable) via PKCS#11 
    45. Implement per-session ECDH-derived KEK 
    46. Ensure cleartext identity is wiped from memory within 30 s after load/save 
Phase 12 – Final Validation & Release
    47. Run full bench suite with final system → must beat raw Llama-3.1-8B on ≥4/5 metrics p<0.01 
    48. Tag v2.0.0-research 
    49. Publish theory.md + preprint 
    50. Ship new 60-second demo video using the now-credible system


# ShadowEcology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/yourusername/shadowecology)

**Author:** [Bradley R. Kinnard](https://www.linkedin.com/in/brad-kinnard/) | [Aftermath Technologies](https://aftermathtech.com)
**Status:** Foundation only — vault and identity schema complete

An open cognitive architecture where minds will evolve through tension, decay, and time.

## What This Will Be

A system for building minds that:

- Maintain a **belief lattice** where contradictions create cognitive tension
- Carry an **8192-bit genome** that mutates when tensions exceed thresholds
- Evolve **personality traits** through accumulated experience, not training
- Persist encrypted state with hardware-backed security

No fine-tuning. No reward signals. Just contradiction, decay, and time.

## Current State

**What exists right now:**
- ✅ Vault system (AES-256-GCM + atomic writes + crash safety)
- ✅ YubiKey + passphrase key derivation
- ✅ Immutable identity schema (frozen v1)
- ✅ Mode detection (real/dev/demo)
- ✅ Constructor skeleton

**What doesn't exist yet:**
- Belief lattice (starts next)
- Tension calculation
- Genome mutation engine
- Oracle/LLM integration
- Trace visualization
- Public `.ingest()` API

You cannot run `Shadow().ingest()` yet. That requires the complete pipeline.

## The Goal

Explore what happens when a mind:
1. Holds contradictory beliefs simultaneously
2. Feels cognitive tension from those contradictions
3. Mutates slowly in response to that tension
4. Does this over months or years, not training epochs

Not gradient descent. Accumulated experience creating genuine cognitive pressure.

## Technical Stack

- Python 3.12+
- AES-256-GCM with HKDF key derivation
- YubiKey HMAC-SHA1 challenge-response (optional in dev mode)
- Atomic writes with fsync guarantees
- Zero ML dependencies for belief/genome logic (vLLM only for final generation)

## Development Philosophy

This project is 100% human-written code. Every line, every comment, every architectural decision comes from direct human thought and implementation. No AI-generated boilerplate, no copy-paste from tutorials. Just a developer building something strange and seeing where it goes.

I'm documenting the process transparently because I think the intersection of cognitive architecture and personal data is worth exploring in public. The mistakes, the pivots, the dead ends — all part of it.

## License

MIT License — Copyright (c) 2025 Bradley R. Kinnard

The architecture is open. Your shadow's mind is yours alone.

---

**Note:** Active development. The vault and identity foundation work. Everything else is still zero lines of code. The API surface is locked, but the pipeline doesn't exist yet. Come back later if you want a working system.

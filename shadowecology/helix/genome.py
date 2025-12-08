# Author: Bradley R. Kinnard
# shadowecology/helix/genome.py
# The 8192-bit DNA of the mind

import os


# Locked forever — 1024 bits (128 bytes) per segment
SEGMENT_RANGES = {
    "curiosity": slice(0, 128),
    "caution":   slice(128, 256),
    "humor":     slice(256, 384),
    "verbosity": slice(384, 512),
    "depth":     slice(512, 640),
    "risk":      slice(640, 768),
    "empathy":   slice(768, 896),
    "identity":  slice(896, 1024),
}


class Genome:
    # create from existing bytes (must be exactly 1024)
    def __init__(self, data: bytes):
        if len(data) != 1024:
            raise ValueError(f"Genome must be exactly 1024 bytes, got {len(data)}")
        self._data = bytes(data)  # immutable copy

    # raw 1024-byte view
    def raw(self) -> bytes:
        return self._data

    # create fresh random genome
    @classmethod
    def fresh(cls) -> "Genome":
        return cls(os.urandom(1024))

    # serialize for vault
    def to_bytes(self) -> bytes:
        return self._data

    # deserialize from vault
    @classmethod
    def from_bytes(cls, data: bytes) -> "Genome":
        return cls(data)

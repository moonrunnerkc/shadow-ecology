# Author: Bradley R. Kinnard
# shadowecology/helix/express.py
# Converts raw genome bits into 8 behavioral bias floats

from shadowecology.helix.genome import Genome, SEGMENT_RANGES


# express genome as 8 float biases (0.0–1.0)
def express(genome: Genome) -> dict[str, float]:
    raw = genome.raw()
    biases = {}

    # count set bits in each segment
    for name, byte_range in SEGMENT_RANGES.items():
        segment_bytes = raw[byte_range]
        set_bits = sum(bin(byte).count('1') for byte in segment_bytes)
        biases[name] = set_bits / 1024.0

    # hard floor on curiosity - always at least 30%
    biases["curiosity"] = max(biases["curiosity"], 0.30)

    return biases

# Author: Bradley R. Kinnard
# shadowecology/helix/mutate.py
# Tension-driven evolution - flips bits in genome segments

import random
from shadowecology.helix.genome import Genome, SEGMENT_RANGES


# Locked forever - maps tags to their genome segments
TAG_TO_SEGMENT = {
    "curiosity": "curiosity",
    "caution": "caution",
    "humor": "humor",
    "verbosity": "verbosity",
    "depth": "depth",
    "risk": "risk",
    "empathy": "empathy",
    "identity": "identity",
}


# Locked forever - mutation rates by segment (identity is 20× slower)
SEGMENT_MUTATION_WEIGHT = {
    "curiosity": 1.00,
    "caution": 0.80,
    "humor": 0.70,
    "verbosity": 0.70,
    "depth": 0.60,
    "risk": 1.00,
    "empathy": 0.50,
    "identity": 0.05,
}


# apply tension-driven mutations to genome
def mutate(genome: Genome, tension_by_tag: dict[str, float], current_step: int) -> Genome:
    data = bytearray(genome.raw())
    any_flipped = False

    for tag, tension in tension_by_tag.items():
        if tension <= 0.0:
            continue

        # get segment for this tag
        segment_name = TAG_TO_SEGMENT.get(tag)
        if not segment_name:
            continue

        weight = SEGMENT_MUTATION_WEIGHT[segment_name]
        prob = tension * weight * 0.0005

        # flip bits in this segment's byte range
        byte_range = SEGMENT_RANGES[segment_name]
        for byte_idx in range(byte_range.start, byte_range.stop):
            for bit_pos in range(8):
                if random.random() < prob:
                    data[byte_idx] ^= (1 << bit_pos)
                    any_flipped = True

    # return new genome only if something changed
    if any_flipped:
        return Genome(bytes(data))
    return genome

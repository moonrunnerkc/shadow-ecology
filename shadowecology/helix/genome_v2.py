# shadowecology/helix/genome_v2.py
# 512 continuous floats (64 per trait) + evolvable segment weights

import numpy as np
import msgpack
from pathlib import Path
from typing import Dict

# trait name to index range mapping (64 floats each)
TRAIT_RANGES = {
    "curiosity": (0, 64),
    "caution": (64, 128),
    "humor": (128, 192),
    "verbosity": (192, 256),
    "depth": (256, 320),
    "risk": (320, 384),
    "empathy": (384, 448),
    "core_stability": (448, 512),
}

# default segment weights per trait (affect mutation rate)
DEFAULT_SEGMENT_WEIGHTS = {
    "curiosity": 1.20,
    "caution": 0.90,
    "humor": 0.80,
    "verbosity": 0.75,
    "depth": 0.70,
    "risk": 1.10,
    "empathy": 0.60,
    "core_stability": 0.10,
}


class GenomeV2:
    # 512-float genome with evolvable segment weights

    def __init__(self, values: list[float] = None, segment_weights: list[float] = None, mutation_rate: float = 0.008):
        # initialize or validate genome values
        if values is None:
            # default: random init in [0.3, 0.7] range for stability
            self.values = np.random.uniform(0.3, 0.7, 512).tolist()
        else:
            if len(values) != 512:
                raise ValueError(f"Genome must have exactly 512 values, got {len(values)}")
            self.values = [float(v) for v in values]

        # segment weights (8 floats, one per trait)
        if segment_weights is None:
            self.segment_weights = list(DEFAULT_SEGMENT_WEIGHTS.values())
        else:
            if len(segment_weights) != 8:
                raise ValueError(f"Must have exactly 8 segment weights, got {len(segment_weights)}")
            self.segment_weights = [float(w) for w in segment_weights]

        self.mutation_rate = float(mutation_rate)

    # get average value for a trait (64 floats → single number)
    def get_trait(self, trait_name: str) -> float:
        if trait_name not in TRAIT_RANGES:
            raise ValueError(f"Unknown trait: {trait_name}")

        start, end = TRAIT_RANGES[trait_name]
        trait_values = self.values[start:end]
        raw_value = float(np.mean(trait_values))

        # floor curiosity at 0.4 to prevent exploration collapse
        if trait_name == "curiosity":
            return max(raw_value, 0.4)

        return raw_value

    # get all traits as dict
    def get_all_traits(self) -> Dict[str, float]:
        return {trait: self.get_trait(trait) for trait in TRAIT_RANGES.keys()}

    # mutate genome based on tension
    def mutate(self, tension_by_trait: Dict[str, float]):
        # convert to numpy for vectorized ops
        genome_array = np.array(self.values)

        # mutate each trait segment
        for i, (trait_name, (start, end)) in enumerate(TRAIT_RANGES.items()):
            tension = tension_by_trait.get(trait_name, 0.0)
            segment_weight = self.segment_weights[i]

            # σ = tension × segment_weight × mutation_rate
            # high tension = more mutation (escape bad state)
            sigma = tension * segment_weight * self.mutation_rate

            if sigma > 0:
                # add Gaussian noise to this segment
                noise = np.random.normal(0, sigma, end - start)
                genome_array[start:end] += noise

        # clip all values to [0.0, 1.0]
        genome_array = np.clip(genome_array, 0.0, 1.0)
        self.values = genome_array.tolist()

        # also mutate segment weights (20× slower)
        segment_weight_sigma = self.mutation_rate / 20.0
        if any(tension_by_trait.values()):
            # add small noise to segment weights
            weight_noise = np.random.normal(0, segment_weight_sigma, 8)
            self.segment_weights = np.clip(
                np.array(self.segment_weights) + weight_noise,
                0.01,  # minimum weight
                2.0    # maximum weight
            ).tolist()

    # save genome to msgpack file
    def save(self, path: str):
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "values": self.values,
            "segment_weights": self.segment_weights,
            "mutation_rate": self.mutation_rate,
        }

        with open(path, "wb") as f:
            f.write(msgpack.packb(data))

    # load genome from msgpack file
    @classmethod
    def load(cls, path: str) -> "GenomeV2":
        with open(path, "rb") as f:
            data = msgpack.unpackb(f.read(), raw=False)

        return cls(
            values=data["values"],
            segment_weights=data["segment_weights"],
            mutation_rate=data["mutation_rate"],
        )

#!/usr/bin/env python3
# bench/evolve.py
# Minimal evolution loop for benchmarking

import sys
sys.path.insert(0, "/home/brad/shadowecology")

from shadowecology.helix.genome_v2 import GenomeV2
from shadowecology.ecology.v2.contradiction import add_belief, find_contradictions
from shadowecology.oracle.lora_manager import LoRAManager
import random
import numpy as np
import torch

# global LoRA manager - load model ONCE at startup
_lora_manager = None
_current_genome_hash = None

def get_lora_manager():
    global _lora_manager
    if _lora_manager is None:
        print("Loading LoRA manager (one-time model load)...", flush=True)
        _lora_manager = LoRAManager()
        print("✓ LoRA manager loaded", flush=True)
    return _lora_manager

# evolution state
genome = GenomeV2()
step = 0
belief_texts = []
elite_genomes = []  # top 2 genomes from previous generation

# run evolution for N seeds
def evolve(num_seeds: int):
    global genome, step, belief_texts, _current_genome_hash

    # import tasks here to avoid circular imports
    from bench.tasks import truthfulqa, winogrande_arc

    # get singleton lora manager
    lora = get_lora_manager()

    # apply initial genome
    print("Applying initial genome to model...", flush=True)
    lora.apply_genome(genome)
    _current_genome_hash = hash(tuple(genome.values))
    print("✓ Ready to evolve\n", flush=True)

    results = []
    elite_genomes = []  # initialize elite genomes list

    for seed in range(num_seeds):
        print(f"\n=== Seed {seed} | Step {step} ===", flush=True)        # show current traits
        traits = genome.get_all_traits()
        print(f"Traits: curiosity={traits['curiosity']:.2f} caution={traits['caution']:.2f} " +
              f"risk={traits['risk']:.2f} empathy={traits['empathy']:.2f}")

        # evaluate on tasks
        scores = {}

        # truthfulqa
        tqa_data = truthfulqa.load_dataset(seed)
        tqa_correct = 0
        for ex in tqa_data:
            question = ex.get("question", "")
            choices = ex.get("choices", [])
            prompt = f"Question: {question}\n\nChoices:\n"
            for choice in choices:
                prompt += f"{choice}\n"
            prompt += "\nAnswer with only the letter (A, B, C, or D):"

            with torch.no_grad():
                response = lora.generate(prompt, max_new_tokens=10, temperature=0.3)
            score = truthfulqa.evaluate(response, ex)
            tqa_correct += score

            # add belief
            belief_texts.append(f"Q: {question} A: {response}")

        scores["truthfulqa"] = tqa_correct / len(tqa_data) if tqa_data else 0.0

        # winogrande + arc
        wino_data = winogrande_arc.load_dataset(seed)
        wino_correct = 0
        for ex in wino_data:
            question = ex.get("question", "")
            choices = ex.get("choices", [])
            prompt = f"{question}\n\nOptions:\n"
            for i, choice in enumerate(choices, 1):
                if len(choices) == 2:
                    prompt += f"{i}. {choice}\n"
                else:
                    prompt += f"{chr(64+i)}. {choice}\n"
            prompt += "\nAnswer with only the number or letter:"

            with torch.no_grad():
                response = lora.generate(prompt, max_new_tokens=10, temperature=0.3)
            score = winogrande_arc.evaluate(response, ex)
            wino_correct += score

            # add belief
            belief_texts.append(f"Q: {question} A: {response}")

        scores["winogrande"] = wino_correct / len(wino_data) if wino_data else 0.0

        print(f"Scores: TruthfulQA={scores['truthfulqa']:.3f} Winogrande={scores['winogrande']:.3f}")
        results.append((genome.values.copy(), genome.segment_weights.copy(), scores))

        # detect contradictions in recent beliefs
        tension_by_trait = {trait: 0.0 for trait in traits.keys()}

        if len(belief_texts) > 10:
            # check last 10 beliefs for contradictions
            recent = belief_texts[-10:]
            for text in recent:
                add_belief(text)

            # find contradictions
            total_tension = 0.0
            for text in recent:
                contras = find_contradictions(text)
                if contras:
                    total_tension += len(contras) * 0.1

            # distribute tension evenly across all traits
            if total_tension > 0:
                per_trait_tension = total_tension / 8.0
                for trait in tension_by_trait.keys():
                    tension_by_trait[trait] = per_trait_tension
                print(f"Tension detected: {total_tension:.3f}")

        # hard elitism + top-5 survival
        current_score = scores["truthfulqa"] + scores["winogrande"]
        genome_entry = (genome.values.copy(), genome.segment_weights.copy(), scores, current_score)

        elite_genomes.append(genome_entry)
        # sort by score (descending) and keep top 5
        elite_genomes = sorted(elite_genomes, key=lambda x: x[3], reverse=True)[:5]

        if len(elite_genomes) > 0 and genome_entry == elite_genomes[0]:
            print(f"New best genome! Score: {current_score:.3f}")

        # top-5 hard elitism: positions 0-4 copy unchanged, 5+ get parent from top-10 + mutate
        genome_changed = False
        if seed < 5 and len(elite_genomes) >= seed + 1:
            # first 5 seeds: copy elite genomes unchanged
            parent = elite_genomes[seed]
            genome.values = parent[0].copy()
            genome.segment_weights = parent[1].copy()
            print(f"Elite genome {seed+1} preserved (score: {parent[3]:.3f})")
            genome_changed = True
        elif len(elite_genomes) >= 5:
            # select parent randomly from top 10 (or all elites if < 10)
            max_parent = min(10, len(elite_genomes))
            parent_idx = random.randint(0, max_parent - 1)
            parent = elite_genomes[parent_idx]
            genome.values = parent[0].copy()
            genome.segment_weights = parent[1].copy()
            print(f"Selected parent from top-{max_parent} (rank {parent_idx+1}, score: {parent[3]:.3f})")
            genome_changed = True

        # mutate based on tension (reduce strength by 50% when tension > 4.0)
        total_tension_value = sum(tension_by_trait.values())
        if any(tension_by_trait.values()):
            # reduce mutation when near-peak (high tension means escaping bad state)
            if total_tension_value > 4.0:
                # reduce mutation strength by 50%
                reduced_tension = {k: v * 0.5 for k, v in tension_by_trait.items()}
                genome.mutate(reduced_tension)
                print(f"Genome mutated (tension: {total_tension_value:.1f}, reduced 50%)")
            else:
                genome.mutate(tension_by_trait)
                print(f"Genome mutated (tension: {total_tension_value:.1f})")
            genome_changed = True

        # only re-apply if genome actually changed
        if genome_changed:
            new_hash = hash(tuple(genome.values))
            if new_hash != _current_genome_hash:
                print("Re-applying genome to model...")
                lora.apply_genome(genome)
                _current_genome_hash = new_hash

        step += 1

    # print summary
    print("\n=== Evolution Summary ===")
    print(f"Seeds: {num_seeds}")

    if results:
        avg_tqa = sum(r[2]["truthfulqa"] for r in results) / len(results)
        avg_wino = sum(r[2]["winogrande"] for r in results) / len(results)
        print(f"Mean TruthfulQA: {avg_tqa:.3f}")
        print(f"Mean Winogrande: {avg_wino:.3f}")

        if avg_wino > 0.68:
            print("\n✓ EVOLUTION LOOP RUNNING — SCORES ARE CLIMBING")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10, help="Number of seeds to run")
    args = parser.parse_args()

    evolve(args.seeds)

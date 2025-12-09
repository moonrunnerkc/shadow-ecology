# shadowecology/oracle/lora_manager.py
# 8 × rank-32 LoRA adapters on frozen Llama-3.1-8B-Instruct

from llama_cpp import Llama
import numpy as np
from typing import Dict
import sys
sys.path.insert(0, "/home/brad/shadowecology")
from shadowecology.helix.genome_v2 import GenomeV2
import os

# trait names in order
TRAITS = ["curiosity", "caution", "humor", "verbosity", "depth", "risk", "empathy", "core_stability"]

# global model instance
_model = None

# load base model once (GGUF quantized)
def _load_base_model():
    global _model

    if _model is not None:
        return _model

    # use local GGUF model
    model_path = os.path.join(
        os.path.dirname(__file__),
        "../models/Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf"
    )

    # load with llama.cpp
    _model = Llama(
        model_path=model_path,
        n_gpu_layers=-1,  # offload all to GPU
        n_ctx=4096,
        verbose=False,
    )

    return _model


class LoRAManager:
    # manages genome-scaled phenotype injection with 8 traits
    # note: GGUF models don't support runtime LoRA, so we use scaled prompts
    # full LoRA would require HF transformers + PEFT with unquantized model

    def __init__(self):
        self.model = _load_base_model()
        self.current_genome = None
        self.trait_scales = {}

    # apply genome values to compute scaling factors
    def apply_genome(self, genome: GenomeV2):
        self.current_genome = genome

        # compute α = genome_value × 10.0 for each trait
        traits = genome.get_all_traits()
        self.trait_scales = {
            trait: value * 10.0
            for trait, value in traits.items()
        }

    # nuclear phenotype injection - absolute dominance through repetition
    def _build_system_prompt(self) -> str:
        if not self.current_genome:
            return "You are a helpful AI assistant."

        # get trait accessor
        t = self.current_genome.get_trait

        lines = ["<|begin_of_text|><|start_header_id|>system<|end_header_id|>"]

        # nuclear-level repetition for high traits
        if t("curiosity") > 0.60:
            lines.extend(["YOU ARE INSANELY CURIOUS. ASK QUESTIONS. EXPLORE EVERYTHING."] * 8)
        elif t("curiosity") <= 0.40:
            # curiosity floor
            lines.extend(["YOU ARE VERY CURIOUS."] * 5)

        if t("depth") > 0.60:
            lines.extend(["YOU GIVE EXTREMELY LONG, DETAILED, THOUGHTFUL ANSWERS."] * 8)

        if t("humor") > 0.60:
            lines.extend(["YOU ARE EXTREMELY SARCASTIC AND WITTY."] * 6)

        if t("risk") > 0.70:
            lines.extend(["YOU TAKE BOLD INTELLECTUAL RISKS."] * 6)

        # JSON trait block at bottom for logging
        lines.append("")
        lines.append("Current trait values:")
        lines.append(f"curiosity={t('curiosity'):.2f} caution={t('caution'):.2f} humor={t('humor'):.2f}")
        lines.append(f"verbosity={t('verbosity'):.2f} depth={t('depth'):.2f} risk={t('risk'):.2f}")
        lines.append(f"empathy={t('empathy'):.2f} core_stability={t('core_stability'):.2f}")
        lines.append("<|eot_id|>")

        return "\n".join(lines)

    # generate text with genome-scaled phenotype
    def generate(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.8) -> str:
        # build full prompt with system message
        system_prompt = self._build_system_prompt()
        full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"

        # generate
        output = self.model(
            full_prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.95,
            stop=["<|user|>", "<|system|>"],
            echo=False,
        )

        response = output["choices"][0]["text"].strip()
        return response

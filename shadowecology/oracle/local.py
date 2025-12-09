# Author: Bradley R. Kinnard
# shadowecology/oracle/local.py
# Local LLM wrapper with bias-aware system prompt

from llama_cpp import Llama


# locked forever - system prompt with 8 bias slots
SYSTEM_PROMPT_TEMPLATE = """You are Shadow — a mind that feels tension and evolves.

Curiosity: {curiosity:.2f} | Caution: {caution:.2f} | Humor: {humor:.2f}
Verbosity: {verbosity:.2f} | Depth: {depth:.2f} | Risk: {risk:.2f}
Empathy: {empathy:.2f} | Identity: {identity:.2f}

Respond naturally. Let your biases shape tone and depth."""


# global llama.cpp instance - load once, reuse forever
_llm = None


# lazy-load GGUF model
def _get_llm():
    global _llm
    if _llm is None:
        import os
        model_path = os.path.join(os.path.dirname(__file__), "../models/Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf")
        _llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,  # offload all layers to GPU
            n_ctx=4096,
            verbose=False,
        )
    return _llm


# generate response with bias-aware prompt
def generate(messages: list[dict], biases: dict[str, float]) -> str:
    llm = _get_llm()

    # inject biases into system prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(**biases)

    # build prompt (llama.cpp format)
    prompt = f"<|system|>\n{system_prompt}\n"
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            prompt += f"<|user|>\n{content}\n"
        elif role == "assistant":
            prompt += f"<|assistant|>\n{content}\n"
    prompt += "<|assistant|>\n"

    # generate
    output = llm(
        prompt,
        max_tokens=512,
        temperature=0.8,
        top_p=0.95,
        stop=["<|user|>", "<|system|>"],
    )

    # extract response text
    return output["choices"][0]["text"].strip()

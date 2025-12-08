# Author: Bradley R. Kinnard
# shadowecology/oracle/local.py
# vLLM wrapper with bias-aware system prompt

from vllm import LLM, SamplingParams


# locked forever - system prompt with 8 bias slots
SYSTEM_PROMPT_TEMPLATE = """You are Shadow — a mind that feels tension and evolves.

Curiosity: {curiosity:.2f} | Caution: {caution:.2f} | Humor: {humor:.2f}
Verbosity: {verbosity:.2f} | Depth: {depth:.2f} | Risk: {risk:.2f}
Empathy: {empathy:.2f} | Identity: {identity:.2f}

Respond naturally. Let your biases shape tone and depth."""


# global vLLM instance - load once, reuse forever
_llm = None


# lazy-load vLLM model
def _get_llm():
    global _llm
    if _llm is None:
        _llm = LLM(
            model="meta-llama/Llama-3.2-3B-Instruct",
            tensor_parallel_size=1,
            gpu_memory_utilization=0.9,
        )
    return _llm


# generate response with bias-aware prompt
def generate(messages: list[dict], biases: dict[str, float]) -> str:
    llm = _get_llm()

    # inject biases into system prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(**biases)

    # build full conversation
    full_messages = [
        {"role": "system", "content": system_prompt},
        *messages
    ]

    # sampling params - balanced between creativity and coherence
    params = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        max_tokens=512,
    )

    # generate
    outputs = llm.chat(full_messages, sampling_params=params)

    # extract response text
    return outputs[0].outputs[0].text.strip()

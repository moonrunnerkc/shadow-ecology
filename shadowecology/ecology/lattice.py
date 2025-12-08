# Author: Bradley R. Kinnard
# shadowecology/ecology/lattice.py
# Belief graph structure + hard-coded tag extraction

import re
import uuid
from typing import Any

# Locked forever — guarantees all 8 genome segments can feel tension
TAG_HEURISTICS = {
    r"\b(I|me|my|myself|mine)\b": "identity",
    r"\b(feel|feeling|emotion|love|loving|hate|hating|care|caring|angry|sad|happy|joy|joyful|fear|afraid|scare|scared|scary|terrify|terrified|terrifying|excite|excited|exciting|amaze|amazed|amazing|wonder|wonderful|terrible|awful|hurt|pain)\b": "empathy",
    r"\b(risk|risky|danger|dangerous|safe|safety|bet|gamble|chance|uncertain|uncertainty|threat|hazard)\b": ["risk", "caution"],
    r"\b(what if|idea|explore|exploring|curious|wonder|imagine|maybe|possibly|potential)\b": "curiosity",
    r"\b(joke|funny|lol|lmao|sarcasm|sarcastic|roast|meme|hilarious|laugh)\b": "humor",
    r"\b(explain|because|therefore|thus|hence|reason|deep|depth|detail|detailed|analyze|complex)\b": "depth",
    r"\b(long|short|brief|concise|wordy|verbose|quick|elaborate)\b": "verbosity",
}


class Lattice:
    def __init__(self, nodes: dict | None = None, edges: dict | None = None):
        self.nodes = nodes or {}
        self.edges = edges or {}

    # extract tags from text using hard-coded patterns
    def extract_tags(self, text: str) -> list[str]:
        tags = []
        lower = text.lower()

        for pattern, tag in TAG_HEURISTICS.items():
            if re.search(pattern, lower, re.IGNORECASE):
                if isinstance(tag, list):
                    tags.extend(tag)
                else:
                    tags.append(tag)

        # unique tags only
        return list(set(tags))

    # add new belief node to the graph
    def add_belief(self, content: str, confidence: float, source: str, current_step: int) -> str:
        node_id = uuid.uuid4().hex

        self.nodes[node_id] = {
            "id": node_id,
            "content": content,
            "confidence": confidence,
            "source": source,
            "tags": self.extract_tags(content) or ["untagged"],
            "created_step": current_step,
            "last_active_step": current_step,
        }

        # init edge dict for this node
        self.edges[node_id] = {}

        # TODO: Add automatic edge creation logic
        # Should detect contradictions between new node and existing nodes
        # Based on opposing sentiment in same tag domain
        # e.g., "I love danger" vs "Danger will kill me" → contradiction edge (-1.0)
        # This is what creates tension and drives genome mutation

        return node_id

    # fetch node by ID
    def get_node(self, node_id: str) -> dict:
        return self.nodes[node_id]

    # serialize for vault
    def to_dict(self) -> dict:
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }

    # deserialize from vault
    @classmethod
    def from_dict(cls, data: dict) -> "Lattice":
        return cls(
            nodes=data.get("nodes", {}),
            edges=data.get("edges", {})
        )

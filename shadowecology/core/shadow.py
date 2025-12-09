# Author: Bradley R. Kinnard
# shadowecology/core/shadow.py
# The only public interface to shadowecology - single class, one method

from __future__ import annotations
import os
from typing import Any

from shadowecology.core.identity import Identity, fresh_identity


class Shadow:
    """The shadow - a mind that evolves through tension, decay, and time.

        Args:
            mode: Override env var - "real", "dev", or "demo"
    """

    def __init__(self, mode: str | None = None):
        # resolve mode - must be set before importing lifecycle
        if mode:
            os.environ["SHADOWECOLOGY_MODE"] = mode.lower()

        # import here to pick up env var
        from shadowecology.core.lifecycle import get_identity, current_mode
        self._current_mode = current_mode()

        # get identity based on mode
        if self._current_mode == "demo":
            self._identity: Identity = fresh_identity("demo_ephemeral")
        else:
            self._identity: Identity = get_identity()

    @property
    def mode(self) -> str:
        return self._current_mode

    @property
    def step(self) -> int:
        return self._identity.step

    def __repr__(self) -> str:
        return f"Shadow(mode={self.mode!r}, step={self.step}, id={self._identity.identity_id!r})"

    def ingest(self, thread: dict[str, Any]) -> tuple[Any, str]:
        """Process a thread and return trace + response.

            Args:
                thread: Thread data to process

            Returns:
                (trace, response) tuple
        """
        from shadowecology.oracle.trace import Trace
        from shadowecology.oracle.local import generate
        from shadowecology.helix.express import express
        from shadowecology.helix.mutate import mutate
        from shadowecology.helix.genome import Genome
        from shadowecology.ecology.lattice import Lattice
        from shadowecology.ecology.tension import tension_by_tag
        from shadowecology.ecology.decay import apply_decay
        from shadowecology.ecology.merge import attempt_merge
        from shadowecology.ecology.conditional import attempt_conditional
        from shadowecology.core.identity import Identity

        trace = Trace()
        messages = thread.get("messages", [])

        # convert stored data to working objects
        lattice = Lattice.from_dict(self._identity.lattice)
        genome = Genome.from_bytes(self._identity.genome)
        current_step = self._identity.step

        # process each message
        for msg in messages:
            current_step += 1

            # extract beliefs from message
            content = msg.get("content", "")
            if content:
                lattice.add_belief(content, 0.8, msg.get("role", "user"), current_step)

            # run ecology cycle
            all_ids = set(lattice.nodes.keys())
            apply_decay(lattice, current_step, set())
            attempt_conditional(lattice, current_step, all_ids)
            all_ids = set(lattice.nodes.keys())
            attempt_merge(lattice, current_step, all_ids)

            # calculate tension
            tension = tension_by_tag(lattice, current_step)

            # mutate genome under tension
            genome = mutate(genome, tension, current_step)

            # capture trace frame
            trace.append(lattice, current_step, tension)

        # generate response with current biases
        biases = express(genome)
        response = generate(messages, biases)

        # update identity with evolved state
        self._identity = Identity(
            schema_version=self._identity.schema_version,
            identity_id=self._identity.identity_id,
            created_at=self._identity.created_at,
            step=current_step,
            genome=genome.to_bytes(),
            lattice=lattice.to_dict()
        )

        return trace, response

# Author: Bradley R. Kinnard
# shadowecology/core/shadow.py
# The only public interface to shadowecology - single class, one method

from __future__ import annotations
import os
from typing import Any

from shadowecology.core.identity import Identity
from shadowecology.core.lifecycle import get_identity, current_mode


class Shadow:
    """The shadow - a mind that evolves through tension, decay, and time.

        Args:
            mode: Override env var - "real", "dev", or "demo"
    """

    def __init__(self, mode: str | None = None):
        # resolve mode once at construction
        if mode:
            os.environ["SHADOWECOLOGY_MODE"] = mode.lower()

        self._identity: Identity = get_identity()

    @property
    def mode(self) -> str:
        return current_mode()

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
        raise NotImplementedError("ingest() pipeline coming in Day 7-8")

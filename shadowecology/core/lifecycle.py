# Author: Bradley R. Kinnard
# shadowecology/core/lifecycle.py
# Mode detection and identity persistence - single source of truth for real/dev/demo

import os
from shadowecology.core.identity import Identity, fresh_identity, to_dict, from_dict
from shadowecology.vault.vault import load_or_create as vault_load_or_create
from shadowecology.vault.vault import save_atomic as vault_save_atomic

# detect mode once per process
_MODE = os.getenv("SHADOWECOLOGY_MODE", "real").lower()

# cache identity in real/dev to avoid re-prompting
_identity_cache: Identity | None = None

# returns "real", "dev", or "demo"
def current_mode() -> str:
    return _MODE

# load identity based on current mode
def get_identity() -> Identity:
    global _identity_cache

    if _MODE == "demo":
        # fresh dummy every time, never cached, never persisted
        return fresh_identity("demo_ephemeral")

    # real or dev - load from vault once, cache to avoid re-prompting
    if _identity_cache is None:
        data = vault_load_or_create("shadow_main")
        _identity_cache = from_dict(data)

    return _identity_cache

# persist identity if mode allows it
def persist_identity(identity: Identity) -> None:
    global _identity_cache

    if _MODE == "demo":
        # demo mode never writes to disk
        return

    # real or dev - save atomically to vault
    vault_save_atomic(identity.identity_id, to_dict(identity))
    _identity_cache = identity  # update cache

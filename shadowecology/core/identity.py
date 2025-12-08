# Author: Bradley R. Kinnard
# shadowecology/core/identity.py
# Immutable identity schema - single source of truth for what an identity is

import os
import time
from dataclasses import dataclass
from typing import Any

# Schema v1 — locked forever. No new fields, no changes.
@dataclass(frozen=True)
class Identity:
    schema_version: int
    identity_id: str
    created_at: int
    step: int
    genome: bytes
    lattice: dict[str, Any]

# create brand new identity with random genome
def fresh_identity(identity_id: str) -> Identity:
    return Identity(
        schema_version=1,
        identity_id=identity_id,
        created_at=int(time.time()),
        step=0,
        genome=os.urandom(1024),  # 8192 bits
        lattice={"nodes": {}, "edges": {}}
    )

# only legal way to advance step counter
def increment_step(identity: Identity) -> Identity:
    return Identity(
        schema_version=identity.schema_version,
        identity_id=identity.identity_id,
        created_at=identity.created_at,
        step=identity.step + 1,
        genome=identity.genome,
        lattice=identity.lattice
    )

# round-trip for vault serialization
def to_dict(identity: Identity) -> dict[str, Any]:
    return {
        "schema_version": identity.schema_version,
        "identity_id": identity.identity_id,
        "created_at": identity.created_at,
        "step": identity.step,
        "genome": identity.genome,
        "lattice": identity.lattice
    }

def from_dict(data: dict[str, Any]) -> Identity:
    return Identity(
        schema_version=data["schema_version"],
        identity_id=data["identity_id"],
        created_at=data["created_at"],
        step=data["step"],
        genome=data["genome"],
        lattice=data["lattice"]
    )

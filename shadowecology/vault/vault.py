# Author: Bradley R. Kinnard
# shadowecology/vault/vault.py
# AES-256-GCM encryption/decryption + atomic writes. No knowledge of identity schema.

import os
import msgpack  # type: ignore
from pathlib import Path
from typing import Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from shadowecology.vault.keymaster import get_master_key_once, derive_identity_key

# one place to change if we ever move the vault
VAULT_DIR = Path(__file__).parent / "state"
VAULT_DIR.mkdir(exist_ok=True)


# derive per-identity key from cached master
def identity_key(identity_id: str) -> bytes:
    master = get_master_key_once()
    return derive_identity_key(master, identity_id)


# msgpack + AES-256-GCM, returns nonce || ciphertext || tag
def encrypt_identity(identity_id: str, data: dict[str, Any]) -> bytes:
    key = identity_key(identity_id)
    nonce = os.urandom(12)  # 96-bit nonce, spec requirement
    aead = AESGCM(key)

    pt = msgpack.packb(data, use_bin_type=True)
    ct = aead.encrypt(nonce, pt, None)  # no AAD in v1

    return nonce + ct


# reverse of encrypt - split nonce, decrypt, unpack
def decrypt_identity(identity_id: str, blob: bytes) -> dict[str, Any]:
    key = identity_key(identity_id)
    aead = AESGCM(key)

    nonce, ciphertext = blob[:12], blob[12:]
    pt = aead.decrypt(nonce, ciphertext, None)

    return msgpack.unpackb(pt, raw=False)


# atomic save: write to .tmp, fsync, rename (crash-safe even on power loss)
def save_atomic(identity_id: str, data: dict[str, Any]) -> None:
    final_path = VAULT_DIR / f"{identity_id}.msgpack.enc"
    tmp_path = final_path.with_suffix(".tmp")

    encrypted = encrypt_identity(identity_id, data)

    with open(tmp_path, 'wb') as f:
        f.write(encrypted)
        f.flush()
        os.fsync(f.fileno())

    tmp_path.replace(final_path)


# load existing identity or die
def load(identity_id: str) -> dict[str, Any]:
    path = VAULT_DIR / f"{identity_id}.msgpack.enc"
    if not path.exists():
        print(f"No vault file for {identity_id}")
        raise SystemExit(1)
    return decrypt_identity(identity_id, path.read_bytes())


# load if exists, else create fresh identity with random genome
def load_or_create(identity_id: str) -> dict[str, Any]:
    path = VAULT_DIR / f"{identity_id}.msgpack.enc"
    if path.exists():
        return load(identity_id)
    else:
        fresh: dict[str, Any] = {
            "schema_version": 1,
            "identity_id": identity_id,
            "created_at": int(__import__("time").time()),
            "step": 0,
            "genome": os.urandom(1024),  # 8192 bits
            "lattice": {"nodes": {}, "edges": {}},
        }
        save_atomic(identity_id, fresh)
        return fresh

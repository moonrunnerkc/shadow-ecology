# Author: Bradley R. Kinnard
# shadowecology/vault/keymaster.py
# All key derivation lives here and only here. Nothing else touches crypto primitives.

import os
import getpass
from hashlib import pbkdf2_hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# dev mode bypasses physical YubiKey but still uses passphrase encryption
_MODE = os.getenv("SHADOWECOLOGY_MODE", "real").lower()

def yubikey_challenge() -> bytes:
    """Get deterministic 20-byte HMAC-SHA1 response from YubiKey slot 2.

            Returns:
                20-byte response derived from fixed challenge.

            Raises:
                SystemExit: If YubiKey not detected or slot 2 not configured.
    """
    # dev mode: skip physical YubiKey, use fixed dummy
    if _MODE == "dev":
        return b"\x00" * 20

    # Fixed challenge so same YubiKey always returns same response
    challenge = b"shadowecology-master-key-salt-v1"

    # Call ykman externally — guaranteed in PATH from Day 0
    raw = os.popen(
        f'ykman otp chalresp --totp 2 {challenge.hex()}'
    ).read().strip()

    if not raw or len(raw) != 40:  # 20 bytes → 40 hex chars
        print("No YubiKey detected or slot 2 not configured")
        raise SystemExit(1)

    return bytes.fromhex(raw)


def derive_master_key() -> bytes:
    """Derive 32-byte master key from passphrase + YubiKey using PBKDF2-HMAC-SHA512.

            Prompts user for passphrase, combines with YubiKey response, and derives
            cryptographically strong master key using 100,000 iterations.

            Returns:
                32-byte master key suitable for HKDF expansion.

            Raises:
                SystemExit: If YubiKey not available.
    """
    passphrase = getpass.getpass("Passphrase: ")
    yubikey_resp = yubikey_challenge()  # 20 bytes

    # Use first 16 bytes of response as salt — unique per physical key
    salt = yubikey_resp[:16]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt,
        iterations=100_000,
    )

    # Key material = passphrase bytes + full 20-byte yubikey response
    master_key = kdf.derive(passphrase.encode() + yubikey_resp)
    return master_key


def derive_identity_key(master_key: bytes, identity_id: str) -> bytes:
    """Derive per-identity 32-byte encryption key from master key using HKDF-SHA512.

            Args:
                master_key: 32-byte master key from derive_master_key().
                identity_id: Unique identity identifier (e.g., "shadow_main").

            Returns:
                32-byte AES-256-GCM key unique to this identity.
    """
    hkdf = HKDFExpand(
        algorithm=hashes.SHA512(),
        length=32,
        info=f"shadowecology-v1-{identity_id}".encode(),
    )
    return hkdf.derive(master_key)


# Cache master key on module level so we don't re-prompt during one process
_master_key_cache = None

def get_master_key_once() -> bytes:
    """Get master key with caching to avoid repeated passphrase prompts.

            First call prompts for passphrase and queries YubiKey. Subsequent calls
            in same process return cached key without re-prompting.

            Returns:
                32-byte master key.

            Raises:
                SystemExit: If YubiKey not available on first call.
    """
    global _master_key_cache
    if _master_key_cache is not None:
        return _master_key_cache
    _master_key_cache = derive_master_key()
    return _master_key_cache


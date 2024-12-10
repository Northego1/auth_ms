import hashlib


def hash_fingerprint(fingerprint: bytes) -> bytes:
    hash_value = hashlib.sha256(fingerprint).digest()
    return hash_value
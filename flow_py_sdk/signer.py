import hashlib
from abc import ABC, abstractmethod
from enum import Enum

from ecdsa import SigningKey, NIST256p, SECP256k1
from ecdsa.curves import Curve


class SignAlgo(Enum):
    ECDSA_P256 = 1
    ECDSA_secp256k1 = 2

    @classmethod
    def from_string(cls, s: str) -> 'SignAlgo':
        return {
            "ECDSA_P256": SignAlgo.ECDSA_P256,
            "ECDSA_secp256k1": SignAlgo.ECDSA_secp256k1
        }[s]


class HashAlgo(Enum):
    SHA2_256 = 1
    SHA2_384 = 2
    SHA3_256 = 3
    SHA3_384 = 4

    @classmethod
    def from_string(cls, s: str) -> 'HashAlgo':
        return {
            "SHA2_256": HashAlgo.SHA2_256,
            "SHA2_384": HashAlgo.SHA2_384,
            "SHA3_256": HashAlgo.SHA3_256,
            "SHA3_384": HashAlgo.SHA3_384,
        }[s]


class Signer(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def sign(self, message: bytes) -> bytes:
        pass


class InMemorySigner(Signer):
    def __init__(self, hash_algo: HashAlgo, sign_algo: SignAlgo, key_hex: str) -> None:
        super().__init__()
        self.hash_algo = hash_algo
        self.key = SigningKey.from_string(bytes.fromhex(key_hex), curve=get_signing_curve(sign_algo))

    def sign(self, message: bytes) -> bytes:
        m = create_hasher(self.hash_algo)
        m.update(message)
        hash_ = m.digest()
        return self.key.sign_digest_deterministic(hash_)

    def public_key(self) -> bytes:
        return self.key.verifying_key.to_string()


def create_hasher(hash_id: HashAlgo):
    if hash_id is HashAlgo.SHA2_256:
        return hashlib.sha256()
    if hash_id == HashAlgo.SHA2_384:
        return hashlib.sha384()
    if hash_id == HashAlgo.SHA3_256:
        return hashlib.sha3_256()
    if hash_id == HashAlgo.SHA3_384:
        return hashlib.sha3_384()
    raise NotImplementedError()


def get_signing_curve(sign_algo: SignAlgo) -> Curve:
    if sign_algo == SignAlgo.ECDSA_P256:
        return NIST256p
    if sign_algo == SignAlgo.ECDSA_secp256k1:
        return SECP256k1
    raise NotImplementedError()

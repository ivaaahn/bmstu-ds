from Crypto.Hash import SHA3_256
from Crypto.Hash.SHA3_256 import SHA3_256_Hash
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from .misc import read_rsa_keys, read_signature, write_rsa_keys, write_signature


class Signature:
    @classmethod
    def make(cls, data: bytes, bits: int = 2048) -> tuple[bytes, bytes]:
        rsa_keys = RSA.generate(bits)

        hashed_data = cls._hash_data(data)
        signature = pkcs1_15.new(rsa_keys).sign(hashed_data)
        exported_keys = rsa_keys.publickey().exportKey()

        write_signature(signature)
        write_rsa_keys(exported_keys)

        return signature, exported_keys

    @classmethod
    def verify(cls, data: bytes) -> bool:
        hashed_data = cls._hash_data(data)

        rsa_keys = RSA.import_key(read_rsa_keys())
        signature = read_signature()

        verifier = pkcs1_15.new(rsa_keys)  # объект подписи

        try:
            verifier.verify(hashed_data, signature)
        except (ValueError, TypeError):
            return False
        else:
            return True

    @classmethod
    def _hash_data(cls, data: bytes) -> SHA3_256_Hash:
        return SHA3_256.new(data)

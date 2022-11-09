PUB_KEY_FILENAME = ".signature/public_key.cer"


def read_rsa_keys(public_key_filename: str = PUB_KEY_FILENAME) -> bytes:
    with open(public_key_filename, "rb") as public_key_file:
        return public_key_file.read()


def write_rsa_keys(key: bytes, public_key_filename: str = PUB_KEY_FILENAME) -> None:
    with open(public_key_filename, "wb") as public_key_file:
        public_key_file.write(key)


SIG_FILENAME = ".signature/signature.sig"


def write_signature(signature: bytes, signature_filename: str = SIG_FILENAME) -> None:
    with open(signature_filename, "wb") as sign_file:
        sign_file.write(signature)


def read_signature(signature_filename: str = SIG_FILENAME) -> bytes:
    with open(signature_filename, "rb") as sign_file:
        return sign_file.read()

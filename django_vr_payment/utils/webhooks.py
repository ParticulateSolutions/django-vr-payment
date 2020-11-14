import os
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def decrypt_webhook(
    config_key: str, Initialization_vector: str, auth_tag: str, http_body: str
):

    # Convert data to process
    key = binascii.unhexlify(config_key)
    iv = binascii.unhexlify(Initialization_vector)
    auth_tag = binascii.unhexlify(auth_tag)
    cipher_text = binascii.unhexlify(http_body)

    # Prepare decryption
    decryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv, auth_tag), backend=default_backend()
    ).decryptor()

    # Decrypt
    result = decryptor.update(cipher_text) + decryptor.finalize()
    return result

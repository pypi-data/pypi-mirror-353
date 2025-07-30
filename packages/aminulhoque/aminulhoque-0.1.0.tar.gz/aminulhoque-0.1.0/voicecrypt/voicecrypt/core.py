import base64
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def _derive_key(password: str, salt: bytes, length: int = 32) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def encrypt_audio(input_audio_path: str, output_text_path: str, password: str):
    # Read audio file as bytes
    with open(input_audio_path, 'rb') as f:
        data = f.read()
    # Generate salt and IV
    salt = os.urandom(16)
    iv = os.urandom(16)
    key = _derive_key(password, salt)
    # Pad data
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    # Combine salt + iv + ciphertext
    combined = salt + iv + ct
    # Encode as base64
    b64 = base64.b64encode(combined)
    # Write to text file
    with open(output_text_path, 'wb') as f:
        f.write(b64)

def decrypt_audio(input_text_path: str, output_audio_path: str, password: str):
    # Read base64 text file
    with open(input_text_path, 'rb') as f:
        b64 = f.read()
    combined = base64.b64decode(b64)
    salt = combined[:16]
    iv = combined[16:32]
    ct = combined[32:]
    key = _derive_key(password, salt)
    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ct) + decryptor.finalize()
    # Unpad
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    # Write to audio file
    with open(output_audio_path, 'wb') as f:
        f.write(data) 
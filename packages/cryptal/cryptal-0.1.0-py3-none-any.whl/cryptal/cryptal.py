import os
import base64
import hashlib

BLOCK_SIZE = 16

def pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def derive_key(password: str, salt: bytes, iterations=100_000) -> bytes:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def encrypt(password: str, testo: str) -> str:
    data = testo.encode('utf-8')

    salt = os.urandom(16)
    iv = os.urandom(16)
    key = derive_key(password, salt)

    padded = pad(data)
    encrypted = xor_encrypt(padded, key)

    to_encode = salt + iv + encrypted
    return base64.b64encode(to_encode).decode('utf-8')

def decrypt(password: str, encrypted_b64: str) -> str:
    encrypted_data = base64.b64decode(encrypted_b64.encode('utf-8'))

    salt = encrypted_data[:16]
    iv = encrypted_data[16:32]
    encrypted = encrypted_data[32:]

    key = derive_key(password, salt)
    decrypted_padded = xor_encrypt(encrypted, key)

    decrypted = unpad(decrypted_padded)
    return decrypted.decode('utf-8')

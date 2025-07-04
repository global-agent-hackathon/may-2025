from cryptography.fernet import Fernet, InvalidToken
from typing import Optional
from core.config import settings

try:
    ENCRYPTION_KEY_BYTES = settings.ENCRYPTION_KEY.encode('utf-8')
    fernet_cipher = Fernet(ENCRYPTION_KEY_BYTES)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize Fernet cipher. Ensure ENCRYPTION_KEY is a valid Fernet key. Error: {e}")
    fernet_cipher = None


def encrypt_value(value: Optional[str]) -> Optional[str]:
    """Encrypts a string value. Returns None if input is None or encryption fails."""
    if value is None:
        return None
    if fernet_cipher is None:
        print("Warning: Encryption skipped because cipher is not initialized.")
        return value # Or raise an error

    try:
        return fernet_cipher.encrypt(value.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return None


def decrypt_value(encrypted_value: Optional[str]) -> Optional[str]:
    if encrypted_value is None:
        return None
    if fernet_cipher is None:
        print("Warning: Decryption skipped because cipher is not initialized.")
        return encrypted_value

    try:
        return fernet_cipher.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        print(f"Decryption warning: Invalid token for value. Assuming it might be plaintext or corrupted.")
        return encrypted_value
    except Exception as e:
        print(f"Decryption error for value: {e}")
        return None
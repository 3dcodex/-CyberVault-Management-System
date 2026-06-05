"""
Symmetric encryption for vault credentials using Fernet (AES-128-CBC + HMAC-SHA256).

Key management notes for production:
  - Rotate CREDENTIAL_ENCRYPTION_KEY to re-encrypt existing rows, never delete old keys.
  - Store the key in an environment variable or a secrets manager (AWS Secrets Manager,
    HashiCorp Vault, etc.) — never hard-code it in source control.
  - Fernet tokens are authenticated; tampering raises cryptography.fernet.InvalidToken.
"""

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

# Prefix lets us tell encrypted blobs from legacy plaintext rows without
# attempting a decrypt (which would raise an exception on plaintext data).
_PREFIX = 'CVENC:'


def _get_fernet() -> Fernet:
    key = getattr(settings, 'CREDENTIAL_ENCRYPTION_KEY', None)
    if not key:
        raise RuntimeError(
            'CREDENTIAL_ENCRYPTION_KEY is not set in settings. '
            'Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_value(plaintext: str) -> str:
    """Return an authenticated encrypted string prefixed with CVENC:"""
    if not plaintext:
        return plaintext
    if plaintext.startswith(_PREFIX):
        return plaintext  # already encrypted, idempotent
    token = _get_fernet().encrypt(plaintext.encode()).decode()
    return _PREFIX + token


def decrypt_value(value: str) -> str:
    """
    Decrypt a CVENC:-prefixed string.
    Returns the value unchanged if it has no prefix (legacy plaintext row).
    """
    if not value or not value.startswith(_PREFIX):
        return value  # legacy plaintext — readable but will be re-encrypted on next save
    try:
        return _get_fernet().decrypt(value[len(_PREFIX):].encode()).decode()
    except InvalidToken:
        return ''  # corrupted or wrong key — never leak the raw blob

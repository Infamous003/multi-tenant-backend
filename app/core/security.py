import secrets
import hashlib
import hmac


def generate_api_key() -> str:
    """
    Generate a secure random 32 byte URL-safe API key.

    Returns:
        str: The generated API key.
    """
    api_key = secrets.token_urlsafe(32)
    return api_key


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using SHA256.

    Args:
        api_key (str): The plaintext API key.

    Returns:
        str: Hex digest of the hashed API key.    
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """
    Verify if the provided API key matches the stored hash.

    Agrs:
        provided_key (str): The API key received from a client
        stored_hash (str): The SHA-256 hash of the original API key stored in DB
    
    Returns:
        bool: True if the provided key matches the stored hash, False otherwise.
    """
    provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    return hmac.compare_digest(provided_hash, stored_hash)
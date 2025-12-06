# decrypt_seed.py

import base64
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes, serialization

def load_private_key(pem_path: str) -> rsa.RSAPrivateKey:
    """
    Load RSA private key from PEM file
    """
    with open(pem_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key

def decrypt_seed(encrypted_seed_b64: str, private_key: rsa.RSAPrivateKey) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256
    Returns the decrypted 64-character hex string
    """
    # 1) Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    # 2) Decrypt with OAEP SHA-256
    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 3) Decode to UTF-8
    hex_seed = decrypted_bytes.decode("utf-8").strip().lower()

    # 4) Validate 64-character hex string
    if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
        raise ValueError("Decrypted seed is invalid. Must be 64-character hexadecimal string.")

    return hex_seed

# -------------------------
# ======= MAIN ============
# -------------------------
if __name__ == "__main__":
    # Paths
    PRIVATE_KEY_PATH = "student_private.pem"       # Your private key from Step 2
    ENCRYPTED_SEED_PATH = "encrypted_seed.txt"     # From Step 4
    SEED_OUTPUT_PATH = "data/seed.txt"             # Save decrypted seed inside project folder

    # Ensure "data" folder exists in project
    os.makedirs("data", exist_ok=True)

    # Load private key
    private_key = load_private_key(PRIVATE_KEY_PATH)

    # Read encrypted seed
    with open(ENCRYPTED_SEED_PATH, "r") as f:
        encrypted_seed_b64 = f.read().strip()

    # Decrypt seed
    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)
    print("Decrypted seed:", hex_seed)

    # Save to data/seed.txt
    with open(SEED_OUTPUT_PATH, "w") as f:
        f.write(hex_seed)

    print(f"Seed saved to {SEED_OUTPUT_PATH}")

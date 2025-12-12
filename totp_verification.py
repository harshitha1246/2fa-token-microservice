# totp_verify.py
import base64
import pyotp

def verify_totp_code(hex_seed: str, code: str) -> bool:
    """
    Verify a TOTP code against the 64-char hex seed.
    Returns True if valid, False otherwise.
    """
    if len(hex_seed) != 64:
        raise ValueError("Hex seed must be 64 characters long.")

    # Convert hex → bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # Convert bytes → Base32 STRING (not bytes)
    seed_base32 = base64.b32encode(seed_bytes).decode('utf-8')

    # Create TOTP object
    totp = pyotp.TOTP(seed_base32, digits=6, interval=30)

    # Verify code
    return totp.verify(code)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    # Read hex seed from file
    with open("data/seed.txt", "r") as f:
        hex_seed = f.read().strip()

    # Input TOTP code to verify
    user_code = input("Enter TOTP code to verify: ").strip()

    if verify_totp_code(hex_seed, user_code):
        print("TOTP code is valid ")
    else:
        print("TOTP code is invalid ")

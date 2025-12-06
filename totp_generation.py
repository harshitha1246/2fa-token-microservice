
# totp_generate.py
import base64
import pyotp

def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from 64-character hex seed
    """
    if len(hex_seed) != 64:
        raise ValueError("Hex seed must be 64 characters long.")

    # Convert hex to bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # Convert bytes to base32
    seed_base32 = base64.b32encode(seed_bytes)

    # Generate TOTP
    totp = pyotp.TOTP(seed_base32, digits=6, interval=30)  # SHA-1 default
    code = totp.now()

    return code

# -------------------------
# ======= MAIN ============
# -------------------------
if __name__ == "__main__":
    # Read hex seed from file
    with open("data/seed.txt", "r") as f:
        hex_seed = f.read().strip()

    totp_code = generate_totp_code(hex_seed)
    print("Current TOTP code:", totp_code)

#!/usr/bin/env python3
import base64
import pyotp
from datetime import datetime
from pathlib import Path

# Path to seed file
SEED_FILE = Path("/data/seed.txt")

def generate_totp_from_seed(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    seed_base32 = base64.b32encode(seed_bytes)
    totp = pyotp.TOTP(seed_base32, digits=6, interval=30)
    return totp.now()

def main():
    try:
        hex_seed = SEED_FILE.read_text().strip()
    except FileNotFoundError:
        print("Seed file not found.")
        return

    # Generate TOTP code
    code = generate_totp_from_seed(hex_seed)

    # Get UTC timestamp in format YYYY-MM-DD HH:MM:SS
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Print formatted line
    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()

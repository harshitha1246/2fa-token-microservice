# app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import base64
import os
import time

# Crypto imports
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import pyotp

# ===== PATHS =====
PRIVATE_KEY_PATH = "student_private.pem"
SEED_FILE = Path("data/seed.txt")

app = FastAPI()

# ========================
# MODELS
# ========================
class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# ========================
# HELPERS
# ========================
def load_private_key(path=PRIVATE_KEY_PATH):
    try:
        with open(path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load private key")

def decrypt_seed(encrypted_b64: str) -> str:
    # Base64 decode
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
    except:
        raise HTTPException(status_code=500, detail="Base64 decode failed")

    private_key = load_private_key()

    try:
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")

    hex_seed = decrypted.decode().strip().lower()

    # Validate hex seed
    if len(hex_seed) != 64 or any(c not in "0123456789abcdef" for c in hex_seed):
        raise HTTPException(status_code=500, detail="Invalid decrypted seed")

    return hex_seed

def generate_totp(hex_seed: str):
    seed_bytes = bytes.fromhex(hex_seed)
    seed_base32 = base64.b32encode(seed_bytes).decode()   # ✅ decode bytes to string
    totp = pyotp.TOTP(seed_base32, digits=6, interval=30)
    code = totp.now()
    remaining = 30 - (int(time.time()) % 30)             # ✅ integer
    return code, remaining

def verify_totp(hex_seed: str, user_code: str):
    seed_bytes = bytes.fromhex(hex_seed)
    seed_base32 = base64.b32encode(seed_bytes).decode()  # decode to string
    totp = pyotp.TOTP(seed_base32, digits=6, interval=30)
    return totp.verify(user_code, valid_window=1)        # ±1 window

# ========================
# ENDPOINTS
# ========================

# 1️⃣ POST /decrypt-seed
@app.post("/decrypt-seed")
def decrypt_seed_api(req: DecryptSeedRequest):
    hex_seed = decrypt_seed(req.encrypted_seed)

    # Create folder if not exists
    SEED_FILE.parent.mkdir(exist_ok=True)

    # Save seed
    SEED_FILE.write_text(hex_seed)

    return {"status": "ok"}

# 2️⃣ GET /generate-2fa
@app.get("/generate-2fa")
def generate_2fa_api():
    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text().strip()
    code, valid = generate_totp(hex_seed)

    return {"code": code, "valid_for": valid}

# 3️⃣ POST /verify-2fa
@app.post("/verify-2fa")
def verify_api(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text().strip()
    is_valid = verify_totp(hex_seed, req.code)

    return {"valid": is_valid}

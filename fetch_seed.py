import json
import requests
from typing import Optional

def read_public_key_pem(pem_path: str) -> str:
    with open(pem_path, "r", encoding="utf-8") as f:
        pem = f.read().strip()
    if not (pem.startswith("-----BEGIN") and "-----END" in pem):
        raise ValueError("Public key PEM file doesn't contain expected BEGIN/END markers.")
    return pem

def request_seed(student_id: str, github_repo_url: str, api_url: str,
                 public_key_pem_path: str = "student_public.pem",
                 timeout_seconds: int = 10) -> Optional[str]:
    pubkey_pem = read_public_key_pem(public_key_pem_path)
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": pubkey_pem
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout_seconds)
    except requests.RequestException as e:
        raise RuntimeError(f"Network/timeout error while calling Instructor API: {e}")
    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError(f"Non-JSON response from API (status {resp.status_code}): {resp.text}")
    if resp.status_code != 200 or data.get("status") != "success":
        raise RuntimeError(f"API error: status_code={resp.status_code}, body={json.dumps(data)}")
    encrypted_seed = data.get("encrypted_seed") or data.get("encrypted seed") or data.get("encryptedSeed")
    if not encrypted_seed:
        raise RuntimeError(f"API success but missing encrypted_seed field in response: {json.dumps(data)}")
    with open("encrypted_seed.txt", "w", encoding="utf-8") as f:
        f.write(encrypted_seed)
    print("Encrypted seed saved to encrypted_seed.txt (do NOT commit this file).")
    return encrypted_seed

if __name__ == "__main__":
    API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
    STUDENT_ID = "23MH1A1246"
    GITHUB_REPO_URL = "https://github.com/harshitha1246/2fa-token-microservice.git"
    seed = request_seed(STUDENT_ID, GITHUB_REPO_URL, API_URL, public_key_pem_path="student_public.pem")
    print("Encrypted seed (truncated):", seed[:80] + "..." if seed else "None")

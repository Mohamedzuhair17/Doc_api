import requests
import base64
import json
import os

# --- CONFIGURATION (Match your .env) ---
API_URL = "http://localhost:8000"
API_KEY = "hackathon_secret_123"  # Change this if you modified it in .env
FILE_PATH = "sample_invoice.pdf"  # Make sure this file exists locally for testing

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def infer_file_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if ext == "pdf":
        return "pdf"
    if ext == "docx":
        return "docx"
    return "image"


def test_analyze():
    # 1. Encode file to Base64
    try:
        with open(FILE_PATH, "rb") as f:
            encoded_bytes = base64.b64encode(f.read())
            b64_string = encoded_bytes.decode("utf-8")
    except FileNotFoundError:
        print(f"Error: {FILE_PATH} not found. Please place a small document in this folder.")
        return

    # 2. Dispatch Task
    payload = {
        "fileName": FILE_PATH,
        "fileType": infer_file_type(FILE_PATH),
        "fileBase64": b64_string
    }
    
    print(f"[*] Sending {FILE_PATH} to API for analysis...")
    response = requests.post(f"{API_URL}/api/document-analyze", json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"[!] Request failed ({response.status_code}): {response.text}")
        return

    print("\n[SUCCESS] Document Analysis Result:")
    print(json.dumps(response.json(), indent=4))

if __name__ == "__main__":
    test_analyze()

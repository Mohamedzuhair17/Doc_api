import requests
import base64
import json
import time

# --- CONFIGURATION (Match your .env) ---
API_URL = "http://localhost:8000"
API_KEY = "hackathon_secret_123"  # Change this if you modified it in .env
FILE_PATH = "sample_invoice.pdf" # Make sure this file exists locally for testing

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

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
        "fileBase64": b64_string
    }
    
    print(f"[*] Sending {FILE_PATH} to API for analysis...")
    response = requests.post(f"{API_URL}/api/document-analyze", json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"[!] Error Dispatching Task: {response.text}")
        return

    task_id = response.json().get("task_id")
    print(f"[+] Task Created! ID: {task_id}")

    # 3. Poll for Results
    print(f"[*] Polling for results...")
    max_retries = 12 # 60 seconds total
    for i in range(max_retries):
        result_response = requests.get(f"{API_URL}/api/results/{task_id}", headers=headers)
        result_data = result_response.json()
        
        status = result_data.get("status")
        print(f"[*] Attempt {i+1}: Status = {status}")
        
        if status == "success":
            print("\n[SUCCESS] Document Analysis Result:")
            print(json.dumps(result_data.get("data"), indent=4))
            return
        elif status == "Failed":
            print(f"\n[FAILED] Analysis failed: {result_data.get('error')}")
            return
        
        time.sleep(5)

    print("[!] Polling timed out (document might be taking too long to process).")

if __name__ == "__main__":
    test_analyze()

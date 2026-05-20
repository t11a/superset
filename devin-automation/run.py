import os
import sys
import time
import requests

# 必要な環境変数の取得
DEVIN_API_KEY = os.environ.get("DEVIN_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
ISSUE_URL = os.environ.get("ISSUE_URL")
DEVIN_ORG_ID = os.environ.get("DEVIN_ORG_ID")

DEVIN_API_BASE_URL = "https://api.devin.ai/v3"

def create_session(prompt):
    headers = {
        "Authorization": f"Bearer {DEVIN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt
    }

    print(f"Creating Devin session for issue: {ISSUE_URL}")
    try:
        response = requests.post(f"{DEVIN_API_BASE_URL}/organizations/{DEVIN_ORG_ID}/sessions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        session_id = data.get('session_id')
        session_url = data.get('url')
        print(f"✅ Successfully created session!")
        print(f"🔗 Session ID: {session_id}")
        print(f"🔗 Session URL: {session_url}")
        return session_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create session: {e}")
        if e.response is not None:
            print(f"Response details: {e.response.text}")
        sys.exit(1)

def monitor_session(session_id):
    headers = {
        "Authorization": f"Bearer {DEVIN_API_KEY}",
    }
    print(f"\nMonitoring session {session_id} for completion...")
    
    while True:
        try:
            response = requests.get(f"{DEVIN_API_BASE_URL}/organizations/{DEVIN_ORG_ID}/sessions/{session_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            status = data.get("status_enum") or data.get("status", "unknown")
            
            print(f"[Status Update] Session {session_id} is currently: {status}")
            
            # blocked, stopped, or error states indicate we should stop polling
            if status in ["stopped", "blocked", "failed", "completed"]:
                print(f"🏁 Session finished monitoring with status: {status}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error checking status: {e}")
            
        # 1分ごとにステータスをチェック
        time.sleep(60)

def main():
    if not DEVIN_API_KEY:
        print("❌ Error: DEVIN_API_KEY environment variable is not set.")
        sys.exit(1)
        
    if not ISSUE_URL:
        print("❌ Error: ISSUE_URL environment variable is not set.")
        sys.exit(1)
        
    if not DEVIN_ORG_ID:
        print("❌ Error: DEVIN_ORG_ID environment variable is not set. You can find it in your Devin account settings.")
        sys.exit(1)
        
    prompt = f"""
You are tasked with fixing a reported issue in the {GITHUB_REPOSITORY} repository.

The issue details can be found at this URL: {ISSUE_URL}

Please follow these instructions exactly:
1. Clone the repository at https://github.com/{GITHUB_REPOSITORY}.git
2. Read the details of the issue carefully.
3. Fix the issue in the code.
4. Run tests or validations if applicable.
5. Create a new branch, commit your changes, and create a Pull Request against the repository. 
6. Ensure the PR title is descriptive and the description mentions 'Fixes {ISSUE_URL}'.
7. Stop the session once the PR is successfully created.
"""
    
    session_id = create_session(prompt)
    monitor_session(session_id)

if __name__ == "__main__":
    main()

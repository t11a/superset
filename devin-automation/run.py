import os
import sys
import requests

# 必要な環境変数の取得
DEVIN_API_KEY = os.environ.get("DEVIN_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
ISSUE_URL = os.environ.get("ISSUE_URL")
DEVIN_ORG_ID = os.environ.get("DEVIN_ORG_ID")

DEVIN_API_BASE_URL = "https://api.devin.ai/v3"

def write_step_summary(text):
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        try:
            with open(summary_file, "a") as f:
                f.write(text + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write to GITHUB_STEP_SUMMARY: {e}")

def post_github_comment(comment_body):
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY or not ISSUE_URL:
        print("Skipping GitHub comment (missing credentials/info).")
        return
        
    try:
        issue_number = ISSUE_URL.split("/")[-1]
    except Exception:
        print("Could not parse issue number from ISSUE_URL.")
        return

    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"body": comment_body}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Successfully posted comment to GitHub issue.")
    except Exception as e:
        print(f"⚠️ Failed to post comment to GitHub issue: {e}")

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
        return session_id, session_url
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create session: {e}")
        if e.response is not None:
            print(f"Response details: {e.response.text}")
        sys.exit(1)

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
1. Clone the repository at https://github.com/{GITHUB_REPOSITORY}.git using --depth 1 to save time
2. Read the details of the issue carefully.
3. [IMPORTANT] Before you start making changes, post a comment on the original issue ({ISSUE_URL}) explaining your planned approach, using the provided GITHUB_TOKEN in your environment.
4. Fix the issue in the code.
5. Run tests or validations if applicable.
6. Create a new branch, commit your changes, and create a Pull Request against the repository. 
7. Ensure the PR title is descriptive and the description mentions 'Fixes {ISSUE_URL}'.
8. [IMPORTANT] After the PR is successfully created (or if you encounter an unrecoverable failure), post a detailed comment on the original issue ({ISSUE_URL}) summarizing:
   - The exact changes you made (with a brief technical explanation)
   - The test/validation results
   - A link to the created Pull Request (if successful) or error details (if failed)
9. Stop the session once the PR is successfully created or the failure is reported.

Note: You can use the `gh` CLI (which is pre-authenticated via the GITHUB_TOKEN in your environment) or standard HTTP requests to GitHub's REST API to post comments to the issue.
"""
    
    session_id, session_url = create_session(prompt)
    
    start_msg = f"🚀 **Devin** has started investigating this issue.\n\n🔗 [View Devin Session]({session_url})"
    post_github_comment(start_msg)
    
    print("⚡ Session successfully initiated. Skipping active session monitoring (Async Mode).")
    print(f"🔗 Devin will self-report its progress directly to the issue: {ISSUE_URL}")
    write_step_summary(
        f"### 🚀 Devin Session Started (Async Mode)\n"
        f"- **Issue:** {ISSUE_URL}\n"
        f"- **Session Link:** [View Devin Session]({session_url})\n\n"
        f"> ⚡ **Note:** This workflow finished immediately in async mode. "
        f"Devin is working in the background and will report progress directly on the GitHub Issue."
    )

if __name__ == "__main__":
    main()

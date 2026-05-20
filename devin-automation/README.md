# Devin Automation

This directory contains the automation scripts to trigger a Devin session directly from a GitHub Issue creation event.

## Architecture

This solution leverages **GitHub Actions** and **Docker** to provide a seamless, event-driven remediation pipeline:

1. **Trigger**: A new issue is opened in the repository (e.g., CodeQL vulnerability alert or a bug report).
2. **GitHub Actions Workflow**: The `.github/workflows/devin-trigger.yml` workflow listens to the `issues` event and spins up an Ubuntu runner.
3. **Docker Execution**: The workflow builds the Docker image defined in `devin-automation/Dockerfile` and injects necessary context (`ISSUE_URL`, repository details) and secrets (`DEVIN_API_KEY`, `DEVIN_ORG_ID`).
4. **Devin Session Creation & Observability**: `run.py` invokes the Devin API (v3) to create a new session, passing a prompt that instructs Devin to fix the issue and open a Pull Request. The script then monitors the session's status (running, completed, failed) and streams the status back to the GitHub Actions logs, ensuring the engineering team has full visibility into the autonomous remediation process.

## How to Run

### 1. Prerequisites
You must configure the following Repository Secrets in your GitHub repository (`Settings > Secrets and variables > Actions`):
- `DEVIN_API_KEY`: Your Devin API token.
- `DEVIN_ORG_ID`: Your Devin Organization ID.

### 2. Triggering the Automation
Simply create a new Issue in this repository. Ensure the issue description contains sufficient detail for Devin to understand the problem.
Upon creation, navigate to the **Actions** tab in GitHub to watch the `Trigger Devin Automation` workflow build the container, trigger Devin, and monitor the progress.

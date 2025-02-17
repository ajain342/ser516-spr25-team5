import os
import sys
import requests
import json
import re
from datetime import datetime, timedelta

def get_repo_from_url(repo_url):
    """Extracts 'owner/repo' from a GitHub URL."""
    match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    else:
        print("Invalid GitHub repository URL.")
        sys.exit(1)

def fetch_issues(repo, token):
    """Fetches issues from a given GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100"
    headers = {"Authorization": f"token {token}"} if token else {}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching issues: {response.json()} ")
        sys.exit(1)
    return response.json()

def calculate_mttr(issues):
    """Calculates Mean Time to Resolve (MTTR) for issues."""
    resolve_times = []
    
    for issue in issues:
        created_at = issue.get("created_at")
        closed_at = issue.get("closed_at")
        
        if created_at and closed_at:
            created_time = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
            closed_time = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ")
            resolve_times.append((closed_time - created_time).total_seconds())
    
    mttr_seconds = sum(resolve_times) / len(resolve_times) if resolve_times else 0
    mttr_timedelta = timedelta(seconds=mttr_seconds)
    
    days = mttr_timedelta.days
    hours, remainder = divmod(mttr_timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days}d:{hours}h:{minutes}m:{seconds}s"

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <GitHub Repo URL>")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    repo = get_repo_from_url(repo_url)
    github_token = os.getenv("GH_TOKEN")  # Optional GitHub token
    
    #print(f"Fetching issues from {repo}...")
    issues = fetch_issues(repo, github_token)
    
    #print("Calculating MTTR (Mean Time to Resolve)...")
    mttr = calculate_mttr(issues)
    
    print(f"MTTR (Mean Time to Resolve): {mttr}")

if __name__ == "__main__":
    main()

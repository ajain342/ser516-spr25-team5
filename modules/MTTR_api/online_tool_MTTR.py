# This tool is inspired from github repo: https://github.com/github/issue-metrics
# Later the code was modified for accepting github repo link as an input.
# Also modified output to later generate visual representation.

import argparse
import requests
from datetime import datetime
import numpy as np
class IssueWithMetrics:
    """A class to represent a GitHub issue with metrics."""

    def __init__(self, number, title, html_url, author, created_at, closed_at):
        self.number = number
        self.title = title
        self.html_url = html_url
        self.author = author
        self.created_at = created_at
        self.closed_at = closed_at
        self.time_to_close = (
            (closed_at - created_at).total_seconds() if closed_at and created_at else None
        )

def fetch_issues(repo_url, token=None):
    """
    Fetches closed issues from a GitHub repository.
    
    Args:
        repo_url (str): GitHub repository URL.
        token (str): GitHub personal access token (optional for higher rate limits).

    Returns:
        List[IssueWithMetrics]: List of issues with time to resolve.
    """
    repo_path = repo_url.replace("https://github.com/", "").strip("/")
    api_url = f"https://api.github.com/repos/{repo_path}/issues"
    headers = {"Authorization": f"token {token}"} if token else {}

    issues_with_metrics = []
    page = 1

    while True:
        response = requests.get(api_url, headers=headers, params={"state": "closed", "per_page": 100, "page": page})
        if response.status_code != 200:
            error_msg = response.json().get('message', 'Unknown error')
            if error_msg == "Not Found":
                raise Exception("Unable to clone repository. Please ensure the repository is public or valid.")
            else:
                raise Exception(f"Error fetching issues: {error_msg}")

        issues = response.json()
        if not issues:
            break  # No more issues

        for issue in issues:
            if "pull_request" in issue:  # Ignore PRs
                continue
            
            created_at = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            closed_at = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ") if issue["closed_at"] else None
            
            issues_with_metrics.append(
                IssueWithMetrics(
                    number=issue["number"],
                    title=issue["title"],
                    html_url=issue["html_url"],
                    author=issue["user"]["login"],
                    created_at=created_at,
                    closed_at=closed_at,
                )
            )
        
        page += 1  # Go to the next page of results

    return issues_with_metrics

def calculate_mttr(issues_with_metrics):
    """
    Calculate Mean Time to Repair (MTTR) in hours.

    Args:
        issues_with_metrics (List[IssueWithMetrics]): A list of issues with their metrics.

    Returns:
        float: Mean Time to Repair in hours.
    """
    repair_times = []

    for issue in issues_with_metrics:
        if issue.time_to_close is not None:
            # print(f"Issue #{issue.number}:")
            # print(f"  Created: {issue.created_at}")
            # print(f"  Closed:  {issue.closed_at}")
            # print(f"  Time Taken: {issue.time_to_close / 3600:.2f} hours\n")
            repair_times.append(issue.time_to_close)

    if not repair_times:
        return None  # No valid issues

    return np.mean(repair_times) / 3600  # Convert seconds to hours

def fetch_mttr_online(repo_url):
    issues = fetch_issues(repo_url, None)

    if not issues:
        return {"mttr": None, "error": "No closed issues found"}

    mttr = calculate_mttr(issues)
    return {"mttr": mttr, "error": None} if mttr else {"mttr": None, "error": "No issues with valid timestamps"}


def main():
    parser = argparse.ArgumentParser(description="Calculate Mean Time to Repair (MTTR) in a GitHub repo.")
    parser.add_argument("repo_url", help="GitHub repository URL (e.g., https://github.com/user/repo)")
    parser.add_argument("--token", help="GitHub personal access token (optional for higher API rate limits)")

    args = parser.parse_args()
    
    print(f"Fetching issues from {args.repo_url}...\n")
    issues = fetch_issues(args.repo_url, args.token)

    if not issues:
        print("No closed issues found.")
        return

    mttr = calculate_mttr(issues)

    if mttr is not None:
        print(f"Mean Time to Resolve (MTTR): {mttr:.2f} hours")
    else:
        print("\nNo issues found with valid closure times.\n")

if __name__ == "__main__":
    main()

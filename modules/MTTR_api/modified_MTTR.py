import sys
import requests
from datetime import datetime

def fetch_closed_issues(repo_url):
    """
    Fetches all closed issues using GitHub API.
    Raises Exception on any non-200 response.
    """
    api_url = repo_url.replace("github.com", "api.github.com/repos") + "/issues"
    issues = []
    page = 1

    while True:
        params = {"state": "closed", "per_page": 100, "page": page}
        response = requests.get(api_url, params=params)

        if response.status_code != 200:
            # Provide more specific error messages for common cases
            if response.status_code in (400, 403, 404):
                raise Exception("The repository may be private or invalid.")
            error_msg = response.json().get('message', 'Unknown error')
            raise Exception(f"GitHub API error: {error_msg} (status {response.status_code})")

        batch = response.json()
        if not batch:
            break  # No more issues left

        # Filter out pull requests (PRs)
        filtered_issues = [issue for issue in batch if "pull_request" not in issue]
        issues.extend(filtered_issues)

        page += 1  # Go to next page

    return issues

def calculate_mttr(issues):
    """
    Calculates Mean Time to Repair (MTTR) in hours,
    prints some details for each issue, and returns the final MTTR.
    """
    repair_times = []

    for issue in issues:
        if "created_at" in issue and "closed_at" in issue and issue["closed_at"]:
            created_time = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            closed_time = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
            time_taken = (closed_time - created_time).total_seconds()

            print(f"Issue #{issue['number']}:")
            print(f"  Created: {created_time}")
            print(f"  Closed:  {closed_time}")
            print(f"  Time Taken: {time_taken / 3600:.2f} hours\n")

            repair_times.append(time_taken)

    if not repair_times:
        return None
    
    # Mean time in hours
    return sum(repair_times)/len(repair_times)/3600

def fetch_mttr_gitapi(repo_url):
    """
    Attempts to fetch closed issues from GitHub via the standard REST API,
    calculate MTTR, and return a dict with {"mttr": ..., "error": ...}.
    """
    try:
        repo_url = repo_url.rstrip("/")
        issues = fetch_closed_issues(repo_url)

        if not issues:
            return {
                "mttr": None,
                "error": "No closed issues found"
            }

        mttr = calculate_mttr(issues)
        if mttr is None:
            return {
                "mttr": None,
                "error": "No issues with valid timestamps"
            }
        return {
            "mttr": mttr,
            "error": None
        }

    except Exception as e:
        return {
            "mttr": None,
            "error": f"Calculation failed: {str(e)}"
        }

if __name__ == "__main__":
    # Standalone usage
    if len(sys.argv) != 2:
        print("Usage: python modified_MTTR.py <GitHub_Repo_URL>")
        sys.exit(1)

    repo_url = sys.argv[1].rstrip("/")
    # Attempt to get closed issues and calculate
    result = fetch_mttr_gitapi(repo_url)
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(f"MTTR: {result['mttr']:.2f} hours")

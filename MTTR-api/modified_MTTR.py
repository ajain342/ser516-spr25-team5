import sys
import requests
from datetime import datetime

def fetch_closed_issues(repo_url):
    """Fetches all closed issues using GitHub API."""
    api_url = repo_url.replace("github.com", "api.github.com/repos") + "/issues"
    params = {"state": "closed", "per_page": 100} 
    response = requests.get(api_url, params=params)

    if response.status_code != 200:
        error_msg = response.json().get('message', 'Unknown error')
        raise Exception(f"GitHub API error: {error_msg}")

    return response.json()

def calculate_mttr(issues):
    """Calculates Mean Time to Repair (MTTR) and prints details for each issue."""
    repair_times = []

    for issue in issues:
        if "created_at" in issue and "closed_at" in issue:
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
    
    return sum(repair_times)/len(repair_times)/3600 if repair_times else None

def fetch_mttr_gitapi(repo_url):
    try:
        repo_url = repo_url.rstrip("/")
        issues = fetch_closed_issues(repo_url)
        
        if not issues:
            return {"mttr": None, "error": "No closed issues found"}
        
        mttr = calculate_mttr(issues)
        return {"mttr": mttr, "error": None} if mttr else {"mttr": None, "error": "No issues with valid timestamps"}
    
    except Exception as e:
        return {"mttr": None, "error": f"Calculation failed: {str(e)}"}
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mttr_calculator.py <GitHub_Repo_URL>")
        sys.exit(1)

    repo_url = sys.argv[1].rstrip("/") 
    issues = fetch_closed_issues(repo_url)

    issue_count = len(issues)
    mttr = calculate_mttr(issues)

    if mttr is not None:
        print(f"\nTotal Closed Issues: {issue_count}")
        print(f"Mean Time to Repair (MTTR): {mttr:.2f} hours")
    else:
        print(f"No closed issues found for {repo_url}.")

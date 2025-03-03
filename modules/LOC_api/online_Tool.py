import json
import requests
import argparse
from urllib.parse import urlparse

def get_github_repo():
    parser = argparse.ArgumentParser(description="Analyze LOC using CodeTabs online tool.")
    parser.add_argument("repo_url", type=str, help="GitHub repository URL")
    args = parser.parse_args()
    parsed_url = urlparse(args.repo_url)
    repo_path = parsed_url.path.strip("/")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    return repo_path

def fetch_loc_codetabs(repo_path):
    try:
        api_url = f"https://api.codetabs.com/v1/loc/?github={repo_path}"
        print(f"Attempting to call: {api_url}")
        response = requests.get(api_url)
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            # If 403 (forbidden) or 404 (not found), indicate the repo may be private or does not exist.
            if response.status_code in (400, 403, 404):
                raise Exception("Failed to fetch LOC data: Repository may be private or does not exist.")
            else:
                raise Exception(f"Error fetching LOC data from CodeTabs (status {response.status_code})")
        loc_data = response.json()
        if not isinstance(loc_data, list):
            raise Exception("Unexpected response format from CodeTabs")
        total_lines = None
        for item in loc_data:
            if item.get('language') == "Total":
                total_lines = item.get('linesOfCode')
                break
        if total_lines is None:
            raise Exception("Could not find 'Total' linesOfCode in CodeTabs response")
        return {"total_lines": total_lines}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching LOC data: {e}")

def main():
    repo_path = get_github_repo()
    try:
        resultOnline = fetch_loc_codetabs(repo_path)
        print(f"Total LOC: {resultOnline['total_lines']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

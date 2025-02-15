import json
import requests
import argparse
from urllib.parse import urlparse

def get_github_repo():
    parser = argparse.ArgumentParser(description="Analyze LOC using CodeTabs online tool.")
    parser.add_argument("repo_url", type=str, help="GitHub repository URL")
    args = parser.parse_args()
    parsed_url = urlparse(args.repo_url)
    repo_path = parsed_url.path.strip("/")  # Extracts username/repo from URL
    # Remove ".git" if it's present in the repository path
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    return repo_path

def fetch_loc_codetabs(repo_path):
    try:
        api_url = f"https://api.codetabs.com/v1/loc/?github={repo_path}"
        print(f"Attempting to call: {api_url}")
        response = requests.get(api_url)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        loc_data = response.json()

        total_lines = next((item['linesOfCode'] for item in loc_data if item['language'] == "Total"), None)

        return {"total_lines": total_lines, "error": None}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching LOC data: {e}")
        exit(1)

def main():
    repo_path = get_github_repo()    
    resultOnline = fetch_loc_codetabs(repo_path)
    
    if resultOnline["error"]:
        print(f"Error: {resultOnline['error']}")
        exit(1)
    print(f"Total LOC: {resultOnline['total_lines']}")

if __name__ == "__main__":
    main()

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

def fetch_loc_from_codetabs(repo_path):
    api_url = f"https://api.codetabs.com/v1/loc/?github={repo_path}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching LOC data: {e}")
        exit(1)

def main():
    repo_path = get_github_repo()
    loc_data = fetch_loc_from_codetabs(repo_path)
    
    # Extract the linesOfCode for "Total"
    total_lines_of_code = next((item['linesOfCode'] for item in loc_data if item['language'] == "Total"), None)
    
    if total_lines_of_code is not None:
        print(f"Modified LOC: {total_lines_of_code}")
    else:
        print("Total lines of code not found")

if __name__ == "__main__":
    main()

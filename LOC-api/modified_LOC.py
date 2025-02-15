import json
import os
import subprocess
import tempfile
import argparse
import requests
from urllib.parse import urlparse

def get_github_repo():
    parser = argparse.ArgumentParser(description="Clone a GitHub repo and analyze LOC using cloc.")
    parser.add_argument("repo_url", type=str, help="GitHub repository URL")
    args = parser.parse_args()
    return args.repo_url

def clone_repo(repo_url, temp_dir):
    subprocess.run(["git", "clone", repo_url, temp_dir], check=True)

def run_cloc(temp_dir):
    output_file = os.path.join(temp_dir, "cloc_output.json")
    subprocess.run(["cloc", temp_dir, "--json", f"--out={output_file}"], check=True)
    return output_file

def compute_modified_loc(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    
    modified_loc = 0
    for lang, stats in data.items():
        if isinstance(stats, dict):  # Ensure it's not metadata
            code = stats.get("code", 0)
            comments = stats.get("comment", 0)
            modified_loc += code + (comments / 2)
    
    return modified_loc

def fetch_loc_cloc(repo_url):
    try:
        parsed = urlparse(repo_url)
        if not all([parsed.scheme, parsed.netloc]):
            return {"total_lines": None, "error": "Invalid URL format"}
        
        repo_path = parsed.path.strip("/")
        if repo_path.endswith(".git"):
            repo_path = repo_path[:-4]
            
        # Validate we have a proper GitHub path
        if "/" not in repo_path or repo_path.count("/") != 1:
            return {"total_lines": None, "error": "Invalid GitHub repository format"}

        api_url = f"https://api.codetabs.com/v1/loc/?github={repo_path}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        loc_data = response.json()
        total_lines = next((item['linesOfCode'] for item in loc_data if item['language'] == "Total"), None)
        
        return {"total_lines": total_lines, "error": None}

    except Exception as e:
        return {"total_lines": None, "error": f"CodeTabs error: {str(e)}"}
    

def main():
    repo_url = get_github_repo()
    result = fetch_loc_cloc(repo_url)
    
    if result["error"]:
        print(f"Error: {result['error']}")
        exit(1)
        
    print(f"Modified LOC: {result['total_lines']}")

if __name__ == "__main__":
    main()
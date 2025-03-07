import json
import os
import subprocess
import tempfile
import argparse
from urllib.parse import urlparse

def get_github_repo():
    parser = argparse.ArgumentParser(description="Clone a GitHub repo and analyze LOC using cloc.")
    parser.add_argument("repo_url", type=str, help="GitHub repository URL")
    args = parser.parse_args()
    return args.repo_url

def clone_repo(repo_url, temp_dir):
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
    except subprocess.CalledProcessError:
        print("Failed to clone repository.")
        exit(1)

def run_cloc(temp_dir):
    output_file = os.path.join(temp_dir, "cloc_output.json")
    try:
        subprocess.run(["cloc", temp_dir, "--json", f"--out={output_file}"], check=True)
    except subprocess.CalledProcessError:
        print("Failed to run cloc.")
        exit(1)
    return output_file

def compute_modified_loc(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    
    modified_loc = 0
    for lang, stats in data.items():
        if lang in ["header", "SUM"]:  # Ignore metadata
            continue
        if isinstance(stats, dict):
            code = stats.get("code", 0)
            comments = stats.get("comment", 0)
            modified_loc += code + (comments / 2)
    
    return modified_loc

def main():
    repo_url = get_github_repo()
    with tempfile.TemporaryDirectory() as temp_dir:
        clone_repo(repo_url, temp_dir)
        json_output = run_cloc(temp_dir)
        modified_loc = compute_modified_loc(json_output)
        print(f"Modified LOC: {modified_loc}")

if __name__ == "__main__":
    main()

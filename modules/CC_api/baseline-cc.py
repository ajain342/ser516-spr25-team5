import os
import subprocess
import argparse
import shutil
import tempfile
from urllib.parse import urlparse
from modules.fetch_repo import fetch_repo

def get_git_code_churn(repo_path):
    if not os.path.exists(repo_path) or not os.path.exists(os.path.join(repo_path, ".git")):
        print("Repository path does not exist or is not a valid git repository.")
        return

    try:
        total_commits = int(subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip())
    except subprocess.CalledProcessError:
        print("Error: The repository is empty or HEAD does not exist.")
        return
    
    print(f"\nTotal commits: {total_commits}")
    
    if total_commits == 0:
        print("The repository has no commits. Nothing to analyze.")
        return

    num_commits_before_latest = int(input("Enter the number of commits before the latest to compare: "))
    if num_commits_before_latest < 0 or num_commits_before_latest >= total_commits:
        print("Invalid input. Enter a number between 0 and the total number of commits - 1.")
        return
    
    start_commit = f"HEAD~{num_commits_before_latest}" if num_commits_before_latest > 0 else "HEAD~1"
    end_commit = "HEAD"
    
    commits = get_commits(repo_path, start_commit, end_commit)
    
    files = {}
    contribution = 0
    churn = 0
    modified = 0
    
    for commit in commits:
        files, contribution, churn, modified = get_loc(repo_path, commit, files, contribution, churn, modified)
    
    print(f"\nCode Churn Metrics for commits between {start_commit} and {end_commit}:")
    print(f"Total added lines: {contribution}")
    print(f"Total Deleted Lines: {churn}")
    print(f"Total Modified Lines: {modified}")
    print(f"Code Churn: {contribution + churn + modified}")

def get_commits(repo_path, start_commit, end_commit):
    command = ["git", "log", "--format=%H", "--no-merges", f"{start_commit}..{end_commit}"]
    return subprocess.run(command, cwd=repo_path, capture_output=True, text=True, check=True).stdout.splitlines()

def get_loc(repo_path, commit, files, contribution, churn, modified):
    command = ["git", "show", "--format=", "--unified=0", "--numstat", commit]
    results = subprocess.run(command, cwd=repo_path, capture_output=True, text=True, check=True).stdout.splitlines()
    
    for result in results:
        parts = result.split("\t")
        if len(parts) == 3:
            try:
                added, deleted = int(parts[0]), int(parts[1])
                file = parts[2]
                if file not in files:
                    files[file] = {}
                if added > 0:
                    contribution += added
                if deleted > 0:
                    churn += deleted
                if added > 0 and deleted > 0:
                    modified += min(added, deleted)
            except ValueError:
                continue
    return files, contribution, churn, modified

def main():
    try:
        parser = argparse.ArgumentParser(description="Compute Git code churn from a GitHub repository.")
        parser.add_argument("repo_url", type=str, help="GitHub repository URL")
        
        args = parser.parse_args()
        
        fetch_result = fetch_repo(args.repo_url)
        if "error" in fetch_result:
            print(f"Error: {fetch_result['error']}")
            return
            
        repo_path = fetch_result["temp_dir"]
        if repo_path:
            get_git_code_churn(repo_path)
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

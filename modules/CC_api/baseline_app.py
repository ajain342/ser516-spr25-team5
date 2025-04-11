import os
import subprocess
import shutil
import tempfile
from flask import Flask, request, jsonify
from modules.utilities.fetch_repo import fetch_repo

def get_commits(repo_path, start_commit, end_commit):
    command = ["git", "log", "--format=%H", "--no-merges", f"{start_commit}..{end_commit}"]
    return subprocess.run(command, cwd=repo_path, capture_output=True, text=True, check=True).stdout.splitlines()

def get_loc(repo_path, commit):
    command = ["git", "show", "--format=", "--unified=0", "--numstat", commit]
    results = subprocess.run(command, cwd=repo_path, capture_output=True, text=True, check=True).stdout.splitlines()
    
    added_lines, deleted_lines, modified_lines = 0, 0, 0
    for result in results:
        parts = result.split("\t")
        if len(parts) == 3:
            try:
                added, deleted = int(parts[0]), int(parts[1])
                if added > 0:
                    added_lines += added
                if deleted > 0:
                    deleted_lines += deleted
                if added > 0 and deleted > 0:
                    modified_lines += min(added, deleted)
            except ValueError:
                continue
    return added_lines, deleted_lines, modified_lines

def get_git_code_churn(repo_url, num_commits_before_latest):
    repo_path = None
    try:
        if not repo_url:
            return jsonify({"error": "Missing repository URL"}), 400
        
        fetch_result = fetch_repo(repo_url)
        if "error" in fetch_result:
            return jsonify({"error": fetch_result["error"]}), 400
        
        repo_path = fetch_result["repo_dir"]
        total_commits = int(subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip())
        if total_commits == 0:
            return jsonify({"error": "Repository has no commits"}), 400
        
        if total_commits >= 1000:
            return jsonify({"error": "Too large repo, please enter a repo with less than 1000 commits."}), 400
        if num_commits_before_latest < 0:
            return jsonify({"error": "The number of commits must be a non-negative integer."}), 400
        if num_commits_before_latest >= total_commits:
            return jsonify({"error": "The number of commits specified exceeds the available commits in the repository."}), 400
        
        start_commit = f"HEAD~{num_commits_before_latest}" if num_commits_before_latest > 0 else "HEAD~1"
        end_commit = "HEAD"
        
        commits = get_commits(repo_path, start_commit, end_commit)
        added_lines, deleted_lines, modified_lines = 0, 0, 0
        
        for commit in commits:
            a, d, m = get_loc(repo_path, commit)
            added_lines += a
            deleted_lines += d
            modified_lines += m
        
        return jsonify({
            "method": "online",
            "added_lines": added_lines,
            "commit_range": f"{start_commit} to {end_commit}",
            "deleted_lines": deleted_lines,
            "modified_lines": modified_lines,
            "result": added_lines + deleted_lines + modified_lines,
            "total_commits": total_commits
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
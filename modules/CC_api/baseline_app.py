import os
import subprocess
import shutil
import tempfile
from flask import Flask, request, jsonify

app = Flask(__name__)

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        return None
    return temp_dir

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

@app.route('/baseline-CC', methods=['POST'])
def get_git_code_churn(repo_url, num_commits_before_latest):
    
    if not repo_url:
        return jsonify({"error": "Missing repository URL"}), 400
    
    repo_path = clone_repo(repo_url)
    if not repo_path:
        return jsonify({"error": "Failed to clone repository"}), 500
    
    try:
        total_commits = int(subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip())
        if total_commits == 0:
            return jsonify({"error": "Repository has no commits"}), 400
        
        if num_commits_before_latest < 0 or num_commits_before_latest >= total_commits:
            return jsonify({"error": "Invalid number of commits specified"}), 400
        
        start_commit = f"HEAD~{num_commits_before_latest}" if num_commits_before_latest > 0 else "HEAD~1"
        end_commit = "HEAD"
        
        commits = get_commits(repo_path, start_commit, end_commit)
        added_lines, deleted_lines, modified_lines = 0, 0, 0
        
        for commit in commits:
            a, d, m = get_loc(repo_path, commit)
            added_lines += a
            deleted_lines += d
            modified_lines += m
        
        return {
            "method": "online",
            "added_lines": added_lines,
            "commit_range": f"{start_commit} to {end_commit}",
            "deleted_lines": deleted_lines,
            "modified_lines": modified_lines,
            "net_change or churn": added_lines + deleted_lines + modified_lines,
            "total_commits": total_commits
        }
    
    finally:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, ignore_errors=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
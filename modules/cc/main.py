import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from flask import Flask, request, jsonify
# from modules.cc.baseline_app import get_git_code_churn
from modules.utilities.fetch_repo import fetch_repo
from modules.utilities.response_wrapper import wrap_with_timestamp
import git

app = Flask(__name__)

def get_commit_count(repo):
    return len(list(repo.iter_commits()))

def compute_code_churn(repo, start_commit, end_commit):
    
    added_lines = 0
    deleted_lines = 0
    modified_lines = 0

    diff_stat = repo.git.diff(start_commit, end_commit, '--numstat')

    for line in diff_stat.split("\n"):
        parts = line.split("\t")
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

@app.route('/cc', methods=['POST'])
def code_churn():
    data = request.get_json()
    repo_url = data.get("repo_url")

    try:
        num_commits_before_latest = int(data.get("num_commits_before_latest", 0))
    except Exception:
        return jsonify({"error": "Enter commits in number."}), 400

    # method = data.get("method")

    try:
        # if method == "modified":
        if not repo_url:
            return jsonify({"error": "Missing 'repo_url' in request data"}), 400

        fetch_res= fetch_repo(repo_url)
        if isinstance(fetch_res, dict) and "error" in fetch_res:
            return jsonify({"error": fetch_res["error"]}), 200
        
        head_sha, repo_path = fetch_res

        repo = git.Repo(repo_path)
        total_commits = get_commit_count(repo)

        if total_commits >= 1000:
            return jsonify({"error": "Too large repo, please enter a repo with less than 1000 commits."}), 400
        if num_commits_before_latest < 0:
            return jsonify({"error": "The number of commits must be a non-negative integer."}), 400
        if num_commits_before_latest >= total_commits:
            return jsonify({"error": "The number of commits specified exceeds the available commits in the repository."}), 400

        start_commit = f"HEAD~{num_commits_before_latest}" if num_commits_before_latest > 0 else "HEAD~1"
        end_commit = "HEAD"

       
        added, deleted, modified = compute_code_churn(repo, start_commit, end_commit)
        result = {
            # "method": method,
            "total_commits": total_commits,
            "commit_range": f"{start_commit} to {end_commit}",
            "added_lines": added,
            "deleted_lines": deleted,
            "modified_lines": modified,
            "result": added + deleted + modified
        }

        repo.close()
        return jsonify(wrap_with_timestamp(result))

        # elif method == "online":
        #     return jsonify(wrap_with_timestamp(get_git_code_churn(repo_url, num_commits_before_latest)))

        # else:
        #     return jsonify({"error": "Invalid method. Use 'online' or 'modified'"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
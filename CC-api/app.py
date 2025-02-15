import git
import os
import tempfile
from flask import Flask, request, jsonify

app = Flask(__name__)

def clone_repo(repo_url):
    
    temp_dir = tempfile.mkdtemp()
    repo = git.Repo.clone_from(repo_url, temp_dir)
    return repo, temp_dir

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

@app.route('/code-churn', methods=['POST'])
def code_churn():
    
    try:
        data = request.get_json()
        repo_url = data.get("repo_url")
        num_commits_before_latest = int(data.get("num_commits_before_latest", 0))

        if not repo_url:
            return jsonify({"error": "Missing 'repo_url' in request data"}), 400

        
        repo, repo_path = clone_repo(repo_url)

        
        total_commits = get_commit_count(repo)
        
        if num_commits_before_latest < 0 or num_commits_before_latest >= total_commits:
            return jsonify({"error": "invalid number of commits before latest"}), 400

        
        start_commit = f"HEAD~{num_commits_before_latest}" if num_commits_before_latest > 0 else "HEAD~1"
        end_commit = "HEAD"

        
        added, deleted, modified = compute_code_churn(repo, start_commit, end_commit)

        
        repo.close()
        os.system(f"rm -rf {repo_path}")

        return jsonify({
            "total_commits": total_commits,
            "commit_range": f"{start_commit} to {end_commit}",
            "added_lines": added,
            "deleted_lines": deleted,
            "modified_lines": modified,
            "net_change or churn": added + deleted + modified
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

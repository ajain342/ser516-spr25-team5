import os
import re
import subprocess
import shutil
import tempfile

def get_git_code_churn(repo_url, num_commits_before_latest=0):
    """
    Clones the repository, computes code churn between HEAD and a specified commit,
    and returns a dictionary with the result or an error message.
    """
    # Validate repository URL format
    pattern = re.compile(r'^https?:\/\/(www\.)?github\.com\/[^/]+\/[^/]+', re.IGNORECASE)
    if not repo_url or not pattern.match(repo_url):
        return {"error": "Invalid GitHub repository URL"}
    
    try:
        num_commits_before_latest = int(num_commits_before_latest)
    except ValueError:
        return {"error": "num_commits_before_latest must be an integer"}
    
    # Clone the repository into a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir],
                       check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {"error": "Failed to clone repository. It may be private or invalid."}
    
    try:
        # Count total commits
        count_cmd = ["git", "rev-list", "--count", "HEAD"]
        proc = subprocess.run(count_cmd, cwd=temp_dir,
                              capture_output=True, text=True, check=True)
        total_commits = int(proc.stdout.strip())
        if total_commits == 0:
            return {"error": "Repository has no commits"}
        if num_commits_before_latest < 0 or num_commits_before_latest >= total_commits:
            return {"error": "Invalid number of commits specified"}
        
        start_commit = f"HEAD~{num_commits_before_latest}" if num_commits_before_latest > 0 else "HEAD~1"
        end_commit = "HEAD"
        
        # Get list of commits in range
        command = ["git", "log", "--format=%H", "--no-merges", f"{start_commit}..{end_commit}"]
        result = subprocess.run(command, cwd=temp_dir,
                                capture_output=True, text=True, check=True)
        commits = result.stdout.splitlines()
        
        added_lines, deleted_lines, modified_lines = 0, 0, 0
        for commit in commits:
            cmd = ["git", "show", "--format=", "--unified=0", "--numstat", commit]
            res = subprocess.run(cmd, cwd=temp_dir,
                                 capture_output=True, text=True, check=True)
            for line in res.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) == 3:
                    try:
                        added, deleted = int(parts[0]), int(parts[1])
                        added_lines += added
                        deleted_lines += deleted
                        if added > 0 and deleted > 0:
                            modified_lines += min(added, deleted)
                    except ValueError:
                        continue
                        
        return {
            "method": "online",
            "added_lines": added_lines,
            "deleted_lines": deleted_lines,
            "modified_lines": modified_lines,
            "net_change or churn": added_lines + deleted_lines + modified_lines,
            "total_commits": total_commits
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python baseline_app.py <GitHub_Repo_URL> <num_commits_before_latest>")
        sys.exit(1)
    repo_url = sys.argv[1]
    num_commits_before_latest = sys.argv[2]
    result = get_git_code_churn(repo_url, num_commits_before_latest)
    print(result)

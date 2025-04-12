from modules.utilities.fetch_repo import fetch_repo
import git

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

def main():
    repo_url = input("GitHub repo URL: ").strip()

    fetch_result = fetch_repo(repo_url)
    if "error" in fetch_result:
        return

    repo_path = fetch_result["repo_dir"]
    repo = git.Repo(repo_path)

    total_commits = get_commit_count(repo)
    print(f"\nTotal commits: {total_commits}")

    
    while True:
        try:
            num_commits_before_latest = int(input("Enter the number of commits before the latest to compare: "))
            if num_commits_before_latest < 0 or num_commits_before_latest >= total_commits:
                print("invalid input. Enter a number between 0 and the total number of commits - 1.")
            else:
                break
        except ValueError:
            print("invalid input. enter a valid number.")

    
    start_commit = f"HEAD~{num_commits_before_latest}" if num_commits_before_latest > 0 else "HEAD~1"
    end_commit = "HEAD"

    
    added, deleted, modified = compute_code_churn(repo, start_commit, end_commit)

    
    print(f"\nCode Churn Metrics for commits between {start_commit} and {end_commit}:")
    print(f"Total added lines: {added}")
    print(f"Total Deleted Lines: {deleted}")
    print(f"Total Modified Lines: {modified}")
    print(f"Net Change (Total Churn): {added + deleted}")


if __name__ == "__main__":
    main()
import json
import os
import subprocess
import tempfile
import argparse

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

def cloc_analysis(repo_url):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            clone_repo(repo_url, temp_dir)
            json_output = run_cloc(temp_dir)
            return {
                "modified_loc": compute_modified_loc(json_output),
                "error": None
            }
    except subprocess.CalledProcessError as e:
        return {"modified_loc": None, "error": f"Process error: {str(e)}"}
    except Exception as e:
        return {"modified_loc": None, "error": f"Unexpected error: {str(e)}"}
    

def main():
    repo_url = get_github_repo()
    result = cloc_analysis(repo_url)
    
    if result["error"]:
        print(f"Error: {result['error']}")
        exit(1)
        
    print(f"Modified LOC: {result['modified_loc']}")

if __name__ == "__main__":
    main()
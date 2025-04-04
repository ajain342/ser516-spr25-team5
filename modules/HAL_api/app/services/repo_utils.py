import os
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
import git
import tempfile
from java_file_parser import JavaFileParser
import config

class RepoUtils:
    @staticmethod
    def clone_repo(repo_url):
        temp_dir = tempfile.mkdtemp()
        try:
            repo = git.Repo.clone_from(repo_url, temp_dir)
        except Exception:
            raise Exception("Failed to clone repository. Ensure the repository is public or valid.")
        return repo, temp_dir

    @staticmethod
    def read_files(temp_dir):
        if os.path.isdir(temp_dir):
            file_contents = {}
            for root, _, files in os.walk(temp_dir):
                for file_name in files:
                    full_path = os.path.join(root, file_name)
                    if JavaFileParser.is_valid(full_path):
                        _, ext = os.path.splitext(file_name)
                        if ext in config.white_list:
                            file_contents[full_path] = JavaFileParser.parse_file(full_path)
            return file_contents
        return {}
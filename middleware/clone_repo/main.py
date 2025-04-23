from flask import Flask, request, jsonify
from clone_repo import fetch_repo

app = Flask(__name__)

@app.route("/clone", methods=["POST"])
def clone():
    try:
        data = request.get_json()
        repo_url = data["repo_url"]
        head_sha, repo_dir = fetch_repo(repo_url)
        return jsonify({"head_sha": head_sha,
                        "repo_dir": repo_dir}), 200
    except Exception as e:
        return jsonify({"message": f"Error occured while cloning repositoy: {e}"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
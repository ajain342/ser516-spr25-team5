from flask import Flask, request, jsonify
from urllib.parse import urlparse
import re

# These two functions presumably do the actual GitHub calls / logic for calculating MTTR
# They should raise or return an error if the repo is private/invalid
from modified_MTTR import fetch_mttr_gitapi
from online_tool_MTTR import fetch_mttr_online

app = Flask(__name__)

def validate_github_url(repo_url):
    """
    Returns True if repo_url looks like a valid GitHub URL: https://github.com/owner/repo
    Otherwise, returns False.
    """
    pattern = re.compile(r'^https?:\/\/(www\.)?github\.com\/[^/]+\/[^/]+', re.IGNORECASE)
    return bool(pattern.match(repo_url))

@app.route('/')
def home():
    return jsonify(message="Visit /mttr to calculate MTTR")

@app.route('/mttr', methods=['POST'])
def get_mttr():
    data = request.get_json()
    if not data or 'repo_url' not in data:
        return jsonify({"error": "Missing 'repo_url' in request"}), 400

    repo_url = data['repo_url']
    method = data.get('method')

    # 1) Validate the GitHub URL
    if not validate_github_url(repo_url):
        return jsonify({"error": "Invalid GitHub repository URL"}), 400

    try:
        # 2) Handle 'modified' or 'online' logic
        if method == 'modified':
            # Calls your function that presumably uses the GitHub API or local clone
            result = fetch_mttr_gitapi(repo_url)
        elif method == 'online':
            # Calls your function that fetches issues/PRs from GitHub to calculate MTTR
            result = fetch_mttr_online(repo_url)
        else:
            return jsonify({"error": "Invalid method. Use 'online' or 'modified'"}), 400

        # 3) If the returned object has an "error" key, handle it
        #    For example, "No closed issues" => 400
        #    Private or invalid => 400
        #    Or something else => maybe 500
        if "error" in result and result["error"]:
            # You can further customize logic based on the message
            error_msg = result["error"]
            if "No closed" in error_msg or "private" in error_msg.lower() or "invalid" in error_msg.lower():
                return jsonify({
                    "error": error_msg,
                    "repo_url": repo_url
                }), 400
            else:
                return jsonify({
                    "error": error_msg,
                    "repo_url": repo_url
                }), 500

        # 4) If no error, we assume success. Return the final MTTR data.
        #    e.g. result might look like { "mttr": 3.75, "someOtherField": ... }
        return jsonify({
            "repo_url": repo_url,
            "result": round(result["mttr"], 2) if "mttr" in result else None,
            "method": method
        })

    except Exception as e:
        # 5) Catch any unexpected errors (e.g., network failure, parsing issue, etc.)
        return jsonify({
            "error": f"Server error: {str(e)}",
            "method": method,
            "repo_url": repo_url
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

from flask import Flask, request, jsonify
from urllib.parse import urlparse
from modified_MTTR import fetch_mttr_gitapi
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message="Visit /mttr to calculate mttr")

@app.route('/mttr', methods=['POST'])
def get_mttr():
    data = request.get_json()
    
    if not data or 'repo_url' not in data:
        return jsonify({"error": "Missing repo_url in request"}), 400
    
    repo_url = data['repo_url']
    result = fetch_mttr_gitapi(repo_url)
    
    if result["error"]:
        return jsonify({
            "error": result["error"],
            "repo_url": repo_url
        }), 400 if "No closed" in result["error"] else 500
    
    return jsonify({
        "repo_url": repo_url,
        "mttr_hours": round(result["mttr"], 2),
        "method": "git-api"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
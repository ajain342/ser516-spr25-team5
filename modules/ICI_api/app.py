from flask import Flask, request, jsonify
from urllib.parse import urlparse
from ici import compute_ici

app = Flask(__name__)

def parse_url(repo_url):
    parsed_url = urlparse(repo_url)
    repo_path = parsed_url.path.strip("/")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    if repo_path.count('/') != 1:
        return None
    return repo_path

@app.route('/')
def home():
    return jsonify(message="Welcome! Use /ici to compute Infrastructure Cost Index.")

@app.route('/ici', methods=['POST'])
def get_ici():
    data = request.get_json()
    
    if not data or 'repo_url' not in data:
        return jsonify({"error": "Missing repo_url in request"}), 400
    
    repo_url = data['repo_url']
    repo_path = parse_url(repo_url)

    if not repo_path:
        return jsonify({"error": "Invalid GitHub repository URL"}), 400

    try:
        result = compute_ici(repo_url)
        if result is None:
            return jsonify({"error": "Failed to compute ICI"}), 500

        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "repo_url": repo_url
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)

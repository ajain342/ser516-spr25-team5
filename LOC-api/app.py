from flask import Flask, request, jsonify
from modified_LOC import fetch_loc_cloc
from online_Tool import fetch_loc_codetabs
from urllib.parse import urlparse

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
    return jsonify(message="Visit /loc to calculate LOC")

@app.route('/loc', methods=['POST'])
def get_loc():
    data = request.get_json()
    
    if not data or 'repo_url' not in data:
        return jsonify({"error": "Missing repo_url in request"}), 400
    
    repo_url = data['repo_url']
    method = data.get('method', 'cloc')  # Default to cloc

    repo_path = parse_url(repo_url)
    if not repo_path:
        return jsonify({"error": "Invalid GitHub repository URL"}), 400

    try:
        if method == 'cloc':
            result = fetch_loc_cloc(repo_url)
        elif method == 'codetabs':
            result = fetch_loc_codetabs(repo_path)
        else:
            return jsonify({"error": "Invalid method. Use 'cloc' or 'codetabs'"}), 400
        
        if result.get('error'):
            return jsonify(result), 500
            
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "method": method,
            "repo_url": repo_url
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
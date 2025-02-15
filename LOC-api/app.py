from flask import Flask, request, jsonify
from modified_LOC import fetch_loc_cloc
from online_Tool import fetch_loc_codetabs

app = Flask(__name__)

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
    
    if method == 'cloc':
        result = fetch_loc_cloc(repo_url)
    elif method == 'codetabs':
        result = fetch_loc_codetabs(repo_url)
    else:
        return jsonify({"error": "Invalid method. Use 'cloc' or 'codetabs'"}), 400
    
    if result.get('error'):
        return jsonify(result), 500
        
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
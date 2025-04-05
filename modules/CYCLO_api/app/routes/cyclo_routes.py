from flask import jsonify, Blueprint, request
from app.services.cyclo_service import get_cc
from file_utilities.repo_utils import RepoUtils


bp = Blueprint("cyclo", __name__)

@bp.route("/info", methods=["GET"])
def info():
    return jsonify({
        "metricName": "Cyclomatic Complexity",
        "requestFormat": {
            "code": "file_contents"
        },
        "responseFormat": {
                    "Value": {
                        "abbreviation": "Value",
                        "definition": "Contains cyclomatic complexity and summary at the end"
                    },
                    "Cyclo Params/Aggregate": {
                        "abbreviation": "Cyclo Params/Aggregate",
                        "definition": "Contains cyclomatic complexity and aggregate parameters"
                    }
                }
    }), 200

@bp.route("/run", methods=["POST"])
def analyze_cc():
    
    data = request.get_json()
    repo_url = data.get("repo_url")
    if not repo_url:
        return jsonify({"error": "Missing 'repo_url'"}), 400
    
    _, temp_dir = RepoUtils.clone_repo(repo_url)
    code = RepoUtils.read_files(temp_dir)
    
    if not code:
        return jsonify({"message": "No Java files found in the repository"}), 400


    if isinstance(code, dict):
        code = "\n".join(code.values())
    try:
        results = get_cc(code)


        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))
from flask import jsonify, Blueprint, request
from app.services.cyclo_service import get_cc
from modules.utilities.fetch_repo import fetch_repo
from modules.utilities.read_java_files import read_files
from modules.utilities.cache import MetricCache
from modules.utilities.response_wrapper import wrap_with_timestamp

bp = Blueprint("cyclo", __name__)
cc_cache = MetricCache()

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

@bp.route("/cyclo", methods=["POST"])
def analyze_cc():
    data = request.get_json()
    repo_url = data.get("repo_url")
    if not repo_url:
        return jsonify({"error": "Missing 'repo_url'"}), 400

    try:
        fetch_result = fetch_repo(repo_url)
        if isinstance(fetch_result, dict) and "error" in fetch_result:
            return jsonify({"error": fetch_result["error"]}), 200

        head_sha, repo_dir = fetch_result
        cache_key = f"{repo_url}|{head_sha}"

        if cc_cache.contains(cache_key):
            return jsonify({"method": "modified", "results": cc_cache.get(cache_key)}), 200

        code = read_files(repo_dir)
        if not code:
            return jsonify({"message": "No Java files found in the repository"}), 400

        if isinstance(code, dict):
            code = "\n".join(code.values())

        results = get_cc(code)
        cc_cache.add(cache_key, results)

        return jsonify(wrap_with_timestamp(results)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

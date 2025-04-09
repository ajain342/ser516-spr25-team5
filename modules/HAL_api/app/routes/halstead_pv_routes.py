import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))
from flask import jsonify, Blueprint, request
from app.services.halstead_pv_service import HalsteadMetrics
from app.services.extractor import Extractor, ParsingException
from modules.utilities import fetch_repo, read_java_files

bp = Blueprint("halstead_pv", __name__)

@bp.route("/info", methods=["GET"])
def info():
    return (
    jsonify({
        "metricName": "Halstead Program Value",
        "requestFormat": {
            "code": {"file_path": "file_contents"}
        },
        "responseFormat": {
            "difficulty": {
                "abbreviation": "D",
                "definition": "Difficulty of the code base"
            },
            "effort": {
                "abbreviation": "E",
                "definition": "Efforts of the code base"
            },
            "length": {
                "abbreviation": "N",
                "definition": "Program length of the code base"
            },
            "vocabulary": {
                "abbreviation": "Vc",
                "definition": "Vocabulary of the code base"
            },
            "volume": {
                "abbreviation": "Vl",
                "definition": "Volume of the code base"
            }
        }
        }),200)



@bp.route("/run", methods=["POST"])
def calculate_halstead_metrics():
    try:
        data = request.get_json()
        repo_url = data.get("repo_url")
        if not repo_url:
            return jsonify({"error": "Missing 'repo_url'"}), 400

        result = fetch_repo(repo_url)
        code_files = read_java_files.read_files(result["temp_dir"])

        if not code_files:
            return jsonify({"message": "No Java files found in the repository"}), 400

        project_metrics = []

        if not isinstance(code_files, dict):
            return jsonify({"error": "'file_path' must contain a dictionary of file paths and contents."}), 400

        for file_path, code in code_files.items():
            if not isinstance(code, str):
                return jsonify({"error": f"Invalid file content for {file_path}. Expected a string."}), 400

            try:
                extractor = Extractor(code)
                operators, operands = extractor.get_params()
                metrics = HalsteadMetrics.calculate(operators, operands)

                project_metrics.append({
                    "file_name": os.path.basename(file_path), 
                    "metrics": metrics
                })

            except ParsingException as e:
                return jsonify({"error": f"Failed to process {file_path}: {e}"}), 400

        if not project_metrics:
            return jsonify({"error": "No valid Halstead metrics calculated."}), 400

        aggregated_metrics = HalsteadMetrics.aggregate_metrics({m["file_name"]: m["metrics"] for m in project_metrics})
        project_metrics.append({"Summary": aggregated_metrics})

        return jsonify({"file_metrics": project_metrics}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "An unexpected error occurred while processing your request."}), 500


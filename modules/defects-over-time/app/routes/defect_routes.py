from flask import jsonify, Blueprint, request
from app.services.defect_service import defect_service

bp = Blueprint("defect", __name__)


@bp.route("/info", methods=["GET"])
def info():
    return (
        jsonify(
            {
                "metricName": "Defects",
                "requestFormat": {
                    "repo_url": "repo_url",
                },
                "responseFormat": {
                    "Metrics": {
                        "abbreviation": "Metrics",
                        "definition": "Contains all the defect parameters"
                    },
                    "Values": {
                        "abbreviation": "Values",
                        "definition": "Contains the values for the defect parameters"
                    }
                    
                }
            }
        ),
        200,
    )


@bp.route("/defects-over-time", methods=["POST"])
def defects():
    defect_request = request.json
    if not defect_request:
        return jsonify({"error": "Request is empty"}), 400

    if "repo_url" not in defect_request:
        return jsonify({"error": "Missing 'repo_url' in request"}), 400
    
    if defect_request["repo_url"] == "":
        return jsonify({"error": "Empty 'repo_url' in request"}), 400

    return defect_service(defect_request), 200

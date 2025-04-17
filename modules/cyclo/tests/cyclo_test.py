import json

import pytest
from flask import jsonify, Flask
import os
from pathlib import Path
from app.services.cyclo_service import get_cc


app = Flask(__name__)

# def test_hello_world():
#     assert hello_world() == "Hello from the Cyclomatic Complexity Service!"

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def extract_java_file(directory_name):
    directory = Path(directory_name)

    code_list = []

    if not directory.exists() or not directory.is_dir():
        return None, "This directory does not exist"

    for file_path in directory.glob("*.java"):
        with open(file_path, "r") as file:
            content = file.read()
            code_list.append(content)

    return code_list

def test_cyclo_service(client):
    main_dir = os.path.dirname(os.path.abspath(__file__))
    testfolder_path = os.path.join(main_dir, 'testfolder')
    code_list = extract_java_file(testfolder_path)


    for code in code_list:
        data = get_cc(code)
        print(json.dumps(data, indent=2))

        expected = [
            {"Function name": "BarChart::paint", "Cyclomatic complexity":6}
        ]
        #assert len(data) == len(expected)
        assert data[0]["threshold"] == 3
        assert data[1]["Cyclomatic complexity"] == expected[0]["Cyclomatic complexity"]
        assert data[2]["average cyclomatic complexity"] == 6.0
        assert data[3]["total cyclomatic complexity"] == 6
        assert data[4]["functions evaluated"] == 1
        assert data[5]["max cyclomatic complexity"] == 6



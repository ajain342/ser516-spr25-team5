import unittest
import json
import requests
from flask import jsonify

class TestCodeChurnAPI(unittest.TestCase):
    API_URL = "http://localhost:5001/code-churn"

    def test_api_response(self):
        payload = {
                    'repo_url': 'https://github.com/kgary/ser421public',
                    'method': 'online',
                    'num_commits_before_latest': 10
                }
        response = requests.post(self.API_URL, json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("added_lines", data)
        self.assertIn("commit_range", data)
        self.assertIn("deleted_lines", data)
        self.assertIn("method", data)
        self.assertIn("modified_lines", data)
        self.assertIn("result", data)
        self.assertIn("total_commits", data)

        self.assertEqual(data["added_lines"],5664)
        self.assertEqual(data["commit_range"],"HEAD~10 to HEAD")
        self.assertEqual(data["deleted_lines"],819)
        self.assertEqual(data["method"],"online")
        self.assertEqual(data["modified_lines"],712)
        self.assertEqual(data["result"],7195)
        self.assertEqual(data["total_commits"],297)

if __name__ == '__main__':
    unittest.main()

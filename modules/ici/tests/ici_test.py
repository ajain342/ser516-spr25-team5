import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.ici.main import app

class TestICIAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_get_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
    
    def test_missing_repo_url(self):
        respone = self.client.post("/ici", json={})
        self.assertEqual(respone.status_code, 400)
        data = respone.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Missing 'repo_url'")

    def test_post_endpoint(self):
        payload = {
            'repo_url': 'https://github.com/kgary/ser421public'
            }
        response = self.client.post("/ici", json=payload)
        self.assertEqual(response.status_code, 200)
        results = response.get_json()
        self.assertIn("repo_size_mb", results["data"])
        self.assertIn("file_types", results["data"])
        self.assertIn("dependencies", results["data"])
        self.assertIn("ci_cd_usage", results["data"])
        self.assertIn("ici_score", results["data"])
        
if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.cc.main import app

class TestCodeChurnAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
    
    def test_api_response(self):
        payload = {
            "repo_url": "https://github.com/kgary/ser421public",
            "method": "online",
            "num_commits_before_latest": 10
}
        response = self.client.post('/code-churn', json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        self.assertIn("added_lines", data)
        self.assertIn("commit_range", data)
        self.assertIn("deleted_lines", data)
        self.assertIn("method", data)
        self.assertIn("modified_lines", data)
        self.assertIn("result", data)
        self.assertIn("total_commits", data)

if __name__ == '__main__':
    unittest.main()
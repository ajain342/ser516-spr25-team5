import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.CC_api.app import app

class TestCodeChurnAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
    
    def test_api_response(self):
        payload = {
            'repo_url': 'https://github.com/kgary/ser421public',
            'method': 'online',
            'num_commits_before_latest': 10
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

        self.assertEqual(data["added_lines"], 5664)
        self.assertEqual(data["commit_range"], "HEAD~10 to HEAD")
        self.assertEqual(data["deleted_lines"], 819)
        self.assertEqual(data["method"], "online")
        self.assertEqual(data["modified_lines"], 712)
        self.assertEqual(data["result"], 7195)
        self.assertEqual(data["total_commits"], 297)

if __name__ == '__main__':
    unittest.main()
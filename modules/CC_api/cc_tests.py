import unittest
import json
from app import app 

class TestCodeChurnAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_success_response(self):
        response = self.client.post('/code-churn',
                                    json={"repo_url": "https://github.com/mikaelvesavuori/github-dora-metrics.git",
                                          "num_commits_before_latest": 2})
        self.assertEqual(response.status_code, 200)

    def test_missing_repo_url(self):
        response = self.client.post('/code-churn',
                                    json={"num_commits_before_latest": 2})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing 'repo_url'", response.get_json().get('error', ''))

    def test_invalid_commit_number(self):
        response = self.client.post('/code-churn',
                                    json={"repo_url": "https://github.com/mikaelvesavuori/github-dora-metrics.git",
                                          "num_commits_before_latest": -1})
        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid number of commits", response.get_json().get('error', ''))

if __name__ == '__main__':
    unittest.main()

import unittest
import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.mttr.main import app

class TestMTTRAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_home_endpoint(self):
        response = self.client.get('/')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], "Visit /mttr to calculate mttr")

    def test_missing_repo_url(self):
        response = self.client.post('/mttr', json={})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Missing repo_url in request")

    @patch('modules.mttr.main.fetch_mttr_gitapi')
    @patch('modules.mttr.main.fetch_repo')
    def test_repository_with_no_issues(self, mock_fetch_repo, mock_fetch_mttr):
        mock_fetch_repo.return_value = ("dummysha", "/some/path")
        mock_fetch_mttr.return_value = {
            "error": "No closed issues found"
        }
        payload = {
            "repo_url": "https://github.com/Siddharthbadal/Python-Projects"
        }
        response = self.client.post('/mttr', json=payload)
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('No closed', data['error'])

    def test_calculation(self):
        payload = {
            "repo_url": "https://github.com/timescale/tsbs"
        }
        response = self.client.post('/mttr', json=payload)
        data = response.get_json()
        if response.status_code == 200:
            self.assertIn('result', data)
            self.assertIsInstance(data['result'], float)
        else:
            self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()

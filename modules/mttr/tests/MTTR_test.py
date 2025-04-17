import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.mttr.app import app

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

    def test_invalid_method_handling(self):
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs',
            'method': 'invalid'
        }
        response = self.client.post('/mttr', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Invalid method. Use 'online' or 'modified'")

    def test_missing_method_parameter(self):
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs'
        }
        response = self.client.post('/mttr', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Invalid method. Use 'online' or 'modified'")

    def test_repository_with_no_issues(self):
        payload = {
            'repo_url': 'https://github.com/Siddharthbadal/Python-Projects',
            'method': 'online'
        }
        response = self.client.post('/mttr', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('No closed', data['error'])

    def test_modified_method_calculation(self):
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs',
            'method': 'modified'
        }
        response = self.client.post('/mttr', json=payload)
        data = response.get_json()

        if response.status_code == 200:
            self.assertIn('repo_url', data)
            self.assertIn('result', data)
            self.assertIn('method', data)
            self.assertEqual(data['method'], 'modified')
            self.assertIsInstance(data['result'], float)
        else:
            self.assertIn('error', data)

    def test_online_method_calculation(self):
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs',
            'method': 'online'
        }
        response = self.client.post('/mttr', json=payload)
        data = response.get_json()

        if response.status_code == 200:
            self.assertIn('repo_url', data)
            self.assertIn('result', data)
            self.assertIn('method', data)
            self.assertEqual(data['method'], 'online')
            self.assertIsInstance(data['result'], float)
        else:
            self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
import json

class TestMTTRAPI(unittest.TestCase):
    BASE_URL = 'http://localhost:5003'  
    MTTR_ENDPOINT = f'{BASE_URL}/mttr'
    
    def test_home_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = requests.get(self.BASE_URL)
        print(f"\n[GET /] Response: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], "Visit /mttr to calculate mttr")

    def test_missing_repo_url(self):
        """Test missing repository URL parameter"""
        response = requests.post(self.MTTR_ENDPOINT, json={})
        print(f"\n[POST /mttr] No repo_url: {response.text}")
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Missing repo_url in request")

    def test_invalid_method_handling(self):
        """Test invalid calculation method handling"""
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs',
            'method': 'invalid'
        }
        response = requests.post(self.MTTR_ENDPOINT, json=payload)
        print(f"\n[POST /mttr] Invalid method: {response.text}")
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Invalid method. Use 'online' or 'modified'")

    def test_modified_method_calculation(self):
        """Test successful MTTR calculation using modified method"""
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs',
            'method': 'modified'
        }
        response = requests.post(self.MTTR_ENDPOINT, json=payload)
        print(f"\n[POST /mttr] Modified method: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('repo_url', data)
        self.assertIn('result', data)
        self.assertIn('method', data)
        self.assertEqual(data['method'], 'modified')
        self.assertIsInstance(data['result'], float)

    def test_online_method_calculation(self):
        """Test successful MTTR calculation using online method"""
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs',
            'method': 'online'
        }
        response = requests.post(self.MTTR_ENDPOINT, json=payload)
        print(f"\n[POST /mttr] Online method: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('repo_url', data)
        self.assertIn('result', data)
        self.assertIn('method', data)
        self.assertEqual(data['method'], 'online')
        self.assertIsInstance(data['result'], float)

    def test_repository_with_no_issues(self):
        """Test repository with no closed issues handling"""
        payload = {
            'repo_url': 'https://github.com/Siddharthbadal/Python-Projects',
            'method': 'online'
        }
        response = requests.post(self.MTTR_ENDPOINT, json=payload)
        print(f"\n[POST /mttr] No issues repo: {response.text}")
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('No closed', data['error'])

    def test_missing_method_parameter(self):
        """Test missing method parameter handling"""
        payload = {
            'repo_url': 'https://github.com/timescale/tsbs'
        }
        response = requests.post(self.MTTR_ENDPOINT, json=payload)
        print(f"\n[POST /mttr] Missing method: {response.text}")
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Invalid method. Use 'online' or 'modified'")

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
import unittest
import requests
import json

class TestLOCAPI(unittest.TestCase):
    BASE_URL = 'http://localhost:5002'  
    LOC_ENDPOINT = f'{BASE_URL}/loc'
    
    def test_home_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = requests.get(self.BASE_URL)
        print(f"\n[GET /] Response: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], "Visit /loc to calculate LOC")

    def test_missing_repo_url(self):
        """Test missing repository URL parameter"""
        response = requests.post(self.LOC_ENDPOINT, json={})
        print(f"\n[POST /loc] No repo_url: {response.text}")
        
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
        response = requests.post(self.LOC_ENDPOINT, json=payload)
        print(f"\n[POST /loc] Invalid method: {response.text}")
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Invalid method. Use 'online' or 'modified'")


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
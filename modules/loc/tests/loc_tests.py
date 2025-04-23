import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.loc.main import app  # Update this import path based on your structure

class TestLOCAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
    
    def test_home_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = self.client.get('/')
        print(f"\n[GET /] Response: {response.get_data(as_text=True)}")
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], "Visit /loc to calculate LOC")

    def test_missing_repo_url(self):
        """Test missing repository URL parameter"""
        response = self.client.post('/loc', json={})
        print(f"\n[POST /loc] No repo_url: {response.get_data(as_text=True)}")
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "Missing repo_url in request")

    # def test_invalid_method_handling(self):
    #     """Test invalid calculation method handling"""
    #     payload = {
    #         'repo_url': 'https://github.com/timescale/tsbs',
    #         'method': 'invalid'
    #     }
    #     response = self.client.post('/loc', json=payload)
    #     print(f"\n[POST /loc] Invalid method: {response.get_data(as_text=True)}")
        
    #     self.assertEqual(response.status_code, 400)
    #     data = response.get_json()
    #     self.assertIn('error', data)
    #     self.assertEqual(data['error'], "Invalid method. Use 'online' or 'modified'")

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)

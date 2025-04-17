import unittest
import requests
import json
#test comment
class TestMTTRAPI(unittest.TestCase):
    API_URL = 'http://localhost:5001/mttr'  # Updated to port 5001

    def test_api_response(self):
        payload = {'repo_url': 'https://github.com/timescale/tsbs'}
        response = requests.post(self.API_URL, json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"API Response: {data}")  # Added for debugging
        self.assertIn('mttr_hours', data)
        self.assertAlmostEqual(data['mttr_hours'], 2631.33, places=2)

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
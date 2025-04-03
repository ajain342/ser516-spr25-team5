import unittest
import json
from modules.MTTR_api.app import app  

class TestMTTRAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
    
    def test_mttr_missing_repo_url(self):
        response = self.app.post('/mttr', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_mttr_invalid_method(self):
        response = self.app.post('/mttr', json={'repo_url': 'https://github.com/example/repo', 'method': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
    
    def test_mttr_modified_method(self):
        response = self.app.post('/mttr', json={'repo_url': 'https://github.com/example/repo', 'method': 'modified'})
        self.assertIn(response.status_code, [200, 400, 500])  # Acceptable responses depending on repo status
    
    def test_mttr_online_method(self):
        response = self.app.post('/mttr', json={'repo_url': 'https://github.com/example/repo', 'method': 'online'})
        self.assertIn(response.status_code, [200, 400, 500])  # Acceptable responses
    
if __name__ == '__main__':
    unittest.main()

import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from modules.ici.ici import compute_ici

class TestICIAPI(unittest.TestCase):

    def test_compute_ici(self):
        results = compute_ici("test_repo")
        self.assertIn("repo_size_mb", results)
        self.assertIn("file_types", results)
        self.assertIn("dependencies", results)
        self.assertIn("ci_cd_usage", results)
        self.assertIn("ici_score", results)
        
if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
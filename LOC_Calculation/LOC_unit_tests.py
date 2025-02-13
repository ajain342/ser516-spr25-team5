import unittest
import json
import tempfile
from modified_LOC import compute_modified_loc

class TestComputeModifiedLOC(unittest.TestCase):

    def write_temp_json(self, data):
        """Helper function to write JSON data to a temp file and return the file path."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
        json.dump(data, temp_file)
        temp_file.close()
        return temp_file.name

    def test_empty_data(self):
        """Test with an empty JSON file."""
        file_path = self.write_temp_json({})
        self.assertEqual(compute_modified_loc(file_path), 0)

    def test_multiple_languages(self):
        """Test with multiple languages."""
        data = {
            "Java": {"code": 100, "comment": 50},
            "JavaScript": {"code": 200, "comment": 100}
        }
        file_path = self.write_temp_json(data)
        self.assertEqual(compute_modified_loc(file_path), 100 + (50 / 2) + 200 + (100 / 2))

    def test_missing_code_field(self):
        """Test when 'code' field is missing."""
        data = {"Java": {"comment": 50}}
        file_path = self.write_temp_json(data)
        self.assertEqual(compute_modified_loc(file_path), 50 / 2)

    def test_missing_comment_field(self):
        """Test when 'comment' field is missing."""
        data = {"Java": {"code": 100}}
        file_path = self.write_temp_json(data)
        self.assertEqual(compute_modified_loc(file_path), 100)

if __name__ == "__main__":
    unittest.main()

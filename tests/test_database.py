import unittest
from unittest.mock import MagicMock, patch
from app import database

class TestDatabase(unittest.TestCase):

    def test_validate_category(self):
        # Basic normalization
        self.assertEqual(database.validate_category("basketball"), "Basketball")
        self.assertEqual(database.validate_category("  soccer  "), "Soccer")
        
        # Synonyms
        self.assertEqual(database.validate_category("shoes"), "Footwear")
        self.assertEqual(database.validate_category("sneakers"), "Footwear")
        self.assertEqual(database.validate_category("clothing"), "Apparel")
        self.assertEqual(database.validate_category("tents"), "Camping")
        
        # Unknown categories pass through normalized
        self.assertEqual(database.validate_category("unknown"), "Unknown")
        
        # Empty input
        self.assertIsNone(database.validate_category(None))
        self.assertIsNone(database.validate_category(""))

    @patch('app.database.db')
    def test_search_products(self, mock_db):
        # Setup mock data
        mock_docs = [
            MagicMock(to_dict=lambda: {"title": "Soccer Ball", "description": "A ball"}),
            MagicMock(to_dict=lambda: {"title": "Basketball", "description": "Hoops"}),
            MagicMock(to_dict=lambda: {"title": "Running Shoes", "description": "Fast"}),
        ]
        
        # Mock the stream() method
        mock_stream = MagicMock()
        mock_stream.__iter__.return_value = mock_docs
        mock_db.collection.return_value.stream.return_value = mock_stream
        
        # Test search
        results = database.search_products("Ball")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Soccer Ball")
        self.assertEqual(results[1]["title"], "Basketball")
        
        # Test case insensitivity
        results_lower = database.search_products("ball")
        self.assertEqual(len(results_lower), 2)
        
        # Test no results
        results_none = database.search_products("Swimming")
        self.assertEqual(len(results_none), 0)

if __name__ == '__main__':
    unittest.main()

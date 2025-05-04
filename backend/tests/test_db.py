import unittest
from unittest.mock import patch, MagicMock

from src.db import add_document, delete_document, get_db, get_document, query_documents, start_db, update_document

class TestDatabase(unittest.TestCase):
    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.firestore.client')
    def test_start_db(self, mock_client, mock_initialize_app):
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        
        db = start_db()
        
        mock_initialize_app.assert_called_once()
        mock_client.assert_called_once()
        self.assertEqual(db, mock_db)

    @patch('firebase_admin.firestore.client')
    def test_get_db(self, mock_client):
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        
        db = get_db()
        
        mock_client.assert_called_once()
        self.assertEqual(db, mock_db)

    @patch('src.db.get_db')
    def test_add_document(self, mock_get_db):
        # Setup mock DB and document reference
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "test_doc_id"
        
        # Setup chain of mock calls
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Test function
        test_data = {"test": "test"}
        doc_id = add_document("test_collection", test_data)
        
        # Verify calls
        mock_get_db.assert_called_once()
        mock_db.collection.assert_called_once_with("test_collection")
        mock_collection.document.assert_called_once()
        mock_doc_ref.set.assert_called_once_with(test_data)
        self.assertEqual(doc_id, "test_doc_id")

    @patch('src.db.get_db')
    def test_get_document_exists(self, mock_get_db):
        # Setup mock DB and document reference
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_snapshot = MagicMock()
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = {"test": "test"}
        mock_doc_ref.get.return_value = mock_doc_snapshot
        
        # Setup chain of mock calls
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Test function
        result = get_document("test_collection", "test_doc_id")
        
        # Verify calls
        mock_get_db.assert_called_once()
        mock_db.collection.assert_called_once_with("test_collection")
        mock_collection.document.assert_called_once_with("test_doc_id")
        mock_doc_ref.get.assert_called_once()
        self.assertEqual(result, {"test": "test"})

    @patch('src.db.get_db')
    def test_get_document_not_exists(self, mock_get_db):
        # Setup mock DB and document reference
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_snapshot = MagicMock()
        mock_doc_snapshot.exists = False
        mock_doc_ref.get.return_value = mock_doc_snapshot
        
        # Setup chain of mock calls
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Test function
        result = get_document("test_collection", "test_doc_id")
        
        # Verify calls
        mock_get_db.assert_called_once()
        mock_db.collection.assert_called_once_with("test_collection")
        mock_collection.document.assert_called_once_with("test_doc_id")
        mock_doc_ref.get.assert_called_once()
        self.assertIsNone(result)

    @patch('src.db.get_db')
    def test_update_document(self, mock_get_db):
        # Setup mock DB and document reference
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        
        # Setup chain of mock calls
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Test function
        test_data = {"test": "test2"}
        update_document("test_collection", "test_doc_id", test_data)
        
        # Verify calls
        mock_get_db.assert_called_once()
        mock_db.collection.assert_called_once_with("test_collection")
        mock_collection.document.assert_called_once_with("test_doc_id")
        mock_doc_ref.update.assert_called_once_with(test_data)

    @patch('src.db.get_db')
    def test_delete_document(self, mock_get_db):
        # Setup mock DB and document reference
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        
        # Setup chain of mock calls
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        mock_db.collection.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Test function
        delete_document("test_collection", "test_doc_id")
        
        # Verify calls
        mock_get_db.assert_called_once()
        mock_db.collection.assert_called_once_with("test_collection")
        mock_collection.document.assert_called_once_with("test_doc_id")
        mock_doc_ref.delete.assert_called_once()

    @patch('src.db.get_db')
    def test_query_documents(self, mock_get_db):
        # Setup mock DB and query
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_where = MagicMock()
        mock_doc1 = MagicMock()
        mock_doc1.id = "doc1"
        mock_doc1.to_dict.return_value = {"field": "value1"}
        mock_doc2 = MagicMock()
        mock_doc2.id = "doc2"
        mock_doc2.to_dict.return_value = {"field": "value2"}
        
        # Setup chain of mock calls
        mock_collection = MagicMock()
        mock_where.stream.return_value = [mock_doc1, mock_doc2]
        mock_collection.where.return_value = mock_where
        mock_db.collection.return_value = mock_collection
        mock_get_db.return_value = mock_db
        
        # Test function
        results = query_documents("test_collection", "field", "==", "value")
        
        # Verify calls
        mock_get_db.assert_called_once()
        mock_db.collection.assert_called_once_with("test_collection")
        mock_collection.where.assert_called_once_with("field", "==", "value")
        mock_where.stream.assert_called_once()
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ("doc1", {"field": "value1"}))
        self.assertEqual(results[1], ("doc2", {"field": "value2"}))

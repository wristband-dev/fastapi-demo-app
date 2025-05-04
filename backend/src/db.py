from logging import Logger
from typing import Any
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.document import DocumentReference


from google.cloud.firestore_v1.stream_generator import StreamGenerator
from google.cloud.firestore_v1.transforms import Sentinel
from wristband.utils import get_logger

logger: Logger = get_logger()

# --------- DB INITIALIZATION ---------
def start_db() -> Client:
    try:
        # Check if default app already exists
        default_app = firebase_admin.get_app()
    except ValueError:
        # Initialize app only if it doesn't exist
        firebase_admin.initialize_app()
    
    db: Client = firestore.client()
    return db

def get_db() -> Client:
    return firestore.client()


def get_server_timestamp() -> Sentinel:
    return firestore.firestore.SERVER_TIMESTAMP


# --------- DOCUMENT MANIPULATION ---------
def add_document(
    collection_name: str, 
    data: dict
) -> str:
    """Add a document to a collection."""
    db: Client = get_db()
    doc_ref: DocumentReference = db.collection(collection_name).document()
    doc_ref.set(data)
    logger.info(f"Added document with ID: {doc_ref.id}")
    return doc_ref.id

def update_field(collection_name: str, doc_id: str, field: str, value: Any) -> dict | None:
    """Update a field in a document."""
    db: Client = get_db()
    doc_ref: DocumentReference = db.collection(collection_name).document(doc_id)

    if not doc_ref.get().exists:
        logger.error(f"Document {doc_id} does not exist!")
        return None
    
    doc_ref.update({field: value})
    logger.info(f"Document {doc_id} updated with: {field} = {value}")

    return doc_ref.get().to_dict()


def get_document(collection_name: str, doc_id: str) -> dict | None:
    """Get a document by ID."""
    db: Client = get_db()
    doc_ref = db.collection(collection_name).document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        logger.info(f"Document data: {doc.to_dict()}")
        return doc.to_dict()
    else:
        logger.error("Document does not exist!")
        return None

def update_document(collection_name: str, doc_id: str, data: dict) -> None:
    """Update a document with new data."""
    db: Client = get_db()
    doc_ref: DocumentReference = db.collection(collection_name).document(doc_id)
    if not doc_ref.get().exists:
        logger.error(f"Document {doc_id} does not exist!")
        return None
    doc_ref.update(data)
    logger.info(f"Document {doc_id} updated with: {data}")

def delete_document(collection_name: str, doc_id: str) -> None:
    """Delete a document."""
    db: Client = get_db()
    db.collection(collection_name).document(doc_id).delete()
    logger.info(f"Document {doc_id} deleted")

def query_documents(collection_name: str, field: str, operator: str, value: str) -> list[tuple[str, dict]]:
    """Query documents in a collection."""
    db: Client = get_db()
    docs: StreamGenerator[DocumentSnapshot] = db.collection(collection_name).where(field, operator, value).stream()
    results: list[tuple[str, dict]] = []
    for doc in docs:
        logger.info(f"Document ID: {doc.id}, Data: {doc.to_dict()}")
        results.append((doc.id, doc.to_dict()))
    return results
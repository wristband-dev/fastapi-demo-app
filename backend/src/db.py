from logging import Logger
from typing import Any
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference


from google.cloud.firestore_v1.stream_generator import StreamGenerator
from google.cloud.firestore_v1.transforms import Sentinel
from wristband.utils import get_logger
import os
from .config_utils import get_config_value
from urllib.parse import urlparse

logger: Logger = get_logger()

# --------- DB INITIALIZATION ---------

def start_db() -> Client:
    try:
        app = firebase_admin.get_app()
        logger.debug(f"Firebase app already initialized. Project ID: {app.project_id}")
    except ValueError: # No app initialized yet
        logger.debug("Firebase app not initialized. Proceeding with initialization.")
        
        try:
            project_id = get_config_value("database", "project_id")
            if not isinstance(project_id, str):
                err_msg = f"project_id '{project_id}' from config is not a string. Aborting initialization."
                logger.error(err_msg)
                raise ValueError(err_msg)
            logger.debug(f"Using mandatory project_id '{project_id}' from config.")
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Critical: Failed to load mandatory project_id from config: {e}. Aborting initialization.")
            raise

        options = {'projectId': project_id}
        
        # Try to get FIRESTORE_EMULATOR_HOST from environment first
        emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")

        if not emulator_host:
            # If not set in env, try to construct from config.yml for `npm start` compatibility
            logger.debug("FIRESTORE_EMULATOR_HOST not set in environment. Attempting to construct from config.yml.")
            try:
                app_host_from_config = get_config_value("app", "host") # e.g., "http://localhost"
                db_port_from_config = get_config_value("database", "port") # e.g., 6002
                
                parsed_url = urlparse(app_host_from_config)
                hostname = parsed_url.hostname # Extracts "localhost"
                
                if hostname and db_port_from_config:
                    constructed_emulator_host = f"{hostname}:{db_port_from_config}" # e.g., "localhost:6002"
                    os.environ["FIRESTORE_EMULATOR_HOST"] = constructed_emulator_host
                    emulator_host = constructed_emulator_host # Use this for the current run
                    logger.debug(f"Constructed and set FIRESTORE_EMULATOR_HOST to '{emulator_host}' from config.yml.")
                else:
                    logger.warning("Could not construct FIRESTORE_EMULATOR_HOST from config.yml (app.host or database.port missing or invalid).")
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Could not load app.host or database.port from config to construct FIRESTORE_EMULATOR_HOST: {e}. Proceeding without it.")
        
        # Now, emulator_host is either from original environment or constructed from config
        if emulator_host:
            logger.info(f"FIRESTORE_EMULATOR_HOST is '{emulator_host}'. Connecting to emulator using project ID '{project_id}'.")
            firebase_admin.initialize_app(options=options)
        else:
            logger.info(f"FIRESTORE_EMULATOR_HOST not set. Initializing Firebase for project ID '{project_id}' using Application Default Credentials.")
            try:
                cred_object = credentials.ApplicationDefault()
                firebase_admin.initialize_app(credential=cred_object, options=options)
            except Exception as e:
                logger.error(f"Critical: Failed to initialize Firebase with ADC for project '{project_id}': {e}. Aborting initialization.")
                raise
        
        initialized_app = firebase_admin.get_app()
        logger.debug(f"Firebase app initialization completed. Effective Project ID: {initialized_app.project_id}")
        
        if initialized_app.project_id != project_id:
             logger.warning(
                f"Initialized project ID '{initialized_app.project_id}' does not match configured project ID '{project_id}'. "
                f"This can happen if Application Default Credentials (ADC) are tied to a different project for non-emulator setups, or if FIRESTORE_EMULATOR_HOST implies a different project for the emulator."
             )
    
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

def query_documents(
        collection_name: str, 
        field: str | None = None, 
        operator: str | None = None, 
        value: str | None = None
    ) -> list[dict]:
    """Query documents in a collection."""
    db: Client = get_db()
    collection_ref = db.collection(collection_name)
    query = collection_ref

    if field and operator and value:
        query = collection_ref.where(field, operator, value)

    results: list[dict] = []

    for doc in query.stream():
        logger.info(f"Document ID: {doc.id}, Data: {doc.to_dict()}")
        results.append((doc.to_dict()))
    return results
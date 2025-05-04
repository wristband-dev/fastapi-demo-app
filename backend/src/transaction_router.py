# Standard library imports
import logging
from typing import Any, List, Dict, Optional
from fastapi import APIRouter, Request, Response, Body, HTTPException, Path
import uuid
from datetime import datetime
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.stream_generator import StreamGenerator
from nbformat import Sentinel
from pydantic import BaseModel, Field

# Wristband imports
from wristband.utils import get_logger

# Local imports
from src.db import add_document, get_document, get_server_timestamp, update_document, delete_document, get_db, update_field

# Configure logger
logger: logging.Logger = get_logger()

# Initialize router
router = APIRouter()

# Collection name for transactions
TRANSACTION_COLLECTION = "transactions"

# Models
class TransactionCreate(BaseModel):
    name: str
    amount: float
    date: str
    description: str = ""

class Transaction(BaseModel):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: str
    amount: float
    date: str
    description: str

class Transactions(BaseModel):
    transactions: List[Transaction] = Field(default_factory=list)

class DeleteResponse(BaseModel):
    message: str


@router.post("/", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate) -> Transaction:
    """Create a new transaction"""
    logger.debug(f"Creating transaction: {transaction}")
    
    # Create new transaction data
    new_transaction: Dict[str, Any] = transaction.model_dump()
    new_transaction["created_at"] = get_server_timestamp()
    new_transaction["updated_at"] = get_server_timestamp()
    
    # Add document to Firestore
    doc_id: str = add_document(TRANSACTION_COLLECTION, new_transaction)
    
    # add the id to the transaction
    doc_ref: dict | None = update_field(TRANSACTION_COLLECTION, doc_id, "id", doc_id)

    if doc_ref is None:
        raise HTTPException(status_code=500, detail="Failed to update transaction")

    return Transaction(**doc_ref)


@router.get("/", response_model=Transactions)
async def get_transactions() -> Transactions:
    """Get all transactions"""
    logger.debug("Getting all transactions")
    
    # Query all documents in the transactions collection
    db: Client = get_db()
    transactions_ref: StreamGenerator[DocumentSnapshot] = db.collection(TRANSACTION_COLLECTION).stream()
    transactions: List[Transaction] = []
    
    for doc in transactions_ref:
        transaction_data: Dict[str, Any] = doc.to_dict()
        transaction_data["id"] = doc.id  # Add document ID to the transaction
        transactions.append(Transaction(**transaction_data))
    
    return Transactions(transactions=transactions)


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str = Path(...)) -> Transaction:
    """Get a transaction by ID"""
    logger.debug(f"Getting transaction with ID: {transaction_id}")
    
    # Get the document from Firestore
    transaction: dict | None = get_document(TRANSACTION_COLLECTION, transaction_id)
    
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return Transaction(**transaction)


@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str = Path(...), transaction: TransactionCreate = Body(...)) -> Transaction:
    """Update a transaction by ID"""
    logger.debug(f"Updating transaction with ID: {transaction_id}")
    
    # Check if transaction exists
    existing_transaction: dict | None = get_document(TRANSACTION_COLLECTION, transaction_id)
    if existing_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Prepare data for update
    update_data: dict = transaction.model_dump()
    update_data["updated_at"] = get_server_timestamp()
    
    # Update the document in Firestore
    update_document(TRANSACTION_COLLECTION, transaction_id, update_data)
    
    # Return updated transaction
    # Merge existing data with updates
    result: dict = {**existing_transaction, **update_data, "id": transaction_id}
    return Transaction(**result)


@router.delete("/{transaction_id}", response_model=DeleteResponse)
async def delete_transaction(transaction_id: str = Path(...)) -> DeleteResponse:
    """Delete a transaction by ID"""
    logger.debug(f"Deleting transaction with ID: {transaction_id}")
    
    # Check if transaction exists
    existing_transaction: dict | None = get_document(TRANSACTION_COLLECTION, transaction_id)
    if existing_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Delete the document from Firestore
    delete_document(TRANSACTION_COLLECTION, transaction_id)
    
    return DeleteResponse(message="Transaction deleted successfully")
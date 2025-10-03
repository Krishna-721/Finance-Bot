from fastapi import Depends, status, APIRouter, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionSummary, TransactionUpdate
from app.models.transaction import TransactionType
from app.models.user import User
from app.services.transaction_service import TransactionService
from app.utils.dependencies import get_current_user

router=APIRouter(
    prefix='/transactions',
    tags=['Transactions']
)

@router.post('/', response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_data: TransactionCreate,
                       current_user: User=Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """Create a new transaction income/expense"""
    transaction=TransactionService.create_transaction(db,transaction_data, current_user)
    return transaction

@router.get('/', response_model=List[TransactionResponse])
def get_transactions(
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by type (income/expense)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
  transactions=TransactionService.get_user_transactions(db,current_user,category,skip,limit,transaction_type)
  return transactions

@router.get("/summary", response_model=TransactionSummary)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get financial summary for the authenticated user
    Returns total income, expenses, and net savings
    """
    summary = TransactionService.get_summary(db, current_user)
    return summary

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction based of a partcular user based on user_id"""
    transaction = TransactionService.get_transaction_by_id(db, transaction_id, current_user)
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a transaction
    Only some/provided fields will be updated
    """
    transaction = TransactionService.update_transaction(db, transaction_id, transaction_data, current_user)
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a transaction
    """
    TransactionService.delete_transaction(db, transaction_id, current_user)
    return None

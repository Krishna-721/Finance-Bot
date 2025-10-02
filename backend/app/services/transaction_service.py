from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionSummary

class TransactionService:
    @staticmethod
    def create_transaction(db: Session, transaction_data: Transaction, user: User) ->Transaction:
        """ New Transaction for the user"""
        new_transaction = Transaction(
            user_id=user.id,
            amount=transaction_data.amount,
            type=transaction_data.type,
            category=transaction_data.category,
            description=transaction_data.description,
            date=transaction_data.date
        )

        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction
    
    @staticmethod
    def get_user_transaction(db: Session, user=User ,transaction_type: Optional[TransactionType]=None,
                             category: Optional[str]=None,
                             skip: int=0,
                             limit: int=100)->List[Transaction]:
        """Input
        Get all transactions of a user
        """    
        if transaction_type:
            query=query.filter(Transaction.type==transaction_type)

        if category:
            query=query.filter(Transaction.category==category)
    
        query=query.order_by(Transaction.date.desc())
        transactions=query.offset(skip).limit(limit).all()

        return transactions
    
    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: int, user: User) -> Transaction:
        """
        Get a specific transaction by ID
        """
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id  # Security: Only user's own transactions
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
    
    @staticmethod
    def update_transaction(
        db: Session, 
        transaction_id: int, 
        transaction_data: TransactionUpdate,
        user: User) -> Transaction:
        """
        Update a transaction
        """
        # Get transaction (this checks ownership automatically)
        transaction = TransactionService.get_transaction_by_id(db, transaction_id, user)
        
        # Update only provided fields
        update_data = transaction_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(transaction, field, value)
        
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    @staticmethod
    def delete_transaction(db: Session, transaction_id: int, user: User) -> None:
        """
        Delete a transaction
        """
        transaction = TransactionService.get_transaction_by_id(db, transaction_id, user)
        
        db.delete(transaction)
        db.commit()
    
    @staticmethod
    def get_summary(db: Session, user: User) -> TransactionSummary:
        """
        Get financial summary for user
        """
        # Get total income
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.INCOME
        ).scalar() or 0.0
        
        # Get total expenses
        total_expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE
        ).scalar() or 0.0
        
        # Get transaction count
        transaction_count = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).count()
        
        return TransactionSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            net_savings=total_income - total_expenses,
            transaction_count=transaction_count
        )
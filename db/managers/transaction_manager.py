from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as saSession
from sqlalchemy import and_, extract
from datetime import date, datetime
from typing import List, Optional
from db.db import db_instance
from db.models.transaction import Transaction
from db.models.category import Category
from db.models.enums import TransactionType


class TransactionManager:
    def __init__(self):
        self.Session = db_instance.Session

    def add_transaction(self, 
                       transaction_type: TransactionType,
                       amount: float,
                       category_name: str,
                       vendor: str = None,
                       note: str = None,
                       transaction_date: date = None) -> Transaction:
        """Add a new transaction to the database"""
        session = self.Session()  # type: saSession
        try:
            # Find the category
            category = session.query(Category).filter_by(name=category_name).first()
            if not category:
                raise ValueError(f"Category '{category_name}' not found")
            
            # Create transaction directly
            transaction = Transaction(
                type=transaction_type,
                amount=amount,
                category_id=category.id,
                vendor=vendor,
                note=note,
                date=transaction_date or date.today()
            )
            
            session.add(transaction)
            session.commit()
            return transaction
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def list_transactions(self, limit: int = None) -> List[Transaction]:
        """Get all transactions, optionally limited"""
        session = self.Session()
        query = session.query(Transaction).order_by(Transaction.date.desc())
        
        if limit:
            query = query.limit(limit)
            
        transactions = query.all()
        session.close()
        return transactions

    def get_transactions_by_category(self, category_name: str) -> List[Transaction]:
        """Get all transactions for a specific category"""
        session = self.Session()
        try:
            transactions = (session.query(Transaction)
                          .join(Category)
                          .filter(Category.name == category_name)
                          .order_by(Transaction.date.desc())
                          .all())
            return transactions
        finally:
            session.close()

    def get_transactions_by_date_range(self, 
                                     start_date: date, 
                                     end_date: date) -> List[Transaction]:
        """Get transactions within a date range"""
        session = self.Session()
        try:
            transactions = (session.query(Transaction)
                          .filter(and_(
                              Transaction.date >= start_date,
                              Transaction.date <= end_date
                          ))
                          .order_by(Transaction.date.desc())
                          .all())
            return transactions
        finally:
            session.close()

    def get_transactions_by_month(self, year: int, month: int) -> List[Transaction]:
        """Get transactions for a specific month"""
        session = self.Session()
        try:
            transactions = (session.query(Transaction)
                          .filter(and_(
                              extract('year', Transaction.date) == year,
                              extract('month', Transaction.date) == month
                          ))
                          .order_by(Transaction.date.desc())
                          .all())
            return transactions
        finally:
            session.close()

    def update_transaction(self, 
                          transaction_id: int,
                          **kwargs) -> Transaction:
        """Update a transaction with new values"""
        session = self.Session()
        try:
            transaction = session.query(Transaction).filter_by(id=transaction_id).first()
            if not transaction:
                raise ValueError(f"Transaction with id {transaction_id} not found")
            
            # Update allowed fields
            allowed_fields = ['amount', 'vendor', 'note', 'date', 'category_id']
            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    setattr(transaction, key, value)
            
            session.commit()
            return transaction
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by ID"""
        session = self.Session()
        try:
            transaction = session.query(Transaction).filter_by(id=transaction_id).first()
            if not transaction:
                return False
            
            session.delete(transaction)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_spending_summary_by_category(self, 
                                       start_date: date = None, 
                                       end_date: date = None) -> dict:
        """Get spending summary grouped by category"""
        session = self.Session()
        try:
            query = (session.query(Category.name, 
                                 session.query(Transaction.amount)
                                 .filter(Transaction.category_id == Category.id)
                                 .filter(Transaction.type == TransactionType.EXPENSE))
                    .outerjoin(Transaction))
            
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)
            
            # This is a simplified version - you might want to use SQL aggregation
            summary = {}
            for category_name, in session.query(Category.name).all():
                expense_total = (session.query(Transaction.amount)
                               .join(Category)
                               .filter(Category.name == category_name)
                               .filter(Transaction.type == TransactionType.EXPENSE))
                
                if start_date:
                    expense_total = expense_total.filter(Transaction.date >= start_date)
                if end_date:
                    expense_total = expense_total.filter(Transaction.date <= end_date)
                
                total = sum(t.amount for t in expense_total.all())
                if total > 0:
                    summary[category_name] = total
            
            return summary
        finally:
            session.close()
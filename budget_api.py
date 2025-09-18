from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from db.managers.category_manager import CategoryManager
from db.managers.transaction_manager import TransactionManager
from db.models.enums import TransactionType
from db.models.transaction import Transaction
from db.models.category import Category


class BudgetAPI:
    """Unified API for all budget-related database operations"""
    
    def __init__(self):
        self.category_manager = CategoryManager()
        self.transaction_manager = TransactionManager()
    
    # ===== CATEGORY OPERATIONS =====
    
    def create_category(self, name: str, limit: float = 0, parent: str = None) -> Category:
        """Create a new category"""
        return self.category_manager.add_category(name, limit, parent)
    
    def get_categories(self) -> List[Category]:
        """Get all categories"""
        return self.category_manager.list_categories()
    
    def get_category(self, name: str = None, category_id: int = None) -> Optional[Category]:
        """Get a category by name or ID"""
        if name:
            return self.category_manager.get_category_by_name(name)
        elif category_id:
            return self.category_manager.get_category_by_id(category_id)
        else:
            raise ValueError("Must provide either name or category_id")
    
    def update_category(self, category_id: int, **kwargs) -> Category:
        """Update a category"""
        return self.category_manager.update_category(category_id, **kwargs)
    
    def delete_category(self, category_id: int, force: bool = False) -> bool:
        """Delete a category"""
        return self.category_manager.delete_category(category_id, force)
    
    def get_category_hierarchy(self) -> Dict:
        """Get categories in hierarchical structure"""
        return self.category_manager.get_category_hierarchy()
    
    # ===== TRANSACTION OPERATIONS =====
    
    def add_transaction(self, 
                       transaction_type: str,
                       amount: float,
                       category: str,
                       vendor: str = None,
                       note: str = None,
                       transaction_date: str = None) -> Transaction:
        """Add a new transaction using string parameters"""
        # Convert string type to enum
        tx_type = TransactionType.INCOME if transaction_type.lower() == 'income' else TransactionType.EXPENSE
        
        # Parse date if provided
        parsed_date = None
        if transaction_date:
            try:
                parsed_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        
        return self.transaction_manager.add_transaction(
            tx_type, amount, category, vendor, note, parsed_date
        )
    
    def get_transactions(self, 
                        limit: int = None,
                        category: str = None,
                        start_date: str = None,
                        end_date: str = None,
                        month: str = None) -> List[Transaction]:
        """Get transactions with various filters"""
        
        if month:
            # Parse month format "YYYY-MM"
            try:
                year, month_num = map(int, month.split('-'))
                return self.transaction_manager.get_transactions_by_month(year, month_num)
            except ValueError:
                raise ValueError("Month must be in YYYY-MM format")
        
        if category:
            return self.transaction_manager.get_transactions_by_category(category)
        
        if start_date or end_date:
            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else date.min
            end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else date.max
            return self.transaction_manager.get_transactions_by_date_range(start, end)
        
        return self.transaction_manager.list_transactions(limit)
    
    def update_transaction(self, transaction_id: int, **kwargs) -> Transaction:
        """Update a transaction"""
        return self.transaction_manager.update_transaction(transaction_id, **kwargs)
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        return self.transaction_manager.delete_transaction(transaction_id)
    
    # ===== REPORTING & ANALYSIS =====
    
    def get_budget_summary(self, month: str = None) -> Dict:
        """Get comprehensive budget summary"""
        # Parse month if provided
        start_date, end_date = None, None
        if month:
            try:
                year, month_num = map(int, month.split('-'))
                start_date = date(year, month_num, 1)
                # Get last day of month
                if month_num == 12:
                    end_date = date(year + 1, 1, 1)
                else:
                    end_date = date(year, month_num + 1, 1)
            except ValueError:
                raise ValueError("Month must be in YYYY-MM format")
        
        # Get category spending summary
        category_summary = self.category_manager.get_category_spending_summary(
            start_date=start_date, end_date=end_date
        )
        
        # Get total income and expenses
        transactions = self.get_transactions(
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None
        )
        
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        
        # Calculate budget health
        categories_over_budget = [name for name, data in category_summary.items() if data['over_budget']]
        total_budget_limits = sum(data['limit'] for data in category_summary.values() if data['limit'] > 0)
        
        return {
            'period': month or 'all_time',
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_amount': total_income - total_expenses,
            'total_budget_limits': total_budget_limits,
            'budget_utilization': (total_expenses / total_budget_limits * 100) if total_budget_limits > 0 else None,
            'categories_over_budget': categories_over_budget,
            'category_breakdown': category_summary,
            'transaction_count': len(transactions)
        }
    
    def get_spending_trends(self, months: int = 6) -> Dict:
        """Get spending trends over the last N months"""
        trends = {}
        current_date = date.today()
        
        for i in range(months):
            # Calculate month
            month_date = date(current_date.year, current_date.month - i, 1) if current_date.month - i > 0 else date(current_date.year - 1, 12 - (i - current_date.month), 1)
            month_str = month_date.strftime('%Y-%m')
            
            # Get transactions for this month
            transactions = self.transaction_manager.get_transactions_by_month(month_date.year, month_date.month)
            
            total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
            total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
            
            trends[month_str] = {
                'income': total_income,
                'expenses': total_expenses,
                'net': total_income - total_expenses,
                'transaction_count': len(transactions)
            }
        
        return trends
    
    # ===== UTILITY METHODS =====
    
    def validate_category_exists(self, category_name: str) -> bool:
        """Check if a category exists"""
        return self.get_category(name=category_name) is not None
    
    def get_quick_stats(self) -> Dict:
        """Get quick overview stats"""
        categories = self.get_categories()
        transactions = self.get_transactions(limit=1000)  # Last 1000 transactions
        
        return {
            'total_categories': len(categories),
            'total_transactions': len(transactions),
            'categories_with_limits': len([c for c in categories if c.limit_amount > 0]),
            'recent_transaction_count': len([t for t in transactions if t.date >= date.today().replace(day=1)]),  # This month
        }
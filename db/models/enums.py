from pathlib import Path
from enum import Enum as PyEnum
import enum

class DBFile(PyEnum):
    MAIN = Path("budget.db")
    TEST = Path("budget_test.db")

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

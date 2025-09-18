
from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from base import Base
from enums import TransactionType
from dataclasses import dataclass


@dataclass
class TransactionObj:
    id: int = None
    type: TransactionType
    amount: float = 0
    category_id: int = None
    vendor: str
    note: str
    
class Transaction(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="transactions")
    vendor = Column(String, nullable=True)
    note = Column(String, nullable=True)
    date = Column(Date, default = date.today)
    


from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    limit_amount = Column(Float, default=0)
    transactions = relationship("Transaction", back_populates="category")
    
    # self-referential parent-child relationship
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    subcategories = relationship("Category", backref=backref('parent', remote_side=[id]))
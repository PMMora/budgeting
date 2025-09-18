from sqlalchemy.exc import IntegrityError
from db.db import db_instance
from db.models.category import CategoryObj, Category
from sqlalchemy.orm import Session as saSession

class CategoryManager:
    def __init__(self):
        self.Session = db_instance.Session

    def add_category(self, name: str, limit_amount: float = 0, parent_name: str = None):
        session = self.Session() # type: saSession
        try:
            parent = None
            if parent_name:
                parent = session.query(Category).filter_by(name=parent_name).first()
                if not parent:
                    raise ValueError(f"Parent category '{parent_name}' not found")
            category = Category(name=name, limit_amount=limit_amount,parent=parent)
            session.add(category)
            session.commit()
            return category
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Category '{name}' already exists")
        finally:
            session.close()

    def update_category(self, category: CategoryObj):
        return
    
    def list_categories(self):
        session = self.Session()
        categories = session.query(Category).all()
        session.close()
        return categories


from typing import List
from sqlalchemy.exc import IntegrityError
from db.db import db_instance
from db.models.category import Category
from sqlalchemy.orm import Session as saSession

class CategoryManager:
    def __init__(self):
        self.Session = db_instance.Session

    def add_category(self, name: str, limit_amount: float = 0, parent_name: str = None) -> Category:
        session = self.Session() # type: saSession
        try:
            parent = None
            if parent_name:
                parent = session.query(Category).filter_by(name=parent_name).first()
                if not parent:
                    raise ValueError(f"Parent category '{parent_name}' not found")
            category = Category(name=name, limit_amount=limit_amount, parent=parent)
            session.add(category)
            session.commit()
            return category
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Category '{name}' already exists")
        finally:
            session.close()

    def update_category(self, **kwargs) -> Category:
        session = self.Session()
        try:
            category_id = kwargs.pop('category_id', None)
            category_name = kwargs.pop('category_name', None)

            if not category_id and not category_name:
                raise ValueError("Must provide category_id or category_name")
            
            if category_id:
                category = session.query(Category).filter_by(id=category_id).first()
                if not category:
                    raise ValueError(f"Category with id: {category_id} not found")
            else:
                category = session.query(Category).filter_by(name=category_name).first()
                if not category:
                    raise ValueError(f"Category with name: {category_name} not found")
            
            allowed_fields = ["name", "parent", "limit_amount"]
            updated_fields = []

            for k,v in kwargs.items():
                if k in allowed_fields and v is not None:
                    setattr(category, k, v)
                    updated_fields.append(k)
                elif k not in allowed_fields:
                    raise ValueError(f"Key of {k} not in allowed_fields, update name, parent, or limit_amount")

            if not updated_fields:
                raise ValueError(f"no valid fields provided for update")
            
            session.commit()
            return category
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Category name must be unique")
        except Exception as e:
            session.rollback()
            return e
        finally:
            session.close()
    
    def list_categories(self) -> List[Category]:
        session = self.Session()
        categories = session.query(Category).all()
        session.close()
        return categories


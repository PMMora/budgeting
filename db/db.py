from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.enums import DBFile

class DB:
    def __init__(self, db_file: DBFile = DBFile.MAIN):
        self.engine = create_engine(f"sqlite:///{db_file.value}", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

db_instance = DB()  # Singleton instance

"""
Database handler untuk ArisDev Framework
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class Database:
    """Database handler untuk ArisDev Framework"""
    
    def __init__(self, url="sqlite:///database.db"):
        """Inisialisasi database
        
        Args:
            url (str): Database URL
        """
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.Session()
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()

class Model(Base):
    """Base model untuk ArisDev Framework"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def to_json(self):
        """Convert model to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data):
        """Create model from dictionary
        
        Args:
            data (dict): Model data
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str):
        """Create model from JSON
        
        Args:
            json_str (str): JSON string
        """
        return cls.from_dict(json.loads(json_str))
    
    def save(self, session):
        """Save model to database
        
        Args:
            session: Database session
        """
        session.add(self)
        session.commit()
        return self
    
    def delete(self, session):
        """Delete model from database
        
        Args:
            session: Database session
        """
        session.delete(self)
        session.commit()
    
    @classmethod
    def get_by_id(cls, session, id):
        """Get model by ID
        
        Args:
            session: Database session
            id: Model ID
        """
        return session.query(cls).get(id)
    
    @classmethod
    def get_all(cls, session):
        """Get all models
        
        Args:
            session: Database session
        """
        return session.query(cls).all()
    
    @classmethod
    def filter_by(cls, session, **kwargs):
        """Filter models by attributes
        
        Args:
            session: Database session
            **kwargs: Filter attributes
        """
        return session.query(cls).filter_by(**kwargs)
    
    @classmethod
    def create(cls, session, **kwargs):
        """Create new model
        
        Args:
            session: Database session
            **kwargs: Model attributes
        """
        model = cls(**kwargs)
        return model.save(session)
    
    @classmethod
    def update(cls, session, id, **kwargs):
        """Update model
        
        Args:
            session: Database session
            id: Model ID
            **kwargs: Model attributes
        """
        model = cls.get_by_id(session, id)
        if model:
            for key, value in kwargs.items():
                setattr(model, key, value)
            return model.save(session)
        return None
    
    @classmethod
    def delete_by_id(cls, session, id):
        """Delete model by ID
        
        Args:
            session: Database session
            id: Model ID
        """
        model = cls.get_by_id(session, id)
        if model:
            model.delete(session)
            return True
        return False 
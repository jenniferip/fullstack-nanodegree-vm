"""
This file contains all of the code needed to setup the database,
itemcatalog.db, needed to support the backend of the catalog web application.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
        }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'title': self.title,
            'id': self.id,
            'description': self.description,
            'category_id': self.category_id,
            'time_created': self.time_created
        }


engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    auth = relationship('Auth', back_populates='user')

class Auth(Base):
    __tablename__ = 'auths'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    email = Column(String)
    email_verified_at = Column(DateTime)
    user = relationship('User', back_populates='auth')



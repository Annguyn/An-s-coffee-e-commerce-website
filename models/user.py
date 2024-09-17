from models.Base import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    telephone = Column(String(20))
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
class UserAddress(Base):
    __tablename__ = 'user_address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    telephone = Column(String(20))
    mobile = Column(String(20))

    user = relationship('User', backref='addresses')
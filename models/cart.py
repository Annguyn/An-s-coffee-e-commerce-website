from models.Base import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ShoppingSession(Base):
    __tablename__ = 'shopping_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    total = Column(Float)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    user = relationship('User', backref='shopping_sessions')


class CartItem(Base):
    __tablename__ = 'cart_item'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('shopping_session.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    session = relationship('ShoppingSession', backref='cart_items')
    product = relationship('Product', backref='cart_items')
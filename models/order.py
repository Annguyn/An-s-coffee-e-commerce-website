from models.Base import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class OrderDetails(Base):
    __tablename__ = 'order_details'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    total = Column(Float)
    payment_id = Column(Integer, ForeignKey('user_payment.id'))
    shipping_address_id = Column(Integer, ForeignKey('user_address.id'))
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    user = relationship('User', backref='orders')
    payment = relationship('UserPayment', backref='order_details')
    shipping_address = relationship('UserAddress', backref='orders')


class OrderItems(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order_details.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    order = relationship('OrderDetails', backref='order_items')
    product = relationship('Product', backref='order_items')
from models.Base import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship

class UserPayment(Base):
    __tablename__ = 'user_payment'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    payment_type = Column(String(100), nullable=False)  # e.g., 'Credit Card', 'Paypal'
    provider = Column(String(255), nullable=False)      # e.g., 'Visa', 'MasterCard'
    account_no = Column(String(100), nullable=False)
    expiry = Column(Date)  # Expiry date for card

    user = relationship('User', backref='payments')

class PaymentDetails(Base):
    __tablename__ = 'payment_details'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order_details.id'))
    amount = Column(Float, nullable=False)
    provider = Column(String(255), nullable=False)  # e.g., 'Visa', 'Paypal'
    status = Column(String(100), nullable=False)  # e.g., 'Completed', 'Pending'
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    order = relationship('OrderDetails', backref='payment_details')
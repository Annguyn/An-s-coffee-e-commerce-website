from models.Base import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Discount(Base):
    __tablename__ = 'discount'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    desc = Column(Text)
    discount_percent = Column(Float)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    deleted_at = Column(DateTime)

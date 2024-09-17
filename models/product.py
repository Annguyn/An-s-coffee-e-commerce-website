from models.Base import Base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ProductCategory(Base):
    __tablename__ = 'product_category'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    desc = Column(Text)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    deleted_at = Column(DateTime)

class ProductInventory(Base):
    __tablename__ = 'product_inventory'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    deleted_at = Column(DateTime)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    desc = Column(Text)
    SKU = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey('product_category.id'))
    inventory_id = Column(Integer, ForeignKey('product_inventory.id'))
    price = Column(Float, nullable=False)
    discount_id = Column(Integer, ForeignKey('discount.id'))
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    deleted_at = Column(DateTime)

    category = relationship('ProductCategory', backref='products')
    inventory = relationship('ProductInventory', backref='products')
    discount = relationship('Discount', backref='products')
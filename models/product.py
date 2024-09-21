from extensions import db

class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.Text)
    image = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

class ProductInventory(db.Model):
    __tablename__ = 'product_inventory'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.Text)
    SKU = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('product_inventory.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_id = db.Column(db.Integer, db.ForeignKey('discount.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    image = db.Column(db.LargeBinary)
    category = db.relationship('ProductCategory', backref='products')
    inventory = db.relationship('ProductInventory', backref='products')
    discount = db.relationship('Discount', backref='products')

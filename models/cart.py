from extensions import db  # Import db từ Flask-SQLAlchemy

class ShoppingSession(db.Model):  # Thay vì Base
    __tablename__ = 'shopping_session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    shipping_fee = db.Column(db.Float, nullable=False, default=0.0)
    total_before_discount = db.Column(db.Integer, nullable=True, default=0.0)
    applied_coupons = db.Column(db.String, nullable=True)

    user = db.relationship('User', backref='shopping_sessions')


class CartItem(db.Model):  # Thay vì Base
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('shopping_session.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    session = db.relationship('ShoppingSession', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')

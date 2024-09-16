from models.db import db
class ShoppingSession(db.Model):
    __tablename__ = 'shopping_session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='shopping_sessions')


class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('shopping_session.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    session = db.relationship('ShoppingSession', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')

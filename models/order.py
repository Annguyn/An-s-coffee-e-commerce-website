from extensions import db  # Import db từ Flask-SQLAlchemy

class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)
    payment_id = db.Column(db.Integer, db.ForeignKey('user_payment.id'))
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('user_address.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='orders')
    payment = db.relationship('UserPayment', backref='order_details')
    shipping_address = db.relationship('UserAddress', backref='orders')


class OrderItems(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_details.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    order = db.relationship('OrderDetails', backref='order_items')
    product = db.relationship('Product', backref='order_items')

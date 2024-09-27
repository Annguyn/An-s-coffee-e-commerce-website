from extensions import db

class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='orders')
    payment_method = db.relationship('PaymentMethod', backref='order_details')

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
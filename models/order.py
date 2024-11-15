from extensions import db


class ShippingMethod(db.Model):
    __tablename__ = 'shipping_method'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)

class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    billing_id = db.Column(db.Integer, db.ForeignKey('billing_information.id'))
    transaction_id = db.Column(db.String(100), nullable=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment_details.id'))

    payment = db.relationship('PaymentDetails', backref='order')
    billing = db.relationship('BillingInformation', backref='order')
    user = db.relationship('User', backref='orders')


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
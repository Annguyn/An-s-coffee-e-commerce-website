from sqlalchemy import Date

from extensions import db  # Import db from Flask-SQLAlchemy

class UserPayment(db.Model):
    __tablename__ = 'user_payment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_type = db.Column(db.String(100), nullable=False)  # e.g., 'Credit Card', 'Paypal'
    provider = db.Column(db.String(255), nullable=False)      # e.g., 'Visa', 'MasterCard'
    account_no = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.Date)  # Expiry date for card

    user = db.relationship('User', backref='payments')

class PaymentDetails(db.Model):
    __tablename__ = 'payment_details'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_details.id'))
    amount = db.Column(db.Float, nullable=False)
    provider = db.Column(db.String(255), nullable=False)  # e.g., 'Visa', 'Paypal'
    status = db.Column(db.String(100), nullable=False)  # e.g., 'Completed', 'Pending'
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    order = db.relationship('OrderDetails', backref='payment_details')
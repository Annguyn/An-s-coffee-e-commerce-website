from sqlalchemy import Date

from extensions import db

class BillingInformation(db.Model):
    __tablename__ = 'billing_information'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    first_name = db.Column(db.Unicode(255))
    last_name = db.Column(db.Unicode(255))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    shipping_method_id = db.Column(db.Integer, db.ForeignKey('shipping_method.id'))
    city = db.Column(db.String(255))
    shipping_fee = db.Column(db.Float, nullable=True, default=0)
    district = db.Column(db.String(255))
    ward = db.Column(db.String(255))
    telephone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='billing_info')


class PaymentDetails(db.Model):
    __tablename__ = 'payment_details'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    provider = db.Column(db.String(255), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    zp_trans_id = db.Column(db.String(100), nullable=True)


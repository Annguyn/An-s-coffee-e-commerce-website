from extensions import db
from datetime import datetime

class Coupon(db.Model):
    __tablename__ = 'coupon'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    min_payment = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'), nullable=False)
    percent = db.Column(db.Float, nullable=False)
    max = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)

    category = db.relationship('ProductCategory', backref='coupons')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'min_payment': self.min_payment,
            'category_id': self.category_id,
            'percent': self.percent,
            'max': self.max,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
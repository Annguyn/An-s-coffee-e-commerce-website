from extensions import db  # Import db từ Flask-SQLAlchemy

class Discount(db.Model):  # Thay vì Base
    __tablename__ = 'discount'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.Text)
    discount_percent = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

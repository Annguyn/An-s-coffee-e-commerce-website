from extensions import db  # sử dụng SQLAlchemy từ Flask

class User(db.Model):  # Thay vì Base
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Unicode(255))  # Support Vietnamese characters
    last_name = db.Column(db.Unicode(255))
    telephone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

class UserAddress(db.Model):  # Thay vì Base
    __tablename__ = 'user_address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))

    user = db.relationship('User', backref='addresses')

# models/user.py
from extensions import db  # sử dụng SQLAlchemy từ Flask
from flask_security import UserMixin, RoleMixin
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# Define the Role model
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

# Define the User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.Unicode(255))  # Support Vietnamese characters
    last_name = db.Column(db.Unicode(255))
    telephone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)  # Add the 'active' field
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Define the relationship to Role via a secondary table
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    # Define the set_password method to hash the password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Define the verify_password method to check if passwords match
    def verify_password(self, password):
        return check_password_hash(self.password, password)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))

class UserAddress(db.Model):
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
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from livereload import Server
from sqlalchemy import create_engine
from models.discount import Discount
from models.product import Product, ProductCategory, ProductInventory
from models.cart import ShoppingSession, CartItem
from models.user import User
from models.order import OrderDetails, OrderItems
from models.payment import PaymentDetails
from routes.cart import add_to_cart_bp
from routes.chat import chat_bp
from routes.favourie import favourite_bp
from routes.index import index_bp
from routes.account import account_bp
from extensions import db
from os import path, getcwd
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_security import current_user
from routes.billing_information import billing_information_bp
import os
from filters import b64encode
from routes.add_to_favourite import add_to_favourite_bp
from routes.cart import add_to_cart_bp
from routes.order import order_bp
from routes.payment import payment_bp
from routes.product import product_bp
from routes.shipping import shipping_bp
from routes.shop import shop_bp
from flask_login import LoginManager

from routes.styleguide import styleguide_bp
from routes.verify import verify_bp

app = Flask(__name__)
mail = Mail(app)
app.jinja_env.filters['b64encode'] = b64encode
app.config['SECRET_KEY'] = "annguyen"
dir = path.abspath(getcwd())
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jobhuntly@gmail.com'
app.config['MAIL_PASSWORD'] = 'swvk rsqn xvsx vbgr'


app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dir}/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_LOGIN_URL'] = '/account'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/account'

mail.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'account_bp.sign_in'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db.init_app(app)
# Create engine and session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
# session = Session()

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'account.sign_in'
login_manager.login_message = 'Please log in to access this page.'

app.register_blueprint(verify_bp)
app.register_blueprint(styleguide_bp)
app.register_blueprint(order_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(product_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(shipping_bp)
app.register_blueprint(billing_information_bp)
app.register_blueprint(favourite_bp)
app.register_blueprint(add_to_cart_bp)
app.register_blueprint(add_to_favourite_bp)
app.register_blueprint(account_bp)
app.register_blueprint(index_bp)
app.register_blueprint(shop_bp)

# Create tables
with app.app_context():
    db.create_all()
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')
    server.serve(debug=True)

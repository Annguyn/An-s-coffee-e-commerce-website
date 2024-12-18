import secrets
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from flask import Flask, render_template, session, url_for, flash, redirect, request, jsonify
from flask_login import LoginManager, login_user
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from langchain import requests
from services.get_image import train_model, model_exists, get_images_and_labels
from livereload import Server
from sqlalchemy import create_engine
from models.product import Product, ProductCategory, ProductInventory
from models.cart import ShoppingSession, CartItem
from models.user import User
from models.order import OrderDetails, OrderItems
from models.payment import PaymentDetails
from routes.account import account_bp
from routes.admin import admin_bp
from routes.cart import add_to_cart_bp
from routes.chat import chat_bp
from routes.deliver import deliver_bp
from routes.favourie import favourite_bp
from routes.index import index_bp
from extensions import db
from os import path, getcwd
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_security import current_user
from routes.billing_information import billing_information_bp
import os
from filters import b64encode
from routes.add_to_favourite import add_to_favourite_bp
from routes.cart import add_to_cart_bp
from routes.order import order_bp
from routes.payment import payment_bp
from routes.product import product_bp
from routes.refund import refund_bp
from routes.shipping import shipping_bp
from routes.shop import shop_bp
from flask_login import LoginManager
from routes.statistics import statistics_bp
from routes.verify import verify_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
mail = Mail(app)
oauth = OAuth(app)

google = oauth.register(
    'google',
    client_id=os.getenv('GOOGLE_ID'),
    client_secret=os.getenv('GOOGLE_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://127.0.0.1:5000/login/google/authorized',
    client_kwargs={
        'scope': 'email profile',
        'token_endpoint_auth_method': 'client_secret_basic',
    }
)
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    userinfo_endpoint='https://api.github.com/user',
    client_kwargs={'scope': 'user:email'},
)
facebook = oauth.register(
    name='facebook',
    client_id=os.getenv('FACEBOOK_CLIENT_ID'),
    client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
    authorize_url='https://www.facebook.com/v10.0/dialog/oauth',
    authorize_params=None,
    access_token_url='https://graph.facebook.com/v10.0/oauth/access_token',
    access_token_params=None,
    userinfo_endpoint='https://graph.facebook.com/me?fields=id,name,email',
    client_kwargs={'scope': 'email'},
    redirect_uri=os.getenv('FACEBOOK_REDIRECT_URI')
)
@app.route('/login/github')
def login_github():
    redirect_uri = url_for('github_authorized', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/login/github/authorized')
def github_authorized():
    token = github.authorize_access_token()
    if not token:
        flash('Failed to log in with GitHub', 'danger')
        return redirect(url_for('login'))

    user_info = github.get('https://api.github.com/user').json()
    if not user_info:
        flash('Failed to fetch user info', 'danger')
        return redirect(url_for('login'))

    username = user_info.get('login')
    name = user_info.get('name', '')

    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(
            username=username,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if name else '',
            created_at=datetime.now(),
            modified_at=datetime.now(),
            is_admin=False,
            active=True,
            roles=[]
        )
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('You were successfully logged in with GitHub.', 'success')
    return redirect(url_for('index.home'))

@app.route('/login/google')
def login_google():
    nonce = secrets.token_urlsafe()
    session['nonce'] = nonce
    redirect_uri = url_for('account.google_authorized', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@app.route('/login/google/authorized')
def google_authorized():
    token = google.authorize_access_token()
    if not token:
        flash('Failed to log in with Google', 'danger')
        return redirect(url_for('account.sign_in'))

    nonce = session.pop('nonce', None)
    user_info = google.parse_id_token(token, nonce=nonce)
    if not user_info:
        flash('Failed to fetch user info', 'danger')
        return redirect(url_for('account.sign_in'))

    email = user_info.get('email')
    given_name = user_info.get('given_name', '')
    family_name = user_info.get('family_name', '')

    user = User.query.filter_by(username=email).first()
    if user is None:
        user = User(
            username=email,
            first_name=given_name,
            last_name=family_name,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            is_admin=False,
            active=True,
            roles=[]
        )
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('You were successfully logged in with Google.', 'success')
    return redirect(url_for('index.home'))
@app.route('/login/facebook')
def login_facebook():
    redirect_uri = url_for('account.facebook_authorized', _external=True)
    return facebook.authorize_redirect(redirect_uri)

@app.route('/login/facebook/authorized')
def facebook_authorized():
    token = facebook.authorize_access_token()
    if not token:
        flash('Failed to log in with Facebook', 'danger')
        return redirect(url_for('account.sign_in'))

    user_info = facebook.get('https://graph.facebook.com/me?fields=id,name,email').json()
    if not user_info:
        flash('Failed to fetch user info', 'danger')
        return redirect(url_for('account.sign_in'))

    email = user_info.get('email')
    name = user_info.get('name', '')

    user = User.query.filter_by(username=email).first()
    if user is None:
        user = User(
            username=email,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if name else '',
            created_at=datetime.now(),
            modified_at=datetime.now(),
            is_admin=False,
            active=True,
            roles=[]
        )
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('You were successfully logged in with Facebook.', 'success')
    return redirect(url_for('index.home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html' ), 404

app.jinja_env.filters['b64encode'] = b64encode
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
dir = path.abspath(getcwd())
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dir}/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_LOGIN_URL'] = '/account'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/account'
SECURITY_PASSWORD_HASH = 'pbkdf2_sha256'

mail.init_app(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'account_bp.sign_in'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create engine and session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

oauth.init_app(app)
app.register_blueprint(verify_bp)
app.register_blueprint(order_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(product_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(shipping_bp)
app.register_blueprint(billing_information_bp)
app.register_blueprint(favourite_bp)
app.register_blueprint(add_to_cart_bp)
app.register_blueprint(add_to_favourite_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(account_bp)
app.register_blueprint(index_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(deliver_bp)
app.register_blueprint(refund_bp)
app.register_blueprint(statistics_bp)
with app.app_context():
    db.create_all()

user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore)
with app.app_context():
    data = get_images_and_labels()
with app.app_context():
    if not model_exists():
        train_model()
@app.route('/style')
def style():
    return render_template('styleguide.html')
@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')
    server.serve(debug=True)
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from livereload import Server
from sqlalchemy import create_engine
from models.discount import Discount
from models.product import Product, ProductCategory, ProductInventory
from models.cart import ShoppingSession, CartItem
from models.user import User, UserAddress
from models.order import OrderDetails, OrderItems
from models.payment import UserPayment, PaymentDetails
from routes.account import account_bp
from extensions import db
from os import path, getcwd
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "annguyen"
dir = path.abspath(getcwd())
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dir}/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create engine and session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
# session = Session()

app.register_blueprint(account_bp)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')
    server.serve(debug=True)
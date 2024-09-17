from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from livereload import Server
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.discount import Discount
from models.product import Product, ProductCategory, ProductInventory
from models.cart import ShoppingSession, CartItem
from models.user import User, UserAddress
from models.order import OrderDetails, OrderItems
from models.payment import UserPayment, PaymentDetails

from os import path
app = Flask(__name__)
app.config['SECRET_KEY'] = "annguyen"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Create engine and session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
session = Session()

# Create tables
db.metadata.create_all(engine)

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    if not path.exists('database.db'):
        db.create_all(app)
        print('Database created')
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')
    server.serve(debug=True)
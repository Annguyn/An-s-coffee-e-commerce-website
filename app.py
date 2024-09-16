from flask import Flask, render_template
from flask_migrate import Migrate
from livereload import Server
from models.db import db
from routes.account import account_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize SQLAlchemy and Migrate
db.init_app(app)
migrate = Migrate(app, db)


# Import models to ensure they are registered with SQLAlchemy
from models.discount import Discount
# Import other models similarly
# from models.cart import CartItem, ShoppingSession
# from models.order import OrderItems, OrderDetails
# from models.payment import UserPayment, PaymentDetails
# from models.product import Product, ProductCategory, ProductInventory
# from models.user import User, UserAddress

app.register_blueprint(account_bp)

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/*.html')
    server.serve(debug=True)

from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
# from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
csrf = CSRFProtect()

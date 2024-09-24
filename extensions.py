from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

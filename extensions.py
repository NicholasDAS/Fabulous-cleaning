
# extensions.py - Initializes extensions for the entire app

from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Database object
db = SQLAlchemy()

# Email system
mail = Mail()

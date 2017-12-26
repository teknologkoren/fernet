import os


# flask
SECRET_KEY = 'super secret string'
TEMPLATES_AUTO_RELOAD = True
SERVER_NAME = 'localhost:5001'
BASEDIR = os.path.abspath(os.path.dirname(__file__))


# teknologkoren-se api
# schema (http/https) is important, requests need it
TEKNOLOGKORENSE_API_URL = 'http://localhost:5000/api'
TEKNOLOGKORENSE_API_USERNAME = 'fernet'
TEKNOLOGKORENSE_API_PASSWORD = 'very secure password'


# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'db.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False


# Flask-Uploads
UPLOADS_DEFAULT_DEST = 'fernet/static/uploads/'
UPLOADS_DEFAULT_URL = 'http://localhost:5001/static/uploads/'


# Email settings
SMTP_MAILSERVER = 'smtp.example.com'
SMTP_STARTTLS_PORT = 587
SMTP_USERNAME = 'webmaster@example.com'
SMTP_PASSWORD = 'smtpsecretpassword'
SMTP_SENDADDR = 'webmaster@example.com'

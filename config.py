from flask import Flask
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_admin import Admin

app = Flask(__name__)

db = SQLAlchemy()

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE']='sqlalchemy'
app.config['SESSION_SQLALCHEMY']=db
app.config['SECRET_KEY'] = 'no_key'
app.config["IMAGE_UPLOAD_PATH"] = "image_uploads"
app.config["FILE_UPLOAD_PATH"] = "file_uploads"


migrate = Migrate(app, db)
CORS(app)

Session(app)
bcrypt = Bcrypt(app)
mash = Marshmallow(app)
api = Api(app)
db.init_app(app)
admin = Admin(app, name="GoldWorth", template_mode='bootstrap4')

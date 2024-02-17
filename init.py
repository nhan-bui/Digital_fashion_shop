from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:nhandeptrai190103@127.0.0.1:3306/digital_shop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "$%###eqrwqr234312434214"

db = SQLAlchemy(app=app)

cloudinary.config(
    cloud_name="dscod7nw4",
    api_key="436956288784746",
    api_secret="fVQbs2xeeOko-M5Oh8H8AkYw_ds"
)

login_manager = LoginManager(app=app)
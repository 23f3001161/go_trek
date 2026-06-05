from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security
from routes.admin.admin_route import admin
from models.models import db, create_db
from routes.auth.auth_routes import auth
from extensions.extensions import userdatastore
from dotenv import load_dotenv

import os
load_dotenv()
app = Flask(__name__)

app.register_blueprint(admin)
app.register_blueprint(auth)
app.config["SQLALCHEMY_DATABASE_URI"]= os.getenv("SQLITE_URI")
app.config["SECURITY_PASSWORD_SALT"] = os.getenv("PASS_SALT")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SECURITY_JOIN_USER_ROLES"] = True
# app.config["SQLALCHEMY_TRACK_MODIFICATION"]= False
# app.config["SECURITY_REGISTRABLE"] = True
# app.config["SECURITY_SEND_REGISTER_EMAIL"] = True
# app.config["SECURITY_USE_REGISTER_V2"] = True
db.init_app(app)

security = Security(app, userdatastore)


if __name__ == "__main__":
    create_db(app,userdatastore)
    app.run(debug=True)
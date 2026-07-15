from flask import Blueprint, jsonify
from flask_security import utils, login_required, current_user, auth_token_required
from flask import request
from flask_security.utils import hash_password, verify_password
from models.models import db
from src.auth.controller import auth_controller
import uuid
auth = Blueprint("auth",__name__)


@auth.route("/api/login", methods =['POST'])
def login():

    data = request.get_json()
    return auth_controller.login_controller(data)

   


@auth.route("/api/logout", methods = ['POST'])
@auth_token_required
def logout():
    current_user.fs_uniquifier = uuid.uuid4().hex
    db.session.commit()
    utils.logout_user()

    return jsonify({
        "message" : "Logged out successfully"
    }), 200





@auth.route("/api/register", methods = ['POST'])
def register():
    data = request.get_json()
    return auth_controller.register(data)

    
    

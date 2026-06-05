from flask import Blueprint, jsonify
from flask_security import utils, login_required, current_user
from flask import request
from flask_security.utils import hash_password, verify_password
from models.models import db
from extensions.extensions import userdatastore
auth = Blueprint("auth",__name__)



@auth.route("/api/login", methods =['POST'])
def login():

    data = request.get_json()

    # name =data['name']
    email = data['email']
    password = data['password']
    
    

    user = userdatastore.find_user(email=email)
    if not user:
        
        return jsonify({
            "error": "User Not Found"
        }), 404
    
    if not verify_password(password, user.password):
         return jsonify({
            "error": "Password is wrong"
        }), 401
    auth_token = user.get_auth_token()
    utils.login_user(user)
    return jsonify({
            "data": {
                "name" : user.full_name,
                "role" : [ role.name for role in user.roles]
            },
            "auth_token" : auth_token
        }), 200


@auth.route("/api/check", methods = ['GET'])
@login_required
def check_auth():
    return {
        "status" : "User is authenticated",
        "email" : current_user.email
    }, 200


@auth.route("/api/logout", methods = ['POST'])
@login_required
def logout():

    utils.logout_user()

    return jsonify({
        "message" : "Logged out successfully"
    }), 200


@auth.route("/api/register", methods = ['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    role = data['role']

    if not ('name' in data and 'email' in data and 'password' in data and 'role' in data):
            return jsonify({'message': "Something went wrong!"}), 400
    
    if userdatastore.find_user(email =email):
         return jsonify({
              "message" : "Email already exists",
         }), 400
    userdatastore.create_user(
         full_name=name,
         email=email,
         password=hash_password(password),
         roles=[userdatastore.find_role(role)]
    )
    db.session.commit()
    data = {
         "message" : "Registered Sucessfully",
         "values" : {
              "name" : name,
              "email" : email,
              "role" : role
         }
    }

    return jsonify(data), 201

    
    

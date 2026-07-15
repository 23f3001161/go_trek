from flask import Blueprint, jsonify
from flask_security import utils, login_required, current_user
from flask import request
from flask_security.utils import hash_password, verify_password
from models.models import db
from extensions.extensions import userdatastore
import traceback


def login_controller(data):
    

    try:
        if not data:
            return jsonify({
        "error": "Request body required"
    }), 400

        email = data['email']
        print(email)
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
            "message" : "Logged In Successfully",
                "data": {
                    "id" : user.id,
                    "name" : user.full_name,
                    "role" : [ role.name for role in user.roles]
                },
                "auth_token" : auth_token
            }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({
        "error": "Internal Server Error",
        "error message": f"{str(e)}"
    }), 500





def register(data):

    try:
        if not data:
            return jsonify({
        "error": "Request body required"
    }), 400
        name = data['name']
        email = data['email']
        password = data['password']
        # The user will register only, Staff not register, Staff create admin only.
        role = "user"

        if not ('name' in data and 'email' in data and 'password' in data):
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
    except Exception as e:
        print(f"Some error occured: {str(e)}")
        return jsonify({
        "error": "Internal Server Error"
    }), 500
    
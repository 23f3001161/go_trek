from flask import Blueprint, jsonify
from flask_security import auth_token_required, utils
from flask import request
from extensions.extensions import userdatastore
admin = Blueprint("admin",__name__)



# @admin.route("/api/login", methods =['POST'])
# def index():

#     data = request.get_json()

#     # name =data['name']
#     email = data['email']
#     # password = data['password']
#     user = userdatastore.find_user(email=email)
#     if user:
#         auth_token = user.get_auth_token()
#         utils.login_user(user)
#         return {
#             "name" : email,
#             "auth_token" : auth_token
#         }
#     return jsonify({
#         "status" : "Healthy",
#         "auth" : True
#     }), 200



# @admin.route("/api/check", methods = ['GET'])
# @auth_token_required
# def check_auth():
#     return {
#         "status" : "User is authenticated"
#     }, 200
from flask import Blueprint, jsonify
from flask_security import auth_token_required, utils, roles_accepted, current_user
from flask import request
from flask_security.utils import verify_password, hash_password
from extensions.extensions import userdatastore, db
from src.admin.controller import admin_controller


admin = Blueprint("admin",__name__)



@admin.route("/api/staffs/create", methods =['POST'])
@auth_token_required
@roles_accepted('admin')
def create_staff():
    data = request.get_json()
    return admin_controller.create_staff_controller(data)
    

    
@admin.route("/api/staffs/<int:staff_id>", methods =['GET'])
@auth_token_required
@roles_accepted('admin')
def get_single_staff(staff_id):
    return admin_controller.get_single_staff_controller(staff_id)


@admin.route("/api/staffs", methods =['GET'])
@auth_token_required
@roles_accepted('admin')
def get_all_staff():
    search_query= request.args.get('q','').strip()
    return admin_controller.get_staff_controller(search_query)

@admin.route("/api/staffs/<int:staff_id>", methods =['PUT'])
@auth_token_required
@roles_accepted('admin')
def update_staff(staff_id):
    data = request.get_json()
    return admin_controller.update_staff_controller(staff_id,data)



@admin.route("/api/treks", methods = ['POST'])
@auth_token_required
@roles_accepted('admin')
def create_trek():
    data = request.get_json()
    return admin_controller.create_trek(data)


@admin.route("/api/treks", methods = ['GET'])
@auth_token_required
@roles_accepted('admin','user')
def get_treks():
    search_query= request.args.get('q','').strip()
    status_filter = request.args.get('status', '').strip().lower()
    return admin_controller.get_trek(search_query,status_filter)


@admin.route("/api/treks/<int:trek_id>", methods = ['PUT'])
@auth_token_required
@roles_accepted('admin','user')
def update_treks(trek_id):
    data = request.get_json()
    
    return admin_controller.update_trek(trek_id,data)


@admin.route("/api/treks/<int:trek_id>", methods=['DELETE'])
@auth_token_required
@roles_accepted("admin")
def delete_trek(trek_id: int):
    return admin_controller.delete_trek_controller(trek_id)

@admin.route("/api/users", methods=['GET'])
@auth_token_required
@roles_accepted("admin")
def get_all_users():
    search= request.args.get("q", '').strip()
    status = request.args.get('status',True)
    staff= request.args.get('staff',False)
    return admin_controller.get_user_controller(search,status,staff)


@admin.route("/api/users/<int:user_id>", methods =['PUT'])
@auth_token_required
@roles_accepted('admin')
def update_user(user_id):
    data = request.get_json()
    return admin_controller.update_user_controller(user_id,data)


@admin.route("/api/bookings", methods =['GET'])
@auth_token_required
@roles_accepted("admin")
def get_bookings():
    search = request.args.get("q", '').strip()
    status = request.args.get('status')
    return admin_controller.get_bookings(search,status)
from flask import Blueprint
from flask_security import auth_token_required, roles_accepted, current_user
from flask import request
from src.user.controller import controller


user = Blueprint("user", __name__)


@user.route("/api/users/bookings", methods =['POST'])
@auth_token_required
@roles_accepted("user")
def book_trek():
    data = request.get_json()
    return controller.book_trek_controller(data,current_user.id)

@user.route("/api/users/bookings", methods =['GET'])
@auth_token_required
@roles_accepted("user")
def get_bookings():
    return controller.get_my_bookings_controller(current_user.id)

@user.route("/api/users/bookings/<int:booking_id>", methods =['GET'])
@auth_token_required
@roles_accepted("user")
def get_booking(booking_id):

    return controller.get_booking_controller(booking_id,current_user.id)


@user.route("/api/users/dashboard", methods =['GET'])
@auth_token_required
@roles_accepted("user")
def get_all_details():
    return controller.get_all_details_controller(current_user.id)

@user.route("/api/users/history", methods =['GET'])
@auth_token_required
@roles_accepted("user")
def get_booking_history():
    return controller.view_trek_history(current_user.id)


@user.route("/api/users/profile", methods = ['PUT'])
@auth_token_required
@roles_accepted("user")
def update_profile():
    data = request.get_json()
    return controller.update_user_controller(data,current_user.id)



@user.route("/api/csv", methods =['GET'])
@auth_token_required
@roles_accepted("user")
def generate_csv():
    return controller.generate_csv_controller(current_user.id)


@user.route("/api/users/status/<task_id>", methods =['GET'])
@auth_token_required
@roles_accepted("user")
def get_csv_status(task_id):
    return controller.get_task_status(task_id)



@user.route("/api/users/bookings", methods =['DELETE'])
@auth_token_required
@roles_accepted("user")
def cancel_trek():
    data = request.get_json()
    return controller.cancel_booking(data,current_user.id)

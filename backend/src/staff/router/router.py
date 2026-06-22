from flask import Blueprint
from flask_security import auth_token_required, roles_accepted, current_user
from flask import request
from src.staff.controller import controller


staff = Blueprint("staff", __name__)

@staff.route("/api/staff/treks", methods=['GET'])
@auth_token_required
@roles_accepted("staff")
def view_assigned_trek():
    """
    Staff can view assigned Treks
    Args:
    id : current_user.id
    """
    print(current_user)
    return controller.get_all_trek(current_user.id)

@staff.route("/api/staff/treks/<int:trek_id>/participants", methods=['GET'])
@auth_token_required
@roles_accepted("staff","admin")
def view_participants(trek_id):
    """
    Staff can view booked users for their particular trek
    """
    return controller.get_participants_controller(trek_id,current_user)
    


@staff.route("/api/bookings/<int:booking_id>", methods=["PUT"])
@auth_token_required
@roles_accepted("staff")
def update_booking_status(booking_id):

    data = request.get_json()

    return controller.update_booking_status_controller(
        booking_id,
        data
    )
@staff.route("/api/staff/trek/<int:trek_id>")
@roles_accepted("staff", "admin")
@auth_token_required
def get_single_trek(trek_id):
    return controller.get_single_trek_controller(trek_id)

@staff.route("/api/treks/<int:trek_id>", methods = ['PUT'])
@auth_token_required
@roles_accepted("staff")
def update_trek_status(trek_id, data):
    data = request.get_json()
    return controller.update_trek_status(data,trek_id)
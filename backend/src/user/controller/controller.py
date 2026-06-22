from flask import jsonify
from flask_security.utils import hash_password,verify_password
from extensions.extensions import userdatastore, db
from models.models import TrekModel, Users, BookingModel
from datetime import datetime, date



def book_trek_controller(data,current_user_id):
    required_fields = [
         "trek_id", 
        "payment_status"
    ]
    missing_fields = [field for field in required_fields if data.get(field) is None or data.get(field) ==""]
    if missing_fields:
        return jsonify({
            "error" : "Missing requred fields",
            "fields_required" : missing_fields
        }), 400
    
    try:
        user_id = current_user_id
        trek_id = data["trek_id"]

        user = Users.query.get(user_id)
        if not user:
            return jsonify({
                "error" : "User not found"
            }), 404
        trek = TrekModel.query.get(trek_id)
        if not trek:
            return jsonify({
                "error" : "Trek not found"
            }), 404 

        if trek.available_slots <=0:
            return jsonify({
                "error" : "No slots available"
            }), 400
        existing_booking = BookingModel.query.filter_by(
            user_id=user_id,
            trek_id=trek_id
        ).first()

        if existing_booking:
            return jsonify({
                "error": "You already booked this trek"
            }), 400

        confirmed_bookings = BookingModel.query.filter_by(status="booked").count()
        if confirmed_bookings < trek.total_slots:
            new_booking = BookingModel(
            user_id=user_id,
            trek_id=trek_id,
            status="booked",
            payment_status=data.get(
                "payment_status",
                "pending"
            )
        )
        else:
            new_booking = BookingModel(
            user_id=user_id,
            trek_id=trek_id,
            status="waitlist",
            payment_status=data.get(
                "payment_status",
                "pending"
            )
        )
        db.session.add(new_booking)
        trek.available_slots -=1
        db.session.commit()
        return jsonify({
            "message" : "Trek Booked Successfully",
            "booking_id" : new_booking.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error" : "Internal Server error",
            "actual_error" : str(e)
        }), 500
    


def get_my_bookings_controller(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({
            "error" : "User does not exist",
        }), 404
    
    try:
        bookings = BookingModel.query.filter_by(user_id=user_id).order_by(BookingModel.booking_date.desc()) .all()

        return jsonify({
            "total_bookings" : len(bookings),
            "data": [
                {
            "booking_id": booking.id,
            "booking_date": booking.booking_date,
            "status": booking.status,
            "payment_status": booking.payment_status,

            "trek": {
                "id": booking.trek.id,
                "name": booking.trek.name,
                "location": booking.trek.location,
                "difficulty": booking.trek.difficulty,
                "duration_days": booking.trek.duration_days,
                "start_date": booking.trek.start_date,
                "end_date": booking.trek.end_date,
                "status": booking.trek.status
            }
        }
                for booking in bookings
            ]
        }), 200
    except Exception as e:
        return jsonify({
            "error" : "Internal Server Error",
            "actual_error" : str(e)
        })
    

def get_booking_controller(booking_id,current_user_id):
    try:
        booking = BookingModel.query.get(booking_id)
        if not booking:
            return jsonify({
                "message" : "Trek not found"
            }), 404
        if booking.user_id != current_user_id:
            return jsonify({
                "error" : "You are not authorized to view this booking"
            }), 403
        return jsonify({
            "data" : {
                "booking_id": booking.id,
                "booking_status": booking.status,
                "payment_status": booking.payment_status,
                "booking_date": booking.booking_date,

                "trek": {
                    "id": booking.trek.id,
                    "name": booking.trek.name,
                    "location": booking.trek.location,
                    "difficulty": booking.trek.difficulty,
                    "start_date": booking.trek.start_date,
                    "end_date": booking.trek.end_date,
                    "status": booking.trek.status
                }
            }
        }), 200


        
    except Exception as e:
        return jsonify({
            "error" : "Something went wrong",
            "actual_error" : str(e)
           
        })

def get_all_details_controller(user_id:int):
    try:
        available_treks= TrekModel.query.filter_by(
            status= "open"
        ).order_by(TrekModel.created_at.desc()).all()
        booked_treks = BookingModel.query.join(TrekModel).filter(
            BookingModel.user_id == user_id,
            BookingModel.status != "cancelled",
            TrekModel.start_date >= date.today()
        ).all()
        return jsonify({
            "total_available_treks" : len(available_treks),
            "total_booked_treks" : len(booked_treks),
            "available_treks": [
                    {
                        "id": trek.id,
                    "name": trek.name,
                    "location": trek.location,
                    "available_slots": trek.available_slots,
                    "status": trek.status
                    }
                for trek in available_treks
            ],
            "booked_treks" : [
{
    "booking_id" : booking.id,
    "trek_name" : booking.trek.name,
    "trek_id" : booking.trek.id,
    "booking_status": booking.status,
    "payment_status": booking.payment_status,
    "booking_date": booking.booking_date

}
                for booking in booked_treks
            ]
        }), 200

        
    except Exception as e:
        return jsonify({
            "error" : "Someting went wrong",
            "actual_error" : str(e)

        }),500
    


def view_trek_history(user_id):
    try:
        booked_treks = BookingModel.query.filter_by(
            BookingModel.user_id == user_id,
            BookingModel.status != "cancelled",
            
        ).order_by(BookingModel.booking_date.desc()).all()
        return jsonify({
            "booked_treks" : [
{
    "booking_id" : booking.id,
    "trek_name" : booking.trek.name,
    "trek_id" : booking.trek.id,
    "booking_status": booking.status,
    "payment_status": booking.payment_status,
    "booking_date": booking.booking_date

}
                for booking in booked_treks
            ]
        }), 200

    except Exception as e:
        return jsonify({
            "error" : "Someting went wrong",
            "actual_error" : str(e)

        }),500
    


def update_user_controller(data, user_id):
    try:
        user = Users.query.get(user_id)
        if not user:
            return jsonify({
                "error" : "User not found"
            }), 404
        allowed_fields = {
            "full_name" ,
            "email" ,
            "phone"
        }

        safe_data = {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }
        if not safe_data:
            return jsonify({
                "error" : "No valid fields provided"
            }),400
        
        if "email" in safe_data:
            existing_user = Users.query.filter(
                Users.email == safe_data["email"],
                Users.id != user_id
            ).first()
        
        if existing_user:
            return jsonify({
                "error" : "Email already exists"
            }), 400
        user.email = safe_data.get("email", user.email)
        user.full_name = safe_data.get("full_name", user.full_name)
        user.phone = safe_data.get("phone", user.phone)
        db.session.commit()
        return jsonify({
            "message": "Profile updated successfully",
            "data": {
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "phone": user.phone
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error" : "Something went wrong",
            "actual_error" : str(e)
        }), 500
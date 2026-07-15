from flask import jsonify
from extensions.extensions import  db
from models.models import TrekModel, Users, BookingModel
from datetime import date
import json
from extensions.extensions import redis_client
def book_trek_controller(data,current_user_id):
    cache_key= f"booking:{current_user_id}"
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
        redis_client.delete(cache_key)
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
        if trek.status != "open":
            return jsonify({
                "error": f"Trek is not open for booking (current status: {trek.status})"
            }), 400
        
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

        confirmed_bookings = BookingModel.query.filter_by(status="booked",trek_id=trek_id).count()
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
            trek.available_slots -=1
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

    cache_key= f"booking:{user_id}"

    booking_cache = redis_client.get(cache_key)
    if booking_cache:
        return json.loads(booking_cache)
    user = Users.query.get(user_id)
    if not user:
        return jsonify({
            "error" : "User does not exist",
        }), 404
    
    try:
        bookings = BookingModel.query.filter_by(user_id=user_id).order_by(BookingModel.booking_date.desc()) .all()
        data = [
                {
            "booking_id": booking.id,
            "booking_date": booking.booking_date.isoformat(),
            "status": booking.status,
            "payment_status": booking.payment_status,

            "trek": {
                "id": booking.trek.id,
                "name": booking.trek.name,
                "location": booking.trek.location,
                "difficulty": booking.trek.difficulty,
                "duration_days": booking.trek.duration_days,
                "start_date": booking.trek.start_date.isoformat(),
                "end_date": booking.trek.end_date.isoformat(),
                "status": booking.trek.status
            }
        }
                for booking in bookings
            ]
        redis_client.set(cache_key,json.dumps(data),300)
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
        booked_treks = BookingModel.query.filter(
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
    


def generate_csv_controller(user_id):

    from celery_app.celery_app import generate_csv
    try:

        user = Users.query.get(user_id)
        if not user:
            return jsonify({
                "Error" : "User not found"
            }), 404
        

        task = generate_csv.delay(user_id)
        return jsonify({
            "status" : "Accepted",
            "id" : task.id,
            "message" : "Your report will be sent to your email"
        }), 202
    
    except Exception as e:
        return jsonify({
            "error" : "Internal Server Error",
            "actual_error" : str(e)
        }), 500
    


def get_task_status(task_id):
    from celery_app.celery_app import celery
    task = celery.AsyncResult(task_id)

    return jsonify({
        "task_id" : task.id,
        "status" : task.status

    }), 200




def cancel_booking(data,user_id):

    if data:
        booking_id= data["id"]
        booking = BookingModel.query.get(booking_id)
        if booking.user_id != user_id:
            return jsonify({
                "message" : "You are not authorized to change the booking status"
            }), 403

    if booking.status == "cancelled":
        return jsonify({
            "error" : "Booking already cancelled"
        }), 400
    
    booking.status = "cancelled"
    trek = booking.trek
    trek.available_slots +=1

    next_waitlist= (
        BookingModel.query.filter_by(
            trek_id= trek.id,
            status = "waitlist"
        ).order_by(
            BookingModel.booking_date.asc()
        ).first()
    )
    if next_waitlist:
        next_waitlist.status = "booked"
        trek.available_slots -=1

    db.session.commit()
    redis_client.delete(f"booking:{user_id}")
    if next_waitlist:
        redis_client.delete(f"booking:{next_waitlist.user_id}")
    redis_client.delete(f"treks:list")
    redis_client.delete(f"treks:{trek.id}")
    return jsonify({
        "message": "Booking cancelled successfully",
        "booking_id": booking_id
    }), 200




from models.models import TrekModel, Users, BookingModel

import json
 
 

def book_trek_controller(data, current_user_id):
    user_id = current_user_id          
    cache_key = f"booking:{user_id}"    #
 
    required_fields = ["trek_id", "payment_status"]
    missing_fields = [
        field for field in required_fields
        if data.get(field) is None or data.get(field) == ""
    ]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields_required": missing_fields
        }), 400
 
    try:
        trek_id = data["trek_id"]
 
        user = Users.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
 
        trek = TrekModel.query.get(trek_id)
        if not trek:
            return jsonify({"error": "Trek not found"}), 404
 
        # Only allow booking when trek status is Open
        if trek.status != "open":
            return jsonify({
                "error": f"Trek is not open for booking (current status: {trek.status})"
            }), 400
 
        existing_booking = BookingModel.query.filter_by(
            user_id=user_id, trek_id=trek_id
        ).first()
        if existing_booking:
            return jsonify({"error": "You have already booked this trek"}), 400
 
        confirmed_bookings = BookingModel.query.filter_by(
            status="booked", trek_id=trek_id
        ).count()
 
        if confirmed_bookings < trek.total_slots:
            new_booking = BookingModel(
                user_id=user_id,
                trek_id=trek_id,
                status="booked",
                payment_status=data.get("payment_status", "pending")
            )
            trek.available_slots -= 1
        else:
            new_booking = BookingModel(
                user_id=user_id,
                trek_id=trek_id,
                status="waitlist",
                payment_status=data.get("payment_status", "pending")
            )
 
        db.session.add(new_booking)
        db.session.commit()
 
        
        redis_client.delete(cache_key)
        redis_client.delete("treks:list")
        redis_client.delete(f"treks:{trek_id}")
 
        return jsonify({
            "message": "Trek booked successfully",
            "booking_id": new_booking.id,
            "status": new_booking.status
        }), 201
 
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500
 
 

def get_my_bookings_controller(user_id):
    cache_key = f"booking:{user_id}"
 
    booking_cache = redis_client.get(cache_key)
    if booking_cache:
     
        return jsonify(json.loads(booking_cache)), 200
 
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User does not exist"}), 404
 
    try:
        bookings = (
            BookingModel.query
            .filter_by(user_id=user_id)
            .order_by(BookingModel.booking_date.desc())
            .all()
        )
        data = [
            {
                "booking_id": booking.id,
                "booking_date": booking.booking_date.isoformat(),
                "status": booking.status,
                "payment_status": booking.payment_status,
                "trek": {
                    "id": booking.trek.id,
                    "name": booking.trek.name,
                    "location": booking.trek.location,
                    "difficulty": booking.trek.difficulty,
                    "duration_days": booking.trek.duration_days,
                    "start_date": booking.trek.start_date.isoformat(),
                    "end_date": booking.trek.end_date.isoformat(),
                    "status": booking.trek.status
                }
            }
            for booking in bookings
        ]
 
        
        redis_client.set(cache_key, json.dumps(data), ex=300)
 
        return jsonify({
            "total_bookings": len(data),
            "data": data
        }), 200
 
    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500
 
 
def get_booking_controller(booking_id, current_user_id):
    try:
        booking = BookingModel.query.get(booking_id)
        if not booking:
            return jsonify({"message": "Booking not found"}), 404
 
        if booking.user_id != current_user_id:
            return jsonify({
                "error": "You are not authorized to view this booking"
            }), 403
 
        return jsonify({
            "data": {
                "booking_id": booking.id,
                "booking_status": booking.status,
                "payment_status": booking.payment_status,
                "booking_date": booking.booking_date.isoformat(),
                "trek": {
                    "id": booking.trek.id,
                    "name": booking.trek.name,
                    "location": booking.trek.location,
                    "difficulty": booking.trek.difficulty,
                    "start_date": booking.trek.start_date.isoformat(),
                    "end_date": booking.trek.end_date.isoformat(),
                    "status": booking.trek.status
                }
            }
        }), 200
 
    except Exception as e:
        return jsonify({
            "error": "Something went wrong",
            "actual_error": str(e)
        }), 500
 
 
def get_all_details_controller(user_id: int):
    try:
        available_treks = (
            TrekModel.query
            .filter_by(status="open")
            .order_by(TrekModel.created_at.desc())
            .all()
        )
        booked_treks = (
            BookingModel.query.join(TrekModel).filter(
                BookingModel.user_id == user_id,
                BookingModel.status != "cancelled",
                TrekModel.start_date >= date.today()
            ).all()
        )
        return jsonify({
            "total_available_treks": len(available_treks),
            "total_booked_treks": len(booked_treks),
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
            "booked_treks": [
                {
                    "booking_id": booking.id,
                    "trek_name": booking.trek.name,
                    "trek_id": booking.trek.id,
                    "booking_status": booking.status,
                    "payment_status": booking.payment_status,
                    "booking_date": booking.booking_date.isoformat()
                }
                for booking in booked_treks
            ]
        }), 200
 
    except Exception as e:
        return jsonify({
            "error": "Something went wrong",
            "actual_error": str(e)
        }), 500
 
 

def view_trek_history(user_id):
    try:
        
        booked_treks = (
            BookingModel.query
            .filter(
                BookingModel.user_id == user_id,
                BookingModel.status != "cancelled"
            )
            .order_by(BookingModel.booking_date.desc())
            .all()
        )
        return jsonify({
            "total": len(booked_treks),
            "booked_treks": [
                {
                    "booking_id": booking.id,
                    "trek_name": booking.trek.name,
                    "trek_id": booking.trek.id,
                    "location": booking.trek.location,
                    "difficulty": booking.trek.difficulty,
                    "start_date": booking.trek.start_date.isoformat(),
                    "end_date": booking.trek.end_date.isoformat(),
                    "booking_status": booking.status,
                    "payment_status": booking.payment_status,
                    "booking_date": booking.booking_date.isoformat()
                }
                for booking in booked_treks
            ]
        }), 200
 
    except Exception as e:
        return jsonify({
            "error": "Something went wrong",
            "actual_error": str(e)
        }), 500
 
 
def update_user_controller(data, user_id):
    try:
        user = Users.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
 
        allowed_fields = {"full_name", "email", "phone"}
        safe_data = {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }
        if not safe_data:
            return jsonify({"error": "No valid fields provided"}), 400
 
        if "email" in safe_data:
            existing_user = Users.query.filter(
                Users.email == safe_data["email"],
                Users.id != user_id
            ).first()
            if existing_user:
                return jsonify({"error": "Email already in use"}), 400
 
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
            "error": "Something went wrong",
            "actual_error": str(e)
        }), 500
 
 
def generate_csv_controller(user_id):
    from celery_app.celery_app import generate_csv
    try:
        user = Users.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
 
        task = generate_csv.delay(user_id)
        return jsonify({
            "status": "Accepted",
            "task_id": task.id,
            "message": "Your booking history will be sent to your email shortly"
        }), 202
 
    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500
 
 
def get_task_status(task_id):
    from celery_app.celery_app import celery
    task = celery.AsyncResult(task_id)
    return jsonify({
        "task_id": task.id,
        "status": task.status
    }), 200
 
 
def cancel_booking(data, user_id):
    if not data or "id" not in data:
        return jsonify({"error": "Booking ID required"}), 400
 
    booking_id = data["id"]
    booking = BookingModel.query.get(booking_id)
 
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
 
    if booking.user_id != user_id:
        return jsonify({
            "error": "You are not authorized to cancel this booking"
        }), 403
 
    if booking.status == "cancelled":
        return jsonify({"error": "Booking is already cancelled"}), 400
    
    previous_status = booking.status
    booking.status = "cancelled"
    trek = booking.trek
 
  
    if previous_status == "booked":
        trek.available_slots += 1
 

    next_waitlist = (
        BookingModel.query
        .filter_by(trek_id=trek.id, status="waitlist")
        .order_by(BookingModel.booking_date.asc())
        .first()
    )
    if next_waitlist:
        next_waitlist.status = "booked"
        trek.available_slots -= 1
 
    db.session.commit()
 
 
    redis_client.delete(f"booking:{user_id}")
    redis_client.delete(f"treks:list")
    redis_client.delete(f"treks:{trek.id}")
    if next_waitlist:
        redis_client.delete(f"booking:{next_waitlist.user_id}")
 
    return jsonify({
        "message": "Booking cancelled successfully",
        "booking_id": booking_id
    }), 200
 

def browse_treks_controller(search, difficulty, location, duration):
    try:
      
        cache_key = f"treks:browse:{search}:{difficulty}:{location}:{duration}"
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify(json.loads(cached)), 200
 
        query = TrekModel.query.filter_by(status="open")
 
        if search:
            term = f"%{search}%"
            query = query.filter(
                (TrekModel.name.ilike(term)) |
                (TrekModel.location.ilike(term))
            )
        if difficulty and difficulty in ("easy", "moderate", "hard"):
            query = query.filter(TrekModel.difficulty == difficulty)
 
        if location:
            query = query.filter(TrekModel.location.ilike(f"%{location}%"))
 
        if duration:
            try:
                query = query.filter(TrekModel.duration_days == int(duration))
            except ValueError:
                return jsonify({"error": "duration must be an integer"}), 400
 
        treks = query.order_by(TrekModel.start_date.asc()).all()
 
        data = [
            {
                "id": trek.id,
                "name": trek.name,
                "location": trek.location,
                "difficulty": trek.difficulty,
                "duration_days": trek.duration_days,
                "available_slots": trek.available_slots,
                "total_slots": trek.total_slots,
                "start_date": trek.start_date.isoformat(),
                "end_date": trek.end_date.isoformat(),
                "status": trek.status,
                "assigned_staff": (
                    trek.assigned_staff.full_name if trek.assigned_staff else None
                )
            }
            for trek in treks
        ]
 
        
        redis_client.set(cache_key, json.dumps(data), ex=120)
 
        return jsonify({
            "total": len(data),
            "data": data
        }), 200
 
    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500
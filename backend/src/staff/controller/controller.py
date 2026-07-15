from flask import jsonify
from extensions.extensions import  db
from models.models import TrekModel,BookingModel




def get_single_trek_controller(trek_id):
    try:
        if not trek_id:
            return jsonify({
            "error" : "Trek ID is requirerd"
            }), 400
        
        trek = TrekModel.query.get(trek_id)
        if not trek:
            return jsonify({
                "error" : "Trek not founds"
            })
            
            
        return jsonify({
                    "data": {
                    "id": trek.id,
                    "name": trek.name,
                    "location": trek.location,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "available_slots": trek.available_slots,
                    "status": trek.status,
                    "start_date": trek.start_date,
                    "end_date": trek.end_date
                    }
                }), 200
           
        

    except Exception as e:
        return jsonify({
            "error" : "Something Went Wrong",
            "actual_error" : str(e)
        }), 500

def get_participants_controller(trek_id, current_user):

    try:

        trek = TrekModel.query.filter_by(id=trek_id).first()

        if not trek:
            return jsonify({
                "error": "Trek not found"
            }), 404
        if current_user.has_role("staff"):
            if trek.assigned_staff_id != current_user.id:
                return jsonify({
                "error" : "You are not assigned to this trek"
            }), 403
        bookings = BookingModel.query.filter_by(
            trek_id=trek_id
        ).all()

        return jsonify({
            "trek_id": trek.id,
            "trek_name": trek.name,
            "participants": [
                {
                    "booking_id": booking.id,
                    "user_id": booking.user.id,
                    "name": booking.user.full_name,
                    "email": booking.user.email,
                    "phone": booking.user.phone,
                    "booking_status": booking.status,
                    "payment_status": booking.payment_status
                }
                for booking in bookings
            ]
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500
    


def update_booking_status_controller(
    booking_id,
    data
):

    try:

        booking = BookingModel.query.filter_by(
            id=booking_id
        ).first()

        if not booking:
            return jsonify({
                "error": "Booking not found"
            }), 404

        allowed_status = {
            "booked",
            "cancelled",
            "completed"
        }

        status = data.get("status")

        if status not in allowed_status:
            return jsonify({
                "error": "Invalid booking status"
            }), 400

        booking.status = status
        
            

        db.session.commit()

        return jsonify({
            "message": "Booking updated successfully",
            "data": {
                "booking_id": booking.id,
                "user_name": booking.user.full_name,
                "trek_name": booking.trek.name,
                "status": booking.status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500
    


def update_trek_status(data,trek_id):
    try:

        allowed_fields = {
    'status',
    'available_slots'
}

        if 'available_slots' in data and data['available_slots'] < 0:
            return jsonify({
        "error": "available_slots cannot be negative"
    }), 400
        trek_model = TrekModel.query.filter_by(id=trek_id)
        trek = trek_model.first()

        if not trek:
            return jsonify({
        "error": "Trek not found"
    }), 404
        bookng_model_count = BookingModel.query.filter_by(trek_id=trek_id,status='booked').count()
        

        
        if  'status' in data:
            allowed_staff_status = {
                'started',
                'completed'
            }
            if data["status"] not in allowed_staff_status:
                return jsonify({
                    "error": (
                "Staff can only update status "
                "to started or completed"
            )
                }), 403
        if 'available_slots' in data:
                slots = data['available_slots'] + bookng_model_count
                if  slots > trek.total_slots:
                    return jsonify({
                "error": (
                f"Invalid slot count. "
                f"Booked={bookng_model_count}, "
                f"Available={data['available_slots']}, "
                f"Total Capacity={trek.total_slots}"
            )
        }), 400
        safe_data = {
    k: v
    for k, v in data.items()
    if k in allowed_fields
}
        if not safe_data:
            return jsonify({
                "error" : "No valid fields provided"
            }), 400
        trek_model.update(safe_data)
        
        db.session.commit()

        return jsonify({
            "message" : "status updated successfully"
        }), 200



    except Exception as e:

        return jsonify({
            "error": "Internal Server Error",
            "actual_error" : str(e)
        }),500
    




def get_all_trek(staff_id):
    try:

        treks = TrekModel.query.filter_by(assigned_staff_id= staff_id).all()
        return jsonify({
            "total_treks" : len(treks),
            "data" : [
                {
                    "id": trek.id,
                    "name": trek.name,
                    "location": trek.location,
                    "difficulty": trek.difficulty,
                    "duration_days": trek.duration_days,
                    "available_slots": trek.available_slots,
                    "status": trek.status,
                    "start_date": trek.start_date,
                    "end_date": trek.end_date
                }
                for trek in treks
            ]
        }), 200

        
    
    except Exception as e:
        return jsonify({
            "Error" : "Internal Server Error",
            "actual_error" : str(e)
        })
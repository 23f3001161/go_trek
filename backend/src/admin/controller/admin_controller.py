from flask import jsonify
from flask_security.utils import hash_password,verify_password
from extensions.extensions import userdatastore, db
from extensions.extensions import redis_client
from models.models import TrekModel, Users, BookingModel
from datetime import datetime
import json



def create_staff_controller(data):
    required_fields = [
        "email",
        "full_name",
        "phone_number",
        "password"
    ]
    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]
    if missing_fields:
        return jsonify({
            "error" : "Missing required fields",
            "fields_required" : missing_fields
        }), 400
    email = data['email'].strip().lower()
    full_name = data['full_name'].strip()
    phone = data['phone_number'].strip()
    password = hash_password(data['password'])
    
    user = userdatastore.find_user(email=email)
    if user:
        
        return jsonify({
            "error" : f"Staff already exists with name {user.full_name}",
            
        }), 403
    role = userdatastore.find_role("staff")
    user = userdatastore.create_user(
        email=email,
        password = password,
        full_name= full_name,
        roles = [role],
        phone=phone
    )
    db.session.commit()

    return jsonify({
        "message" : "Staff created successfully",
        "data": {
            "id" : user.id,
            "name" : full_name,
            "email" : email,
            "phone_number" : phone,
            "roles" : [role.name for role in user.roles]
        }
    }), 201



def get_single_staff_controller(staff_id : int):
    try:
        if not staff_id:
            return jsonify({
                "error", "Please enter staff id"
            }), 400
        user = userdatastore.user_model.query.get(staff_id)
        if not user or  not user.has_role("staff"):
            return jsonify({
                "error" : "Staff member not found"
            }), 404
        
        return jsonify({
        "message": "Staff details retrieved successfully",
        "data": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "phone": getattr(user, 'phone', 'N/A'),
            "active": user.active,
            "created_at": getattr(user, 'created_at', None),
        }
    })
    except Exception as e:
        
        return jsonify({
            "error" : "Something went wrong",
            "actual_error":  f"Error is {str(e)}"
        }), 500
    

def get_staff_controller(search_query):
    try:
        
        query = userdatastore.user_model.query.filter(
            userdatastore.user_model.roles.any(name='staff')
        )
        
        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                (userdatastore.user_model.full_name.ilike(search_term)) |
                (userdatastore.user_model.email.ilike(search_term)) |
                (userdatastore.user_model.phone.ilike(search_term))
            )
        
        staff_members = query.all()
        return jsonify({
        "message": "Staff details retrieved successfully",
        "data": [
            {
            "id": s.id,
            "name": s.full_name,
            "email": s.email,
            "phone_number": getattr(s, 'phone', 'N/A'),
            "active": s.active
        }
            for s in staff_members
        ]
    }), 200
    except Exception as e:
        
        return jsonify({
            "error" : "Something went wrong",
            "actual_error":  f"Error is {str(e)}"
        }), 500


def update_staff_controller(staff_id, data):
    user_query = userdatastore.user_model.query.filter_by(id=staff_id)
    user = user_query.first()

    if not user or not user.has_role('staff'):
        return jsonify({
            "error", "Staff not found"
        }), 404
    
    allowed_fields = {
        "full_name", 'phone', 'active'
    }
    safe_data = {key: value for key, value in data.items() if key in allowed_fields}

    if 'password' in data and data['password'].strip():
        safe_data['password'] = hash_password(data['password'])

    if safe_data:
        user_query.update(safe_data)
        db.session.commit()
    return jsonify({
        "message" : "Staff details updated sucessfully",
        "data": {
            "id": user.id,
            "name": user.full_name,
            "active": user.active
        }
    }), 200



def create_trek(data):
    required_fields = [
        "name", "location", "difficulty", "duration_days", 
        "total_slots", "start_date", "end_date", "created_by"
    ]
    missing_fields = [field for field in required_fields if data.get(field) is None or data.get(field) ==""]
    if missing_fields:
        return jsonify({
            "error" : "Missing requred fields",
            "fields_required" : missing_fields
        }), 400
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        total_slots = int(data['total_slots'])
        duration_days = int(data['duration_days']) 
        difficulty = data['difficulty'].strip().lower()

        new_trek = TrekModel(
            name=data['name'].strip(),
            location=data['location'].strip(),
            difficulty=difficulty,
            duration_days=duration_days,
            total_slots=total_slots,
            available_slots=total_slots, 
            status="pending",
            start_date=start_date,
            end_date=end_date,
            created_by = data.get("created_by")
        )
        db.session.add(new_trek)
        db.session.commit()
        for key in redis_client.scan_iter("treks:*"):
            redis_client.delete(key)
        return jsonify({
            "message": "Trek created successfully",
            "data": {
                "id": new_trek.id,
                "name": new_trek.name,
                "status": new_trek.status
            }
        }), 201 
    except Exception as e:
        

        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500




def get_trek(search_query,status):

    try:
        cache_key = f"treks:{search_query}:{status}"
        cached = redis_client.get(cache_key)

        if cached:
            return jsonify(json.loads(cached)), 200
        query = TrekModel.query

        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                (TrekModel.name.ilike(search_term)) |
                (TrekModel.location.ilike(search_term))
            )
        valid_statuses = ['pending', 'approved', 'open', 'closed', 'completed']
        if status:
            if status in valid_statuses:
                query = query.filter(TrekModel.status == status)
            else:
                return jsonify({
                "error" : "status not found",
                "message" : "Enter status on specified values"
            }),404
        treks = query.all()
        response = {
            "message" : "Treks retrieved successfully",
            "total_treks" : len(treks),
            "data" : [{
                "id": trek.id,
                "name": trek.name,
                "location": trek.location,
                "difficulty": trek.difficulty,
                "duration_days": trek.duration_days,
                "status": trek.status,
                "start_date": trek.start_date.strftime('%Y-%m-%d'),
                "available_slots": trek.available_slots,
                "staff_assigned": trek.assigned_staff.full_name if trek.assigned_staff else None
            } for trek in treks]
        }

        redis_client.setex(
        cache_key,
        300,
        json.dumps(response)
)

        return jsonify(response)
    except Exception as e:
        return jsonify({
            "error" : "Internal Server Error",
            "actual_error" : f"{str(e)}"
        })
    



def update_trek(trek_id, data):
    trek_model = TrekModel.query.filter_by(id=trek_id)
    trek = trek_model.first()
    if not trek:
        return jsonify({
        "error": "Trek not found"
    }), 404
    allowed_fields= {
      "available_slots",
      "difficulty",
      "duration_days",
      "location",
      "name",
      "assigned_staff_id",
      "start_date",
      "status"
    }

    safe_data = {key : value for key, value in data.items() if key in allowed_fields}

    if safe_data:
        if 'start_date' in safe_data:
            safe_data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d').date()

        trek_model.update(safe_data)
        # for key, value in safe_data.items():
        #     setattr(trek,key,value)
        db.session.commit()
    if 'status' in safe_data:
        return jsonify({
            "message" : f"Trek status changed to {trek.status}",
            "data" : {
            "id": trek.id,
            "name": trek.name,
            "status": trek.status
        }
        }),201

    return jsonify({
        "message" : "trek updated successfully",
        "data" : {
            "id": trek.id,
            "name": trek.name,
            "status": trek.status
        }
    }), 201


def delete_trek_controller(trek_id : int):

    trek = TrekModel.query.get(trek_id)
    
    if not trek:
        return jsonify({
            "error" : "Trek Not found"
        }), 404
    
    trek.status= 'closed'
    db.session.commit()

    return jsonify({
        "message" : f"Trek {trek.name} has been successfully canceled/closed",
        "data" : {
            "id" : trek.id,
            "name" : trek.name,
            "status" : trek.status
        }
    })



def get_user_controller(search, status, staff):
    try:
        query = userdatastore.user_model.query

        if str(staff).lower() == "true":
            query = query.filter(
                userdatastore.user_model.roles.any(name='staff')
            )   
        if search:
            search_term = f"%{search}%"

            query = query.filter(
                (userdatastore.user_model.full_name.ilike(search_term)) |
                (userdatastore.user_model.email.ilike(search_term)) |
                (userdatastore.user_model.phone.ilike(search_term))
            )
        print("status checking")
        if status is not None and status != "":
            is_active = str(status).strip().lower() == "true"
            query = query.filter(
                Users.active == is_active
            )
        users = query.all()
        return jsonify({
            "message": "Users retrieved successfully",
            "data": [
                {
                    "id": user.id,
                    "name": user.full_name,
                    "email": user.email,
                    "phone_number": user.phone,
                    "active": user.active,
                    "roles": [role.name for role in user.roles]
                }
                for user in users
            ]
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Internal Server Error",
            "actual_error": str(e)
        }), 500
    

def update_user_controller(user_id,data):
    try:
        user_model = Users.query.filter_by(id=user_id)
       
        user = user_model.first()
        if not user:
            return jsonify({
        "error": "User not found"
    }), 404
        allowed_fields = {
    "full_name",
    "email",
    "phone",
    "active"
}

        safe_data = {key : value for key, value in data.items() if key in allowed_fields}

        if safe_data:
            if 'active' in safe_data and not isinstance(safe_data['active'],bool):
                return jsonify({
                    "error" : "active must be true or false"
                })

            user_model.update(safe_data)
        # for key, value in safe_data.items():
        #     setattr(trek,key,value)
            db.session.commit()
            if 'active' in safe_data:
                return jsonify({
            "message" : f"User status changed to {user.active}",
            "data" : {
            "id": user.id,
            "name": user.full_name,
            "status": user.active
        }
        }),201

            return jsonify({
        "message" : "User updated successfully",
        "data" : {
            "id": user.id,
            "name": user.full_name,
            "status": user.active
        }
    }), 201
        
    except Exception as e:
        return jsonify({
            "message" : "Internal Server error",
            "actual_error" : f"Error is {str(e)}"
        }),500
    

def get_bookings(search_query, status):
    try:
        query = BookingModel.query

        if search_query:
            search_term = f"%{search_query}%"
            query = query.join(BookingModel.user).join(BookingModel.trek).filter(
                (
                (Users.full_name.ilike(search_term)) |
                (Users.email.ilike(search_term)) |
                (TrekModel.name.ilike(search_term)) 
                
            )

            )
        if status:
            query = query.filter(
                BookingModel.status == status
            )
    
        bookings = query.all()
        return jsonify({
        "total_bookings" : len(bookings),
        "data": [
            {
            "booking_id": booking.id,
            "user_name": booking.user.full_name,
            "trek_name": booking.trek.name,
            "status": booking.status,
            "payment_status": booking.payment_status,
            "booking_date": booking.booking_date
        }
        for booking in bookings
        ]
    }), 200
    except Exception as e:
        return jsonify({
            "error" : "Internal Server Error",
            "actual_error" : str(e)
        }), 500


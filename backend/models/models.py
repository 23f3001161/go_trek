
from flask import Flask
from flask_security import UserMixin, RoleMixin
from flask_security import SQLAlchemyUserDatastore

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timezone

db = SQLAlchemy()


def create_db(app : Flask, userdatastore:SQLAlchemyUserDatastore):
    with app.app_context():
        db.create_all()
        admin_role = userdatastore.find_or_create_role(name='admin', description='Admin Role')
        staff_role = userdatastore.find_or_create_role(name='staff', description='Staff Role')
        staff_role = userdatastore.find_or_create_role(name='user', description='User Role')

        if not userdatastore.find_user(email="admin@gmail.com"): 
            userdatastore.create_user(
            full_name="admin",
            email="admin@gmail.com",
            password="12345",
            roles = [admin_role, staff_role]
            
        )
            
        db.session.commit()

class Users(db.Model, UserMixin):
    __tablename__="users"
    
    id = db.Column(db.Integer, primary_key= True)
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150), nullable= False)
    phone  = db.Column(db.String(20),  nullable=True)
    active = db.Column(db.Boolean, default=True) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(255), unique=True, nullable=True)
    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy='dynamic'))
    
    
    def __repr__(self):
        return f'<User {self.full_name}>'



class Role(db.Model, RoleMixin):
    __tablename__="role"


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique= True)
    description = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'


class UserRole(db.Model):
    __tablename__="user_role"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'), nullable=False)

    def __repr__(self):
        return f'<UserRole user_id= {self.user_id} role_id= {self.role_id}>'




class TrekModel(db.Model):
    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    difficulty  = db.Column(db.Enum('easy', 'moderate', 'hard'), nullable=False)
    duration_days= db.Column(db.Integer, nullable=False)
    total_slots  = db.Column(db.Integer, nullable=False)  
    available_slots  = db.Column(db.Integer, nullable=False)   
    status = db.Column(db.Enum('pending', 'approved', 'open', 'closed', 'started', 'completed'),
                                 nullable=False, default='pending')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    assigned_staff = db.relationship('Users', foreign_keys=[assigned_staff_id], backref='assigned_treks')
    creator = db.relationship('Users', foreign_keys=[created_by], backref='created_treks')
    

    

class BookingModel(db.Model):
    __tablename__ = 'bookings'
    
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "trek_id",
            name="uq_user_trek"
        ),
    )
    id= db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id  = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    status = db.Column(db.Enum('booked', 'cancelled', 'completed', 'waitlist'),
                                nullable=False, default='booked')
    payment_status = db.Column(db.Enum('pending', 'paid', 'refunded'),
                                nullable=False, default='pending')
    created_at = db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    user = db.relationship('Users', backref='bookings')
    trek = db.relationship('TrekModel', backref='bookings') 
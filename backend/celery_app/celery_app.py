from celery import Celery
import smtplib
from models.models import db
from flask import render_template
from email.mime.text import MIMEText
from sqlalchemy import func
from datetime import datetime
from celery.schedules import crontab
from email.message import EmailMessage
from main import app
from datetime import date, timedelta
from models.models import Users, TrekModel, BookingModel
from collections import defaultdict
import csv

celery = Celery(
    'tasks',
    broker ='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery.conf.update(
    timezone = 'Asia/Kolkata',
    enable_utc=False
)




@celery.task()
def generate_csv(user_id):
    with app.app_context():
        user = Users.query.get(user_id)
        bookings = (
        BookingModel.query.join(TrekModel).filter(
        BookingModel.user_id == user_id
    ).all()
    )
        filename = f"booking_history_{user_id}.csv"

        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
            "User ID",
                "Trek Name",
                "Location",
                "Booking Status",
                "Start Date",
                "End Date"
        ])
            for booking in bookings:
                writer.writerow([
                booking.user_id,
                booking.trek.name,
                booking.trek.location,
                booking.status,
                booking.trek.start_date,
                booking.trek.end_date
                ]
                )
        
        send_csv_email(
            to_email=user.email,
            csv_file=filename
        )
        
        print(f"CSV generated: {filename}")
            

 
  

@celery.task()
def send_reminder():
    print("=" * 50)
    print("Running send_reminder()")
    print("=" * 50)
    with app.app_context():
        today = date.today()
    

        bookings = BookingModel.query.join(TrekModel).filter(
        BookingModel.status == "booked",
        TrekModel.start_date > today,
        BookingModel.payment_status == "paid"
    ).all()

        if not bookings:
            return
    
        user_bookings = defaultdict(list)

        for booking in bookings:
            user_bookings[booking.user_id].append(booking)

        for user_id, user_treks in user_bookings.items():
            user = user_treks[0].user

            subject = "Upcoming Trek Reminder"

            body = f"""
    Hello {user.full_name}
    You have following upcoming treks:


"""
            for booking in user_treks:

                trek = booking.trek

                days_left = (
                trek.start_date - today
            ).days

                body += (
                f"\n• {trek.name}"
                f"\n  Location: {trek.location}"
                f"\n  Start Date: {trek.start_date}"
                f"\n  Days Remaining: {days_left}\n"
            )

            body += "\nHappy Trekking!"

            print(body)
            # Email Sending implement will here
            send_email(user.email,subject,body)
            

@celery.task()
def monthly_report():
    with app.app_context():
        today = date.today()

        current_month_start = today.replace(day=1)

        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        print(last_month_start)
        print(last_month_end)

        treks_conducted = TrekModel.query.filter(
            TrekModel.status == "completed",
            TrekModel.end_date >= last_month_start,
            TrekModel.end_date <= last_month_end
        ).count()
        unique_participants = (
        db.session.query(
            BookingModel.user_id
        )
        .join(TrekModel)
        .filter(
            TrekModel.status == "completed",
            TrekModel.end_date >= last_month_start,
            TrekModel.end_date <= last_month_end
        )
        .distinct()
        .count()
    )
        total_participations = (
        BookingModel.query
        .join(TrekModel)
        .filter(
            TrekModel.status == "completed",
            TrekModel.end_date >= last_month_start,
            TrekModel.end_date <= last_month_end
        )
        .count()
    )
        popular_treks = (
        db.session.query(
            TrekModel.name,
            func.count(
                BookingModel.id
            ).label("participants")
        )
        .join(
            BookingModel,
            BookingModel.trek_id == TrekModel.id
        )
        .filter(
            TrekModel.status == "completed",
            TrekModel.end_date >= last_month_start,
            TrekModel.end_date <= last_month_end
        )
        .group_by(
            TrekModel.id,
            TrekModel.name
        )
        .order_by(
            func.count(
                BookingModel.id
            ).desc()
        )
        .limit(3)
        .all()
    )
        html = render_template(
        "monthly_report.html",
        month_year=last_month_start.strftime('%B %Y'),
        treks_conducted=treks_conducted,
        unique_participants=unique_participants,
        total_participations=total_participations,
        popular_treks=
            popular_treks
        ,
        generated_at=datetime.now().strftime("%d %B %Y %H:%M")
    )
        send_email("amanobaidofficial01@gmail.com","Monthly Trekking Report",html, is_html=True)




celery.conf.beat_schedule = {

    "monthly-admin-report": {
        "task": "celery_app.celery_app.monthly_report",
        "schedule": crontab(
            minute="*"
        ),
    },
    "daily-trek-reminder":{
        "task" : "celery_app.celery_app.send_reminder",
        "schedule" : crontab(
           minute="*"
        )
    }
}



SMTP_HOST = 'localhost'
SMTP_PORT = 1025
FROM_EMAIL = '23f3001161@ds.study.iitm.ac.in'
def send_email(to_email, subject, body, is_html=False):
    

    if is_html:
        msg = MIMEText(body, "html")
    else:
        msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT
    ) as server:

        server.send_message(msg)


import traceback

def send_csv_email(to_email, csv_file):
    try:
        

        msg = EmailMessage()

        msg["Subject"] = "Booking History Report"
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email

        msg.set_content(
            "Your booking history report is attached."
        )

        print(f"Opening file: {csv_file}")

        with open(csv_file, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="text",
                subtype="csv",
                filename=csv_file
            )

       

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)

        print(f"CSV emailed successfully to {to_email}")

    except Exception as e:
        
        print(f"Exception: {e}")
        traceback.print_exc()
       

from celery.schedules import crontab

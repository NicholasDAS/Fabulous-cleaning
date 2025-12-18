# this email_utils.py
# This file handles all outgoing emails in the system.
# It sends:
#  An email to the admin when a new booking is created
#  A confirmation email to the customer after booking


from flask_mail import Message
from flask import current_app
from extensions import mail


# send_admin_notification,that is to say send email to me when they have booked a service

def send_admin_notification(booking, user):
    """
    Sends an email to the admin to notify them that a customer
    has submitted a new booking.
    """

    admin_email = current_app.config["MAIL_USERNAME"]  # Your Gmail address

    msg = Message(
        subject="New Cleaning Booking Submitted",
        recipients=[admin_email],  # Admin receives the email here
        sender=admin_email
    )

    msg.body = f"""
A new cleaning booking has been received.

-------------------------
CUSTOMER INFORMATION
-------------------------
Name: {user.fullname}
Email: {user.email}
Phone: {user.phone}

-------------------------
BOOKING DETAILS
-------------------------
Service: {booking.service_type}
Date: {booking.date}
Address: {booking.address}
Rooms: {booking.rooms}
Notes: {booking.note}

Submitted On: {booking.created_at}

Login to your admin dashboard to view more details.
"""

    mail.send(msg)
    print("Admin notification sent.")



# customer confirmation email

def send_user_confirmation(user, booking):
    """
    Sends a confirmation email to the customer so they know
    their booking has been received.
    """

    sender_email = current_app.config["MAIL_USERNAME"]

    msg = Message(
        subject="Your Cleaning Booking is Confirmed!",
        recipients=[user.email],  # Customer receives this email
        sender=sender_email
    )

    msg.body = f"""
Hi {user.fullname},

Thank you for booking with Fabulous Cleaning Service!

Your booking has been received successfully.

-------------------------
BOOKING SUMMARY
-------------------------
Service: {booking.service_type}
Date: {booking.date}
Address: {booking.address}
Rooms: {booking.rooms} 
Notes: {booking.note}

We will contact you shortly to confirm the details.

Thank you once again!
— Fabulous Cleaning Team
"""

    mail.send(msg)
    print("Customer confirmation sent.")

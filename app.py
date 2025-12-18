# app.py - Main Flask Application


from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from config import Config
from extensions import db, mail
from models import User, Booking, ContactMessage
from flask_mail import Message


# ------------------- INITIALIZE APP -------------------
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)


# ------------------- CREATE DATABASE -------------------
with app.app_context():
    db.create_all()


# ------------------- LOGIN REQUIRED DECORATOR -------------------
def login_required(f):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect("/login")
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# ------------------- ADMIN REQUIRED -------------------
def admin_required(f):
    def wrapper(*args, **kwargs):
        if "user_id" not in session or not session.get("is_admin"):
            flash("Admin access only.")
            return redirect("/")
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# ------------------- ROUTES -------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


# ------------------- CONTACT -------------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        msg = ContactMessage(
            fullname=request.form["fullname"],
            email=request.form["email"],
            phone=request.form["phone"],
            message=request.form["message"]
        )
        db.session.add(msg)
        db.session.commit()
        flash("Message sent successfully!")
        return redirect("/contact")

    return render_template("contact.html")


# ------------------- SIGNUP -------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if User.query.filter_by(email=request.form["email"]).first():
            flash("Email already registered. Please log in.")
            return redirect("/signup")

        user = User(
            fullname=request.form["fullname"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please log in.")
        return redirect("/login")

    return render_template("signup.html")


# ------------------- LOGIN -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if not user or not check_password_hash(user.password, request.form["password"]):
            flash("Invalid email or password.")
            return redirect("/login")

        session["user_id"] = user.id
        session["fullname"] = user.fullname
        session["is_admin"] = user.is_admin
        flash("Login successful!")
        return redirect("/dashboard")

    return render_template("login.html")


# ------------------- LOGOUT -------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    bookings = Booking.query.filter_by(
        user_id=user.id
    ).order_by(Booking.created_at.desc()).all()

    return render_template(
        "dashboard.html",
        user=user,
        bookings=bookings,
        now=datetime.utcnow()
    )


# booking route
@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():
    if request.method == "POST":
        try:
            # ---------- SAVE PHOTOS ----------
            def save_pic(field):
                file = request.files.get(field)
                if file and file.filename:
                    filename = secure_filename(
                        f"{datetime.utcnow().timestamp()}_{file.filename}"
                    )
                    file.save(os.path.join(Config.BOOKING_FOLDER, filename))
                    return filename
                return None

            # ---------- CREATE BOOKING ----------
            booking = Booking(
                service_type=request.form["service_type"],
                date=request.form["date"],
                time=request.form["time"],
                rooms=request.form["rooms"],
                address=request.form["address"],
                note=request.form.get("note"),
                photo1=save_pic("photo1"),
                photo2=save_pic("photo2"),
                photo3=save_pic("photo3"),
                user_id=session["user_id"],
                status="Confirmed"
            )

            db.session.add(booking)
            db.session.commit()

            # ---------- EMAIL NOTIFICATION (NON-BLOCKING) ----------
            try:
                msg = Message(
                    subject="🧹 New Cleaning Booking Received",
                    recipients=[Config.MAIL_USERNAME],
                    body=(
                        "A new booking has been made.\n\n"
                        f"Customer: {session.get('fullname')}\n"
                        f"Service: {booking.service_type}\n"
                        f"Date: {booking.date}\n"
                        f"Time: {booking.time}\n"
                        f"Rooms: {booking.rooms}\n"
                        f"Address: {booking.address}\n"
                    )
                )
                mail.send(msg)
            except Exception as email_error:
                print("EMAIL ERROR:", email_error)
                # ---------- CUSTOMER AUTO-REPLY ----------
            try:
                customer = User.query.get(session["user_id"])

                reply = Message(
                    subject="✅ We’ve Received Your Booking",
                    recipients=[customer.email],
                    body=(
                        f"Hello {customer.fullname},\n\n"
                        "Thank you for choosing Fabulous Cleaning Services! ✨\n\n"
                        "We have successfully received your booking with the details below:\n\n"
                        f"Service: {booking.service_type}\n"
                        f"Date: {booking.date}\n"
                        f"Time: {booking.time}\n"
                        f"Address: {booking.address}\n\n"
                        "Our team is reviewing your request and will contact you shortly "
                        "to confirm availability or next steps.\n\n"
                        "If you have any questions, simply reply to this email.\n\n"
                        "Warm regards,\n"
                        "Fabulous Cleaning Services\n"
                        "📧 edakinicholas9@gmail.com"
                    )
                )
                mail.send(reply)

            except Exception as e:
                print("CUSTOMER EMAIL ERROR:", e)

            flash("Booking submitted successfully!")
            return redirect("/dashboard")

        except Exception as e:
            db.session.rollback()
            print("BOOKING ERROR:", e)
            flash("Booking failed. Please try again.")
            return redirect("/booking")

    # ---------- GET REQUEST ----------
    return render_template("booking.html")


# ============================================================
# STEP 2 — EDIT BOOKING (USER ONLY, BEFORE BOOKING DATE)
# ============================================================
@app.route("/booking/<int:id>/edit", methods=["POST"])
@login_required
def edit_booking(id):
    booking = Booking.query.get_or_404(id)

    if booking.user_id != session["user_id"]:
        flash("You are not allowed to edit this booking.")
        return redirect("/dashboard")

    today = datetime.utcnow().date()
    booking_date = datetime.strptime(booking.date, "%Y-%m-%d").date()

    if booking_date < today:
        flash("Past bookings cannot be edited.")
        return redirect("/dashboard")

    booking.service_type = request.form["service_type"]
    booking.date = request.form["date"]
    booking.time = request.form["time"]
    booking.rooms = request.form["rooms"]
    booking.address = request.form["address"]
    booking.note = request.form.get("note")
    booking.status = "Edited"

    db.session.commit()
    flash("Booking updated successfully.")
    return redirect("/dashboard")


# ------------------- PROFILE -------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        try:
            # 1️⃣ Update simple fields FIRST (fast)
            user.fullname = request.form["fullname"]

            # 2️⃣ Handle file upload separately
            pic = request.files.get("profile_pic")
            if pic and pic.filename:
                filename = secure_filename(pic.filename)
                filepath = os.path.join(Config.PROFILE_FOLDER, filename)
                pic.save(filepath)
                user.profile_pic = filename

            # 3️⃣ Commit ONCE
            db.session.commit()

            flash("Profile updated successfully!")
            return redirect("/profile")

        except Exception as e:
            db.session.rollback()
            print("PROFILE UPDATE ERROR:", e)
            flash("Profile update failed. Please try again.")
            return redirect("/profile")

    return render_template("profile.html", user=user)


# ------------------- ADMIN PANEL -------------------
@app.route("/admin")
@admin_required
def admin():
    return render_template(
        "admin_dashboard.html",
        users=User.query.all(),
        bookings=Booking.query.all(),
        messages=ContactMessage.query.all()
    )


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


# ------------------- RUN APP -------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)

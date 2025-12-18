# ============================================================
# models.py - Database models
# ============================================================

from datetime import datetime
from extensions import db


# -------------------- USER MODEL --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    profile_pic = db.Column(db.String(255), default="default.jpg")

    is_admin = db.Column(db.Boolean, default=False)

    bookings = db.relationship("Booking", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.fullname}>"


# ------------------- BOOKING MODEL -------------------
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    service_type = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    rooms = db.Column(db.String(20), nullable=False)

    address = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text)

    photo1 = db.Column(db.String(255))
    photo2 = db.Column(db.String(255))
    photo3 = db.Column(db.String(255))

    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ---------------- CONTACT MESSAGE MODEL -------------
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

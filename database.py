from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_login import UserMixin


# CREATED MODELS
# Available Venues will be stored here
class Venue(db.Model):
    __tablename__ = 'Venue'
    Admin = db.Column(db.String, db.ForeignKey(
        "Member.email_ID"), nullable=False)
    ID = db.Column(db.Integer, autoincrement=True, unique=True,
                   primary_key=True, nullable=False)
    Name = db.Column(db.String, nullable=False)
    Place = db.Column(db.String)
    Capacity = db.Column(db.Integer)
    shows = db.relationship('Show', foreign_keys='Show.V_ID', backref=db.backref(
        'venue_details'), cascade='delete')


# Available Shows in each venues will be stored here
class Show(db.Model):
    __tablename__ = 'Show'
    ID = db.Column(db.Integer, autoincrement=True,
                   primary_key=True, unique=True, nullable=False)
    Name = db.Column(db.String, nullable=False)
    Rating = db.Column(db.Integer, nullable=False)
    Tags = db.Column(db.String, nullable=False)
    Ticket_Price = db.Column(db.Integer, nullable=False)
    Time = db.Column(db.String, nullable=False)
    V_ID = db.Column(db.Integer, db.ForeignKey("Venue.ID"), nullable=False)
    Booked_tickets = db.Column(db.Integer, nullable=False)
    


# Information about booked tickets will be stored here
class Booking(db.Model):
    __tablename__ = 'Booking'
    Booking_ID = db.Column(db.Integer, autoincrement=True,
                           primary_key=True, unique=True, nullable=False)
    Show_ID = db.Column(db.Integer, db.ForeignKey("Show.ID"), nullable=False)
    User_email = db.Column(db.String, db.ForeignKey(
        "Member.email_ID"), nullable=False)
    Price = db.Column(db.Integer, db.ForeignKey(
        "Show.Ticket_Price"), nullable=False)
    Number_of_Tickets = db.Column(db.Integer, nullable=False)


# Information about the Users will be stored here with designation (Admin or member)
class Member(db.Model, UserMixin):
    __tablename__ = 'Member'
    First_name = db.Column(db.String, nullable=False)
    Last_name = db.Column(db.String, nullable=False)
    email_ID = db.Column(db.String, nullable=False,
                         unique=True, primary_key=True)
    Password = db.Column(db.String, nullable=False, unique=False)
    Designation = db.Column(db.String, nullable=False)
    Location = db.Column(db.String, nullable=True)
    def get_id(self):
        return (self.email_ID)
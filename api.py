from flask import Flask, request
from flask_restful import Api, Resource, marshal_with, fields, reqparse
from database import Venue, Show, Member, Booking
from database import db
import os
from werkzeug.exceptions import HTTPException
from flask import make_response
from datetime import datetime as dt
app = Flask(__name__)
api = (Api(app))

class NotFoundError(HTTPException):
    def __init__(self):
        self.response = make_response('The requested resource was not found!',404)

class AlreadyExistsError(HTTPException):
    def __init__(self):
        self.response = make_response('Resource already exists!',409)




#############API for Venue###########################
venue_output_fields = {
    'ID': fields.Integer,     
    'Name': fields.String,
    'Place': fields.String,
    'Capacity': fields.Integer,
}

venue_parser = reqparse.RequestParser()
venue_parser.add_argument('admin_email')
venue_parser.add_argument('venue_name')
venue_parser.add_argument('venue_place')
venue_parser.add_argument('venue_capacity')

class VenueAPI(Resource):

    @marshal_with(venue_output_fields)
    def post(self):
        args = venue_parser.parse_args()
        admin_email = args.get('admin_email')
        v_name = args.get('venue_name')
        v_place = args.get('venue_place')
        v_capacity = args.get('venue_capacity')
        #checking if venue with same name, place, capacity already exists
        venue=Venue.query.filter_by(Admin=admin_email,
                            Place=v_place, Name=v_name, Capacity=v_capacity).first()
        if not venue:
            new_venue = Venue(Admin=admin_email,
                            Place=v_place, Name=v_name, Capacity=v_capacity)
            db.session.add(new_venue)
            db.session.commit()
            return new_venue, 200
        else:
            raise AlreadyExistsError


    @marshal_with(venue_output_fields)
    def get(self, venue_id):
        venue=Venue.query.get(venue_id)
        if venue is not None:
            return venue, 200
        else:
            raise NotFoundError

    @marshal_with(venue_output_fields)
    def put(self,venue_id):
        args = venue_parser.parse_args()
        v_name = args.get('venue_name')
        v_place = args.get('venue_place')
        v_capacity = args.get('venue_capacity')
        venue = Venue.query.get(venue_id)
        if venue:
            venue.Name = v_name
            venue.Place = v_place
            venue.Capacity = v_capacity
            db.session.commit()
            return venue, 200
        else:
            raise NotFoundError

    def delete(self,venue_id):
        venue=Venue.query.get(venue_id)
        if venue:
            db.session.delete(venue)
            db.session.commit()
            return f'venue {venue_id} deleted', 200
        else:
            raise NotFoundError
        
   


#################API for Show#########################

show_output_fields = {
        'ID' :fields.Integer,
        'Name' :fields.String,
        'Rating' :fields.Integer,
        'Tags' :fields.String,
        'Time' :fields.String,
        'Ticket_Price' :fields.Integer,
        'V_ID':fields.Integer,
        'Booked_tickets': fields.Integer,

    }

show_parser = reqparse.RequestParser()
show_parser.add_argument('show_name')
show_parser.add_argument('show_rating')
show_parser.add_argument('show_tags')
show_parser.add_argument('show_time')
show_parser.add_argument('show_ticketprice')
show_parser.add_argument('show_VID')
show_parser.add_argument('show_bt')


class ShowAPI(Resource):

    @marshal_with(show_output_fields)
    def post(self):
        args = show_parser.parse_args()
        s_name = args.get('show_name')
        s_rating = args.get('show_rating')
        s_tags = args.get('show_tags')
        s_time = args.get('show_time')
        s_ticketprice = args.get('show_ticketprice')
        s_VID = args.get('show_VID')
        s_bt = args.get('show_bt')
        #checking if show with same name, rating, tags, time, ticketprice already exists
        show = Show.query.filter_by(Name=s_name, Rating=s_rating,Time=s_time,
                            Tags=s_tags, Ticket_Price=s_ticketprice, V_ID=s_VID, Booked_tickets=s_bt).first()
        
        if not show:
            new_show = Show(Name=s_name, Rating=s_rating,Time=s_time,
                            Tags=s_tags, Ticket_Price=s_ticketprice,V_ID=s_VID, Booked_tickets=s_bt)
            db.session.add(new_show)
            db.session.commit()
            return new_show, 200
        else:
            raise AlreadyExistsError

    
    @marshal_with(show_output_fields)
    def get(self, show_id):
        show=Show.query.get(show_id)
        if show is not None:
            return show, 200
        else:
            raise NotFoundError

    @marshal_with(show_output_fields)
    def put(self,show_id):
        args = show_parser.parse_args()
        s_name = args.get('show_name')
        s_rating = args.get('show_rating')
        s_tags = args.get('show_tags')
        s_time = args.get('show_time')
        s_ticketprice = args.get('show_ticketprice')
        show = Show.query.get(show_id)
        if show:
            show.Name = s_name
            show.Rating = s_rating
            show.Time = s_time
            show.Tags = s_tags
            show.Ticket_Price = s_ticketprice
            db.session.commit()
            return show, 200
        else:
            raise NotFoundError

    def delete(self,show_id):
        show=Show.query.get(show_id)
        if show:
            db.session.delete(show)
            db.session.commit()
            return f'show {show_id} deleted', 200
        else:
            raise NotFoundError



###########################API for Member######################

member_output_fields = {
        'First_name' : fields.String,
        'Last_name': fields.String,
        'email_ID': fields.String,
        'Password': fields.String,
        'Designation': fields.String,
        'Location': fields.String,
    } 

member_parser = reqparse.RequestParser()
member_parser.add_argument('m_fname')
member_parser.add_argument('m_lname')
member_parser.add_argument('m_email')
member_parser.add_argument('m_password')
member_parser.add_argument('m_designation')
member_parser.add_argument('m_location')

class MemberAPI(Resource):
    
    @marshal_with(member_output_fields)
    def post(self):
        args = member_parser.parse_args()
        m_fname = args.get('m_fname')
        m_lname = args.get('m_lname')
        m_email = args.get('m_email')
        m_password = args.get('m_password')
        m_designation = args.get('m_designation')
        m_location = args.get('m_location')
        #checking if member with same name, email, password, designation, location already exists
        member = Member.query.filter_by(First_name=m_fname, Last_name=m_lname, email_ID=m_email,
                            Password=m_password, Designation=m_designation)
        if not member:
            new_member = Member(First_name=m_fname, Last_name=m_lname, email_ID=m_email,
                            Password=m_password, Designation=m_designation)
            db.session.add(new_member)
            db.session.commit()
            return new_member, 200
        else:
            raise AlreadyExistsError

    @marshal_with(member_output_fields)
    def get(self,member_email):
        member=Member.query.get(member_email)
        if member is not None:
            return member, 200
        else:
            raise NotFoundError

    @marshal_with(member_output_fields)
    def put(self,member_email):
        args = member_parser.parse_args()
        m_fname = args.get('m_fname')
        m_lname = args.get('m_lname')
        m_email = args.get('m_email')
        m_password = args.get('m_password')
        m_designation = args.get('m_designation')
        m_location = args.get('m_location')
        member = Member.query.get(member_email)
        if member:
            member.First_name = m_fname
            member.Last_name = m_lname
            member.email_ID = m_email
            member.Password = m_password
            member.Designation = m_designation
            member.Location = m_location
            db.session.commit()
            return member, 200
        else:
            raise NotFoundError

    def delete(self,member_email):
        member=Member.query.get(member_email)
        f_name=member.First_name
        if member:
            db.session.delete(member)
            db.session.commit()
            return f'{f_name}\'s account has been deleted', 200
        else:
            raise NotFoundError


###############################API for Booking###########################################################

booking_output_fields = {
        'Booking_ID' : fields.Integer,
        'Show_ID': fields.Integer,
        'User_email': fields.String,
        'Price': fields.Integer,
        'Number_of_Tickets': fields.Integer,
    } 

booking_parser = reqparse.RequestParser()
booking_parser.add_argument('b_ID')
booking_parser.add_argument('b_sID')
booking_parser.add_argument('b_uemail')
booking_parser.add_argument('b_price')
booking_parser.add_argument('b_ticketnum')




class BookingAPI(Resource):
    @marshal_with(booking_output_fields)
    def post(self):
        args = booking_parser.parse_args()
        b_ID = args.get('b_ID')
        b_sID = args.get('b_sID')
        b_uemail = args.get('b_uemail')
        b_price = args.get('b_price')
        b_ticketnum = args.get('b_ticketnum')
        #checking if booking with same details already exists
        booking = Booking.query.filter_by(Booking_ID=b_ID, Show_ID=b_sID, User_email=b_uemail,
                            Price=b_price, Number_of_Tickets=b_ticketnum)
        if not booking:
            new_booking = Booking(Booking_ID=b_ID, Show_ID=b_sID, User_email=b_uemail,
                            Price=b_price, Number_of_Tickets=b_ticketnum)
            db.session.add(new_booking)
            db.session.commit()
            return new_booking, 200
        else:
            raise AlreadyExistsError


    @marshal_with(booking_output_fields)
    def get(self, booking_id):
        booking=Booking.query.get(booking_id)
        if booking is not None:
            return booking, 200
        else:
            raise NotFoundError


    @marshal_with(booking_output_fields)
    def put(self,booking_id):
        args = booking_parser.parse_args()
        
        booking = Booking.query.get(booking_id)
        if booking:
            booking.Booking_ID = args.get('b_ID')
            booking.Show_ID = args.get('b_sID')
            booking.User_email = args.get('b_uemail')
            booking.Price = args.get('b_price')
            booking.Number_of_Tickets =  args.get('b_ticketnum')
            db.session.commit()
            return booking, 200
        else:
            raise NotFoundError

    def delete(self,booking_id):
        booking=Booking.query.get(booking_id)
        if booking:
            db.session.delete(booking)
            db.session.commit()
            return f'show {booking_id} deleted', 200
        else:
            raise NotFoundError










    
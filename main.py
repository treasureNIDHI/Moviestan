# Imported requirements

from flask_cors import CORS
from flask import flash
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, fields, marshal_with, reqparse
from flask_login import LoginManager, UserMixin, login_required, current_user, logout_user, login_user
from database import Venue, Show, Booking, Member, db
from api import VenueAPI, ShowAPI, MemberAPI, BookingAPI
login_manager = LoginManager()


# Connected database
app = Flask(__name__)
CORS(app)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.app_context().push()
login_manager.init_app(app)
app.config["SECRET_KEY"] = 'abcdefghijkl'
app.app_context().push()
# Api
api = Api(app)
app.app_context().push()


## Defining APIs
api.add_resource(VenueAPI,'/api/venue','/api/venue/<int:venue_id>')
api.add_resource(ShowAPI,'/api/show','/api/show/<int:show_id>')
api.add_resource(MemberAPI,'/api/member','/api/member/<string:member_email>')
api.add_resource(BookingAPI,'/api/booking','/api/booking/<int:booking_id>')



# Loading the details of user
@login_manager.user_loader
def load_user(email_ID):
    return Member.query.filter_by(email_ID=email_ID).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


# Route for index page(home page)
@app.route("/", methods=["GET", "POST"])
# function for index page
def index():
    # returning index page
    return render_template("index.html",current_user=current_user)


# Route for signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    # users can signup themselves
    if request.method == "GET":
        return render_template("SignUp.html")
    else:
        new_member = Member(First_name=request.form['First_name'], Last_name=request.form['Last_name'],
                            Designation=request.form['Designation'], Password=request.form['Password'], email_ID=request.form['email_ID'])
        db.session.add(new_member)
        db.session.commit()
        return redirect(url_for("login"))


@app.route("/location", methods=["GET","POST"])
def location():
    locations = Venue.query.with_entities(Venue.Place).all()
    locations = set(i[0] for i in locations)
    print(locations)
    print(current_user.Location,'b')
    return render_template('location.html', current_user=current_user, locations = locations)

@app.route("/location/<string:loc>", methods=["GET"])
def set_location(loc):
    # member= Member.query.filter_by(email_ID=current_user.email_ID)
    # member.Location=loc
    current_user.Location=loc
    db.session.commit()
    # print(member.Location,'a')
    print(current_user.Location,'a2')
    return redirect(url_for("location"))


# Route for login page
@app.route("/login", methods=["GET", "POST"])
# function for login
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            if current_user.Designation == 'admin':
                halls = Venue.query.filter_by(
                    Admin=current_user.email_ID).all()
                return render_template("admin.html", Venues=halls, create='False', current_user=current_user)
            else:
                shows = Show.query.filter(int(Show.venue_details.Capacity) > 0).all()
                return render_template("user.html", Venues=shows, current_user=current_user)

        return render_template('LogIn.html', current_user=current_user)
    else:
        # Checking password
        User_admin = Member.query.filter_by(
            email_ID=request.form['email_ID']).first()
        if User_admin:
            if User_admin.Password == request.form['Password']:
                login_user(User_admin, remember=True)
                # Checking if the user is admin
                # if the user is admin, it will show all the venues created by that particular admin
                # if request.form.get("admin") and User_admin.Designation == 'admin':
                if User_admin.Designation == 'admin':
                    admin = request.form['email_ID']
                    halls = Venue.query.filter_by(Admin=admin).all()
                    print(halls)
                    flash("you are successfully logged in")
                    return render_template("admin.html", Venues=halls, create="False", current_user=current_user)
                # if the user is not admin, it will render the member page with all the shows
                shows = Show.query.all()
                """[print(s.venue_details.Name) for s in shows] """
                return render_template("user.html", Venues=shows, current_user=current_user)
            else:
                # flash("incorrect username or password")
                return "Incorrect Credentials"
            """if the user has already logged in"""
        elif current_user.is_authenticated:
            if current_user.Designation == 'admin':
                halls = Venue.query.filter_by(
                    Admin=current_user.email_ID).all()
                return render_template("admin.html", Venues=halls, create='False', current_user=current_user)
            else:
                shows = Show.query.filter(int(Show.venue_details.Capacity) > 0).all()
                return render_template("user.html", Venues=shows, current_user=current_user)

# Route for logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/admin_dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    if request.method=="GET":
        halls = Venue.query.filter_by(Admin=current_user.email_ID).all()
        return render_template("admin.html", Venues=halls, create='False',current_user=current_user)


# Route for adding venue
@app.route("/add_venue", methods=["GET", "POST"])
@login_required
# function for adding venue by admin
def add_venue():
    # it will render admin page with venues
    if request.method == "GET":
        return render_template("admin.html", create='True', current_user=current_user)
    else:
        # it will accept response from the form that is in admin page and create a new venue
        new_venue = Venue(Admin=current_user.email_ID,
                          Place=request.form['Place'], Name=request.form['Name'], Capacity=request.form['Capacity'])
        db.session.add(new_venue)
        db.session.commit()
        halls = Venue.query.filter_by(Admin=current_user.email_ID).all()
        return redirect(url_for('dashboard'))
        
# Route for editing the venue details(only admin)


@app.route("/<int:ID>/edit_venue", methods=["GET", "POST"])
@login_required
def edit_venue(ID):
    # it will render edit page
    if request.method == "GET":
        venue=Venue.query.filter_by(ID=ID).first()
        return render_template("edit.html", venue=venue)
    else:
        # it will accept changes from the form that is edit page
        venue = Venue.query.filter_by(ID=ID).first()
        
        venue.Place=request.form['Place']
        venue.Name=request.form['Name']
        venue.Capacity=request.form['Capacity']
        db.session.commit() 
        return redirect(url_for("dashboard"))

# Route for deleting the venue
@app.route("/<int:ID>/delete", methods=["GET"])
def delete_venue(ID):
    # Admin can delete the venue details
    venue = Venue.query.filter_by(ID=ID).first()
    db.session.delete(venue)
    db.session.commit()
    return redirect(url_for('login'))

# Route for shows (from admin page)


@app.route("/<int:ID>/shows", methods=["GET", "POST"])
@login_required
def shows(ID):
    # From ID of venue, we can get details of all the shows that is available in that particular venue
    if request.method == "GET":
        show = Show.query.filter_by(V_ID=ID).all()
        name=Venue.query.filter_by(ID=ID).first().Name
        return render_template("show.html", create="False", shows=show, VID=ID, venue=name)



# Route for create shows


# @app.route("/shows/create_show/<int:ID>", methods=["GET", "POST"])
@app.route("/<string:ID>/add_show", methods=["GET", "POST"])
def add_show(ID):
    if request.method == "GET":
        return render_template("show.html", create="True", VID=ID)
    else:
        to_print = request.form['Time']
        new_show = Show(Booked_tickets=0,Time=to_print, Name=request.form['Name'], Rating=request.form['Rating'],
                        Tags=request.form['Tags'], Ticket_Price=request.form['Ticket_Price'],V_ID=ID)
        db.session.add(new_show)
        db.session.commit()
        # return redirect('show.html')

        return redirect(url_for("shows",ID=ID))

# Route for edit the details of already existed shows

@app.route("/<int:VID>/<int:ID>/edit", methods=["GET", "POST"])
def edit_show(VID,ID):
    if request.method == "GET":
        show=Show.query.filter_by(ID=ID).first()
        return render_template("s_edit.html",VID=VID,ID=ID,s=show)
    else:
        show = Show.query.filter_by(ID=ID).first()
        show.Rating=request.form['Rating'] 
        show.Name=request.form['Name']
        show.Tags=request.form['Tags'] 
        show.Ticket_Price=request.form['Ticket_Price']
        db.session.commit()
        return redirect(url_for("shows", ID=VID))

# Route for delete the show


@app.route("/<int:VID>/<int:ID>/delete", methods=["GET", "POST"])
def delete_show(VID,ID):
    show = Show.query.filter_by(ID=ID).first()
    booking = Booking.query.filter_by(Show_ID=ID).all()
    for i in booking:
        db.session.delete(i)
    db.session.delete(show)
    db.session.commit()
    return redirect(url_for('shows',ID=VID))

# Route for show booking
@app.route("/<int:VID>/<int:SID>/book_show", methods=["GET", "POST"])
def book_show(VID, SID):
    show = Show.query.filter_by(ID=SID).first()
    if request.method == "POST":
        if show.Booked_tickets + int(request.form["Number_of_Tickets"]) <= show.venue_details.Capacity:
        
            book_data = Booking(Show_ID=show.ID, User_email=current_user.email_ID, Price=show.Ticket_Price
                                , Number_of_Tickets=int(request.form['Number_of_Tickets']))
            
            show.Booked_tickets+=int(request.form['Number_of_Tickets'])
            db.session.add(book_data)
            db.session.commit()
            return redirect(url_for('booked', ID=current_user.email_ID))
        
    return render_template('book.html', show=show, VID = VID)


@app.route("/user/profile/<string:ID>", methods=["GET","POST"])
def booked(ID):
    if request.method=="GET":
        # User = Member.query.filter_by(email_ID=ID).first()
        
        booked_shows = Booking.query.filter_by(User_email=ID).all()
        booked_dict={}
        for booking in booked_shows:
            print(Show.query.filter_by(ID=booking.Show_ID).first())
            booked_dict[booking.Booking_ID]=Show.query.filter_by(ID=booking.Show_ID).first().Name
        return render_template("booked.html", booked_show=booked_shows, booked_dict=booked_dict)


# Route for search
@app.route("/search", methods=["GET", "POST"])
def show_list():
    # It will match if the searched data present in the database
    searched = request.args.get('searched')
    if searched != "":
        venues = Venue.query.filter((Venue.Name.contains(searched)),(Venue.Place==current_user.Location)).all()
        # venues.extend(Venue.query.filter())
        print(venues)
        shows=[]
        for venue in venues:
            if request.args.get('rating'):
                show=Show.query.filter((Show.V_ID==venue.ID),Show.Rating>=request.args.get('rating'))
            else:
            
                show = Show.query.filter((Show.V_ID==venue.ID)).all()
            for i in show:
                print(i.venue_details.Place)
            shows.extend(show)
        show_list=Show.query.filter(Show.Name.contains(searched)).all()
        for i in show_list:
            if i.venue_details.Place==current_user.Location:
                shows.append(i)

            
            
        print(shows, venues)
        
    
    else:
        return render_template("index.html")
    return render_template("user.html", Venues = shows, create=False)







@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


# To run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)

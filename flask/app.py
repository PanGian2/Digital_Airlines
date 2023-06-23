from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response, session
from bson.objectid import ObjectId
from datetime import timedelta
from markupsafe import escape
import json, os, sys

sys.path.append('./data')

# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')


# Choose DigitalAirlines database
db = client["DigitalAirlines"]
users = db["Users"]
flights = db["Flights"]
bookings = db["Bookings"]

# Initiate Flask App
app = Flask(__name__)
app.secret_key = "thisshouldbeabettersecret"
#The session for both types of users expires after 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)


def is_logged_in():
    '''
    Checks if there is a user logged in the system
    '''
    return "username" in session


def is_user():
    '''
    Checks if the current user is a simple user
    '''
    user = users.find({"type": "User"})
    for u in user:
        if session["username"] == u["username"]:
            return True
    return False


def is_admin():
    '''
    Checks if the current user is an admin
    '''
    return session["username"] == "admin1" or session["username"] == "admin2"

#Home Route
@app.route("/", methods=["GET"])
def home():
    return "<h1>Welcome to Digital Airlines</h1> <h3>Click <a href='/login'>HERE</a> to login</h3>"

#Registration route. Method GET returns the form and method POST creates a user
@app.route("/register", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        data = None
        form = request.form
        try:
            #determine if data is from a form or from json (aka POSTMAN)
            if form:
                data = request.form
            else:
                data = json.loads(request.data)
        except Exception as e:
            return Response("bad json content", status=400, mimetype="application/json")
        if data == None:
            return Response("bad request", status=400, mimetype="application/json")

        #Neccesary fields in order to create user
        if (
            not "email" in data
            or not "password" in data
            or not "username" in data
            or not "fullName" in data
            or not "birthDate" in data
            or not "country" in data
            or not "passportNo" in data
        ):
            return Response(
                "Information incomplete", status=500, mimetype="application/json"
            )

        # Check if there is a user with the same email or username
        if (users.count_documents({"$or": [{"email": data["email"]}, {"username": data["username"]}]}) == 0):
            #Create user with the 'escaped' data
            user = {
                "email": escape(data["email"]),
                "password": escape(data["password"]),
                "username": escape(data["username"]),
                "fullName": escape(data["fullName"]),
                "birthDate": escape(data["birthDate"]),
                "country": escape(data["country"]),
                "passportNo": escape(data["passportNo"]),
                "type": "User",
            }
            # Add user to the 'users' collection
            users.insert_one(user)
            return Response(data["email"] + " was added to the system", status=200, mimetype="application/json")
        else:
            return Response("A user with the given email or username already exists", status=400, mimetype="application/json")
    else:
        #HTML FORM 
        return ''' 
        <h1>Register</h1>
        <form action="" method="post">
            <p><input type=text name=username placeholder="Enter your username" required/></p>
            <p><input type=text name=email placeholder="Enter your email" required/></p>
            <p><input type=password name=password placeholder="Enter your password" required/></p>
            <p><input type=text name=fullName placeholder="Enter your full name" required/></p>
            <p><label>Birth Date: </label><input type=date name=birthDate required/></p>
            <p><input type=text name=country placeholder="Enter your country" required/></p>
            <p><input type=number name=passportNo placeholder="Enter your passport number" required/></p>
            <button type=submit>Register</button>
        </form>
        '''

#Login route. Method GET returns the form and method POST creates a session for the user
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = request.form
        data = None
        try:
            #determine if data is from a form or from json (aka POSTMAN)
            if form:
                data = request.form
            else:
                data = json.loads(request.data)
        except Exception as e:
            return Response("bad json content", status=400, mimetype="application/json")
        if data == None:
            return Response("bad request", status=400, mimetype="application/json")
        
        #Check if user provided the necessary credentials
        if not "email" in data or not "password" in data:
            return Response("Information incomplete", status=400, mimetype="application/json")
        
        user = users.find_one(
            {"$and": [{"email": escape(data["email"])}, {"password": escape(data["password"])}]}
        )
        #If user exists create a cookie with their username
        if user != None: 
            if is_logged_in():
                session.pop("username", None)
            session["username"] = user["username"]
            session.permanent = True
            return Response("Welcome", status=200, mimetype="application/json")
        return Response("Invalid credentials. Please try again!", status=401, mimetype="application/json")
    else:
        #HTML FORM
        return ''' 
        <form action="" method="post">
            <p><input type=text name=email placeholder="Enter your email" /></p>
            <p><input type=password name=password placeholder="Enter your password" /></p>
            <button type=submit>Login</button>
            <button><a href='/register'>Register now!</a></button>
        </form>
        '''

#Logout route. Deletes the active session for the user
@app.route("/logout", methods=["GET"])
def logout():
    if "username" in session:
        session.pop("username", None)
        return Response("You logged out successfully!", status=200, mimetype="application/json")
    else:
        return Response("You are already logged out!", status=200, mimetype="application/json")


#Flights route. Available for both simple user and admin
@app.route("/flights", methods=["GET"])
def get_flights():
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        #Check if the user provided arguments
        args = request.args
        if args:
            depAirport = args.get("departAirport")
            destAirport = args.get("destAirport")
            flightDate = args.get("flightDate")

            #All three filters were provided
            if (depAirport is not None and destAirport is not None and flightDate is not None):
                iterable = flights.find({
                    "$and": [
                        {"departAirport": depAirport},
                        {"destAirport": destAirport},
                        {"flightDate": flightDate}
                    ]
                })
                output = []
                
                #Print the id of the flight, the departure airport, the destination airport and the date of the flight
                for flight in iterable:
                    f = {
                        "_id": str(flight["_id"]),
                        "departAirport": flight["departAirport"],
                        "destAirport": flight["destAirport"],
                        "flightDate": flight["flightDate"],
                    }
                    output.append(f)
                return jsonify(output)
            
            #Only departure airport and destination airport were provided
            elif (depAirport is not None and destAirport is not None and flightDate is None):
                iterable = flights.find({
                    "$and": [
                        {"departAirport": depAirport},
                        {"destAirport": destAirport},
                    ]
                })
                output = []

                #Print the id of the flight, the departure airport, the destination airport and the date of the flight
                for flight in iterable:
                    f = {
                        "_id": str(flight["_id"]),
                        "departAirport": flight["departAirport"],
                        "destAirport": flight["destAirport"],
                        "flightDate": flight["flightDate"],
                    }
                    output.append(f)
                return jsonify(output)
            
            #Only flight date was provided
            elif depAirport is None and destAirport is None and flightDate is not None:
                iterable = flights.find({"flightDate": flightDate})
                output = []

                #Print the id of the flight, the departure airport, the destination airport and the date of the flight
                for flight in iterable:
                    f = {
                        "_id": str(flight["_id"]),
                        "departAirport": flight["departAirport"],
                        "destAirport": flight["destAirport"],
                        "flightDate": flight["flightDate"],
                    }
                    output.append(f)
                return jsonify(output)
            else:
                return Response("The query parameter is not valid", status=400, mimetype="application/json")
        else:
            iterable = flights.find({})
            output = []
            for flight in iterable:
                f = {
                    "_id": str(flight["_id"]),
                    "departAirport": flight["departAirport"],
                    "destAirport": flight["destAirport"],
                    "flightDate": flight["flightDate"],
                }
                output.append(f)
            return jsonify(output)


#Specific flight route. Prints information about a specific flight depending on the user type
@app.route("/flights/<id>", methods=["GET"])
def get_flights_byId(id):
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    if id == None:
        return Response("Bad request", status=400, mimetype="application/json")
    
    #Find flight based on the given id
    flight = flights.find_one({"_id": ObjectId(id)})
    output = []
    if flight != None:
        if is_user():
            #Prints all the details of the flight
            flight["_id"] = str(flight["_id"])
            return jsonify(flight)
        elif is_admin():
            #Prints the details of the flight and the name, last name and ticket type of every booking in this flight
            flight["_id"] = str(flight["_id"])
            output.append(flight)
            booking = bookings.find({"flightID": ObjectId(id)})
            output.append("Bookings")
            for b in booking:
                traveller = {"name": b["firstName"], "lastName": b["lastName"], "ticketType": b["ticketType"]}
                output.append(traveller)
            return jsonify(output)
    return Response("No flight found", status=500, mimetype="application/json")


#Update a flight route. Only available for admins.
@app.route("/flights/<id>", methods=["PUT"])
def update_flights_byId(id):
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_user():
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    
    #Take data from body
    data = None
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content", status=400, mimetype="application/json")
    if data == None:
        return Response("bad request", status=400, mimetype="application/json")
    if id == None:
        return Response("Bad request", status=400, mimetype="application/json")
    if not "businessTicketCost" in data or not "economyTicketCost" in data:
        return Response("Information incompleted", status=400, mimetype="application/json")
    if type(data["businessTicketCost"]) == str:
        return Response("Bad json content. BusinessTicketCost must be an integer", status=400, mimetype="application/json")
    if type(data["economyTicketCost"]) == str:
        return Response("Bad json content. EconomyTicketCost must be an integer", status=400, mimetype="application/json")

    #Find the flight with the given id
    flight = flights.find_one({"_id": ObjectId(id)})
    if flight != None:
        flight = {"_id": ObjectId(id)}
        #Only the ticket costs can be changed
        new_values = {
            "$set": {
                "businessTicketCost": data["businessTicketCost"],
                "economyTicketCost": data["economyTicketCost"],
            }
        }
        flights.update_one(flight, new_values)
        return Response("Ticket costs were updated successfully", status=200, mimetype="application/json")
    return Response("No flight found", status=500, mimetype="application/json")


#Delete a flight route. Only available for admins.
@app.route("/flights/<id>", methods=["DELETE"])
def delete_flight(id):
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_user():
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    if id == None:
        return Response("Bad request", status=400, mimetype="application/json")
    
    #Find the flight with the given id
    flight = flights.find_one({"_id": ObjectId(id)})
    if flight != None:
        #A flight with bookings can't be deleted
        if bookings.find_one({"flightID": ObjectId(id)}):
            return Response("You can't delete this flight, as there are bookings for it", status=200, mimetype="application/json")
        
        flights.delete_one(flight)
        return Response("Flight was deleted successfully", status=200, mimetype="application/json")
    return Response("No flights found", status=500, mimetype="application/json")


#Create a flight route. Only available for admins. The method GET returns the form and the method POST creates a flight
@app.route("/flights/new", methods=["GET", "POST"])
def create_flight():
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_user():
            return Response("You are not authorized to enter this page!", status=403, mimetype="application/json")
    
    if request.method == "POST":
        form = request.form
        data = None
        try:
            #Determine if data is from a form or from json (aka POSTMAN)
            if form:
                data = request.form.to_dict()
            else:
                data = json.loads(request.data)
        except Exception as e:
            return Response("bad json content", status=400, mimetype="application/json")
        if data == None:
            return Response("bad request", status=400, mimetype="application/json")
        
        #Necessary fields to create a flight
        if (not "businessAvailableTickets" in data
            or not "businessTicketCost" in data
            or not "departAirport" in data
            or not "destAirport" in data
            or not "economyAvailableTickets" in data
            or not "economyTicketCost" in data
            or not "flightDate" in data
        ):
            return Response("Information incompleted", status=400, mimetype="application/json")

        
        try:
            data["businessTicketCost"] = float(data["businessTicketCost"])
            data["businessAvailableTickets"] = int(data["businessAvailableTickets"])
            data["economyTicketCost"] = float(data["economyTicketCost"])
            data["economyAvailableTickets"] = int(data["economyAvailableTickets"])
        except Exception as e:
            print(e)
            return Response("Bad json content. The available tickets and costs must numbers", status=400, mimetype="application/json")
       

        #Create a flight and add it to 'flights' collection
        flight = {
            "businessAvailableTickets": data["businessAvailableTickets"],
            "businessTicketCost": data["businessTicketCost"],
            "departAirport": escape(data["departAirport"]),
            "destAirport": escape(data["destAirport"]),
            "economyAvailableTickets": data["economyAvailableTickets"],
            "economyTicketCost": data["economyTicketCost"],
            "flightDate": escape(data["flightDate"]),
        }
        flights.insert_one(flight)
        return Response("Flight was added successfully", status=200, mimetype="application/json")
    else:
        #HTML FORM
        return '''
        <h1>New Flight</h1>
        <form action="" method="post">
            <p>
                <label>Departure Airport: </label>
                <input type=text name=departAirport placeholder="Enter the departure airport" required/>
            </p>
            <p>
                 <label>Destination Airport: </label>
                <input type=text name=destAirport placeholder="Enter the destination airport" required/>
            </p>
            <p>
                <label>Flight Date: </label>
                <input type=date name=flightDate placeholder="Enter the flight date" required/>
            </p>
            <p>
                <label>Available tickets for business class: </label>
                <input type=number name=businessAvailableTickets placeholder="Enter business available tickets" required/>
            </p>
            <p>
                <label>Ticket cost for business class: </label>
                <input type=number name=businessTicketCost placeholder="Enter business ticket cost" required/>
            </p>
            <p>
                <label>Available tickets for economy class: </label>
                <input type=number name=economyAvailableTickets placeholder="Enter economy available tickets" required/>
            </p>
            <p>
                <label>Ticket cost for economy class: </label>
                <input type=number name='economyTicketCost' placeholder="Enter economy ticket cost" required/>
            </p>
            <button type=submit>Submit</button>
        </form>
        '''


#Create a booking for a flight route. Only available to users. The method GET returns the form and the method POST creates a booking
@app.route("/bookings/new/<flight_id>", methods=["GET", "POST"])
def post_new_booking(flight_id):
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_admin():
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    if flight_id == None:
        return Response("Bad request", status=400, mimetype="application/json")
    
    if request.method == "POST":
        data = None
        form = request.form
        try:
            #Determine if data is from a form or from json (aka POSTMAN)
            if form:
                data = request.form
            else:
                data = json.loads(request.data)
        except Exception as e:
            return Response("bad json content", status=400, mimetype="application/json")
        if data == None:
            return Response("bad request", status=400, mimetype="application/json")
        
        #Necessary fields to create a booking
        if (
            not "firstName" in data
            or not "lastName" in data
            or not "email" in data
            or not "passportNo" in data
            or not "birthDate" in data
            or not "ticketType" in data
        ):
            return Response("Information incompleted", status=400, mimetype="application/json")

        #Ticket type must be only 'economy' or 'business'
        if (data["ticketType"] != "economy" and data["ticketType"] != "business"):
            return Response("Ticket Type must business or economy", status=400, mimetype="application/json")
        
        #Find the flight with te given id
        flight = flights.find_one({"_id": ObjectId(flight_id)})
        if flight != None:
            #Check if there are tickets left
            if (data["ticketType"] == "economy" and int(flight["economyAvailableTickets"]) == 0):
                return Response("Not Available Tickets left!", status=200, mimetype="application/json")
            elif (data["ticketType"] == "business" and int(flight["businessAvailableTickets"]) == 0):
                return Response("Not Available Tickets left!", status=200, mimetype="application/json")
            
            #We add the flightID to demonstrate the One-to-Many relationship with the 'flights' collection
            booking = {
                "firstName": escape(data["firstName"]),
                "lastName": escape(data["lastName"]),
                "passportNo": escape(data["passportNo"]),
                "birthDate": escape(data["birthDate"]),
                "email": escape(data["email"]),
                "ticketType": escape(data["ticketType"]),
                "departAirport": flight["departAirport"],
                "destAirport": flight["destAirport"],
                "flightDate": flight["flightDate"],
                "flightID": ObjectId(flight_id),
            }

            #Add booking to 'bookings' collection
            bookings.insert_one(booking)

            #Update the available tickets for this flight
            if data["ticketType"] == "economy":
                tickets = int(flight["economyAvailableTickets"]) - 1
                print(tickets)
                flights.update_one(
                    {"_id": ObjectId(flight_id)},
                    {"$set": {"economyAvailableTickets": tickets}},
                )
            elif data["ticketType"] == "business":
                tickets = flight["businessAvailableTickets"] - 1
                flights.update_one(
                    {"_id": ObjectId(flight_id)},
                    {"$set": {"businessAvailableTickets": tickets}},
                )
            return Response("You successfully booked the ticket!", status=200, mimetype="application/json")
        return Response("No flight found", status=500, mimetype="application/json")
    else: 
        #HTML FORM
        return ''' 
        <h1>New Booking</h1>
        <form action="" method="post">
            <p><input type=text name=firstName placeholder="Enter your name" required/></p>
            <p><input type=text name=lastName placeholder="Enter your last name" required/></p>
            <p><input type=number name=passportNo placeholder="Enter your passport number" required/></p>
            <p><input type=text name=email placeholder="Enter your email" required/></p>
            <p><input type=date name=birthDate placeholder="Enter your birth date" required/></p>
            <p><select name=ticketType required>
                <option value="">Choose a ticket type</option>
                <option value="economy">Economy</option>
                <option value="business">Business</option>
               </select>
            </p>          
            <button type=submit>Submit</button>
        </form>
        '''

#Bookings route. Returns all the bookings done by the user. Only available for users
@app.route("/bookings", methods=["GET"])
def get_bookings():
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_admin():
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    
    #Get the information of the connected user
    user = users.find_one({"username": session["username"]})
    #Find all the bookings with the user's email
    iterable = bookings.find({"email": user["email"]})
    if iterable != None:
        output = []
        for booking in iterable:
            booking["_id"] = str(booking["_id"])
            booking["flightID"] = str(booking["flightID"])
            output.append(booking)
        return jsonify(output)
    return Response("No bookings found", status=500, mimetype="application/json")

#Specific booking route. Returns all the information of a specific booking of the user. Only available to users
@app.route("/bookings/<id>", methods=["GET"])
def get_booking_byID(id):
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_admin():
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    if id == None:
        return Response("Bad request", status=400, mimetype="application/json")

    #Get the information of the connected user
    user = users.find_one({"username": session["username"]})
    booking = bookings.find_one({"_id": ObjectId(id)})
    if booking != None:
        #Check if the booking was done by the connected user
        if booking["email"] == user["email"]:
            booking["_id"] = str(booking["_id"])
            booking["flightID"] = str(booking["flightID"])
            return jsonify(booking)
        else:
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    return Response("No bookings found", status=500, mimetype="application/json")

#Delete a booking route. Only available to users
@app.route("/bookings/<id>", methods=["DELETE"])
def delete_booking_byID(id):
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_admin():
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    if id == None:
        return Response("Bad request", status=500, mimetype="application/json")
    
    #Get the information of the connected user
    user = users.find_one({"username": session["username"]})
    booking = bookings.find_one({"_id": ObjectId(id)})
    if booking != None:
        #Check if the booking was done by the connected user
        if booking["email"] == user["email"]:
            bookings.delete_one(booking)

            #Update the available tickets left of the corresponding flight
            flight = flights.find_one({"_id": booking["flightID"]})
            if booking["ticketType"] == "economy":
                ticket = int(flight["economyAvailableTickets"]) + 1
                flights.update_one({"_id": booking["flightID"]}, {"$set": {"economyAvailableTickets": ticket}})

            elif booking["ticketType"] == "business":
                ticket = int(flight["businessAvailableTickets"]) + 1
                flights.update_one({"_id": booking["flightID"]}, {"$set": {"businessAvailableTickets": ticket}})

            return Response("Booking was deleted successfully!", status=200, mimetype="application/json")
        else:
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    return Response("no bookings found", status=500, mimetype="application/json")

#Delete user route. Only available for users
@app.route("/user/delete", methods=["DELETE"])
def delete_user():
    if not is_logged_in():
        return Response("You must login in this page", status=401, mimetype="application/json")
    else:
        if is_admin():
            return Response("You are not authorized to enter this page", status=403, mimetype="application/json")
    
    #Get the information of the connected user
    user = users.find_one({"username": session["username"]})
    if user != None:
        users.delete_one(user)
        #Deletes the active session of the user
        session.pop("username", None)
        return Response("Was deleted", status=200, mimetype="application/json")
    return Response("No users found", status=500, mimetype="application/json")
                


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

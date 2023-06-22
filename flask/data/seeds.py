from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json, os

# Connect to our local MongoDB
mongodb_hostname = os.environ.get("MONGO_HOSTNAME","localhost")
client = MongoClient('mongodb://'+mongodb_hostname+':27017/')

# Choose DigitalAirlines database
db = client["DigitalAirlines"]
user = db["Users"]
flights = db["Flights"]
booking = db["Bookings"]


users = [
    {
        "username": "user1",
        "fullName": "George Papadopoulos",
        "email": "gp@gmail.com",
        "password": "123",
        "birthDate": "01-01-2002",
        "country": "Greece",
        "passportNo": "98765",
        "type": "User"
    },
    {
        "username": "user2",
        "fullName": "Maria Georgiou",
        "email": "mg@gmail.com",
        "password": "123",
        "birthDate": "01-02-2002",
        "country": "Greece",
        "passportNo": "87654",
        "type": "User"
    },
    {
        "username": "user3",
        "fullName": "Helen Suarez",
        "email": "hs@gmail.com",
        "password": "123",
        "birthDate": "02-01-2001",
        "country": "Spain",
        "passportNo": "13579",
        "type": "User"
    },
    {
        "username": "admin1",
        "fullName": "Nick Giannopoulos",
        "email": "np@gmail.com",
        "password": "admin",
        "birthDate": "01-03-2000",
        "country": "Greece",
        "passportNo": "76543",
        "type": "Admin"
    },
    {
        "username": "admin2",
        "fullName": "Ioanna Androutsou",
        "email": "ia@gmail.com",
        "password": "admin",
        "birthDate": "01-09-2001",
        "country": "Greece",
        "passportNo": "23456",
        "type": "Admin"
    },
]

user.insert_many(users)

flight = {
        "businessAvailableTickets": 50,
        "businessTicketCost": 150,
        "departAirport": "El. Benizelos (ATH)",
        "destAirport": "El Prat (BCN)",
        "economyAvailableTickets": 25,
        "economyTicketCost": 75,
        "flightDate": "2023-6-30",
    }

flights.insert_one(flight)
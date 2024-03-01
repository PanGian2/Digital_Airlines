# Digital Airlines

This service is responsible for booking Digital Airlines tickets. It supports functions such as authentication, adding, editing and deleting flights and reservations. These operations can be done from the browser and from Postman.

## How to run the service

This service uses Docker, Flask as the server and MongoDB as the database. It has been containerized thanks to docker-compose so that the Flask and MongoDB containers run simultaneously. 
So the steps one needs to run to use the service are as follows:
1. Open Git Bash and change the current working directory to the location where we want to clone the directory
    ```
    git init
    ```

2. Clone the repo

     ```
      git clone https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis.git
     ```
3. We compose up the service

   ```
    cd YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis
    docker-compose up -d
   ```
4. When we run it for the first time we need to enter some data into the database. So we go to the seeds.py file which will import some users and a flight into the database.
     ```
      cd flask/data
      python seeds.py
     ```
5.We make sure that the flask is running properly
   
   ```
    docker logs flask
   ```
   ![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/a45604b5-31d1-45e3-bea1-c2a5178448ed)

6. We go to the browser and type http://localhost:5000/ . This takes us to the home page of the service and we can proceed to the various functions of the service.
   
   ![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/c92e4d65-48d3-4ba0-a43a-7aa6df48dccf)


## Functionalities

In order to navigate to the page it is necessary for the user to be logged in first.

### Login

In order to navigate to the page, the user must first log in. Therefore he goes to `/login`. He has to enter his email and password. If either of them is not entered, `Error 400 (Bad Request)` is returned. Also if the data does not correspond to a user, `Error 401 (Unauthorized)` is returned. So when the user enters correct data he is logged into the system. To maintain the connection we use session which is a cookie whose content is encrypted. The value of the session is the username of the logged in user since it is unique. We also define that the session expires after 5 minutes.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/40dda9d1-93af-4c89-9729-51467417af99)

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/3c79723b-5cbc-4041-8c01-a57276d2ec1e)

Users are separated and authenticated as follows. In each record there is a `type` field which takes values `User`, for the ordinary user, and `Admin`, for the administrator. So to see if a user is `User` we take the username from the session and check if the type is `User`. Similarly for administrators, because we know there are only two we check if the username is admin1 or admin2.

The passwords for ordinary users are 123 and for administrators are admin


### Registration

As we said, it is necessary for the user to have an account. Therefore in `/register` he is asked to fill in the form to create an account. He has to fill in username, password, email, full name, date of birth, country of origin and passport. The username and email are unique to each user so if either is given which are already in the system an `Error 400` is returned. Otherwise a new user is created. Since only ordinary users can create an account, we set `type: "User"`

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/c8835425-e3b8-4064-85f9-ee6041e3a8dd)


### Logout

Users are given the option to logout from the system in `/logout'. Simply a logged in user goes to /logout and then logs out. In case he is not logged in it just tells him that he is not logged in

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/aa62db69-9810-4b52-a2f7-83c6c043dd59)


### Find Flights

Users can search all available flights in the system in `/flights`. This endpoint is common to both ordinary users and administrators. Typing /flights will display the id, departure airport, destination airport and date of all available flights.
![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/c14ba56f-6e20-473e-aeed-06dc2bbb6748)

It is also possible to filter the results using `departAirport` and `destAirport` together, `flightDate`, or all three together as arguments. 

For example `http://localhost:5000/flights?departAirport=El. Benizelos (ATH)&destAirport=El Prat (BCN)`

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/375e7481-17a5-4af7-9942-53bcb73b763f)


### Find specific flight

Users can get more flight information by going to `/flights/<id>` where id is the id of the flight. The endpoint is available to both user types but the results per type are different. For ordinary users, the date of the flight, the airport of origin and the airport of final destination, the available tickets (economy and business), and the cost of the tickets for each of the two categories (economy and business) are displayed.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/c1ed220c-3dd7-4881-b087-78869db090eb)

On the other hand, in combination with the above data, the name and full name of the person for whom the reservation has been made as well as the category of the seat that has been booked, for each reservation that has been made on that flight.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/7559a193-1111-46e4-b0f8-13291d18fcf2)


### Update flight

An administrator can change the ticket prices for the business & economy categories of a particular flight. To do this he should go to `/flights/<id>` where id is the id of the flight. This operation is done with the `PUT` method, since we want to update a record. So we need to go to Postman and set the values of the two categories.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/32f933eb-5549-4065-ba40-2e8cb2f786b6)

In case an ordinary user tries to enter this endpoint, `Error 403 Forbidden`


### Create flight

An administrator can create a new flight in `/flights/new`. He/she has to enter the date of the flight, the airport of origin and the airport of final destination, the available tickets (economy and business), and the cost of the tickets for each of the two categories (economy and business). The method of this endpoint is `POST` since we are inserting a new record into the database.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/812de017-aff3-4871-adc8-c9bc2de2c791)

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/139d269e-4d9b-49e2-9cb8-b9fbe251bd2b)

In case the user enters character data for any of the fields of the alerts, the corresponding error message appears, that they must be numbers.


### Delete flight

An administrator can delete a flight in `/flights/<id>` where id is the id of the flight. This can be done in Postman by going to `http://localhost:5000/flights/64943d40a1c64835299976e7` and selecting the `DELETE` method. This gives the following result

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/3ff3ba49-c1d6-4af5-b6ee-bcdf4550773a)

A prerequisite for deleting the flight is that there are no reservations for it. If there are, then the appropriate message is displayed and the flight is not deleted


### Ticket booking

An ordinary user can buy a ticket for a particular flight at `/bookings/new/<flight_id>` where flight_id is the id of the flight. To make the booking he/she will have to fill in the full name, passport number, date of birth, email and the type of ticket he/she wants to buy. Upon successful booking, the departure airport, the origin airport, the date of the flight and the id of the flight are added to the ticket. The available seats for that flight are also updated. It is important that the email is that of the logged in user and not another one, so that the booking is saved in the logged in user's account.

For example for the flight from Athens to Thessaloniki. We have 0 Business tickets available and 15 Economy tickets available. Then the following will occur:

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/396a820a-92b8-4504-9e82-4874d552d99f)

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/0deb7c75-ddc4-4b6a-8b32-ec8cb7fbeb0e)

However, if we choose Business, an error will occur as there are no tickets available.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/7ac1ef2b-24c8-4d60-9285-1383e57a8bd1)


### Find bookings

A simple user can search for all the bookings made in his account in `/bookings`. That is, all bookings whose emails match the email of the logged in user are returned.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/21901048-c9f1-47d7-8f43-69f09fc0d5c4)


### Find specific booking

A simple user can search for a specific booking made in his/her account in `/bookings/<id>` where id is the id of the booking. Again, the email of the booking must match the email of the logged in user. 

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/02b6cd70-0a0b-491f-95c4-4db5ba4d820a)

### Cancel booking

An ordinary user can cancel a reservation made in his/her account in `/bookings/<id>` where id is the id of the reservation. To do this we need to go to Postman and select the `DELETE` method. For example we go to `http://localhost:5000/bookings/64948cfe9c470bb075b1f8a3`. On successful deletion the available tickets for the flight are updated

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/a6d36751-e71f-4edd-8515-026a75c708e6)


### Διαγραφή χρήστη

Ένας απλός χρήστης μπορεί να διαγράψει τον λογαριασμό του στο `/user/delete`. Αρκεί να πάει στο Postman, να επιλέξει την μέθοδο DELETE και ο λογαριασμός του διαγράφεται.

![image](https://github.com/PanGian2/YpoxreotikiErgasia23_e20026_Giannakopoulos_Panagiotis/assets/122677298/f61f32b9-e473-4ea1-a91e-081e5c1adce6)


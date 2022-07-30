# Krypto Backend API Task

## Tech Stack:
Python, Flask for the web application framework, SQLite for the Database Engine, SQLAlchemy as the Object Relational Mapper and Postman is used for API testing.

## Description:
There are 3 major API endpoints, creating an alert, deleting an alert and fetching all alerts by user which can be filtered by status and such. After some frontend magic, this can be used in building a web app to send you E-Mail alerts as the real time price index of BTC-USD reaches your preferred target using GMail SMTP.

## Installation:
    Pull this repository into local machine. Set up a virtual environment in python and install the requirements.txt
    Open a Terminal session within the api folder
    run the commands below from the api directory in the terminal 
      set FLASK_APP=application.py 
      set FLASK_ENV=development or equivalent commands as per operating system
    write and execute the command: flask run

Backend should be up and running on your localhost at port 5000

The homepage at localhost:5000/ shows the current price of bitcoin as retreived from CoinGecko's API

# Documentation:
## API Endpoints:

There are 4 Endpoints in total, 3 for the Alerts and 1 to switch to activated mode, which continues to run and update the user.

## /alerts/create - POST Requests
To Create an alert for a particular user to get email alerts when the price of BTC crosses a particular target.
parameters: uid - user id, aid - alert id, atarget - target price, astatus - Status is set to created when an alert is made using the POST call

## /alerts/delete - PUT Requests
To delete an alert based on alert id, status is changed to deleted and the alert is not sent if it was not triggered before deletion, record is preserved in the database.
parameters: aid - alert id

## /alerts - GET Requests
To fetch all alerts made for a particular user, filter by user id and query filter for the alert status.
parameters: u_id - user id, queryfilter - status of the alert, can be one of ['created','deleted','triggered']

## /user - POST Request
To create a new user profile with username and password
parameters: username, password, email
uid is generated automatically

## /login 
To login as a user, returns a JWT token that is valid for 60 minutes from time of creation
parameters - username, password need to be entered in the fields provided on the browser

## /sendEmail
The API call starts the functions that checks the price of bitcoin in realtime and send the email to all satisfied alerts. Status of alert is changed to triggered after email is sent.

  
# Improvements that can be done
### Users can be assigned roles such as admin or regular users. Admin will be able to view all user details and trigger the sendEmail API Call
### User ID for users could be generated as a random characters of string instead of Integer. 
### User's can be assigned a seperate public ID for security reasons

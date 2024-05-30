import mysql.connector
import json
import time
import threading
from datetime import timedelta
from flask import Flask, request, render_template, redirect, url_for, session, current_app, Response, send_file, jsonify
import os
import matplotlib
import io
import matplotlib.pyplot as plt
import numpy as np
# from picamera2 import Picamera2
import cv2
import re
import requests
import logging
import time  #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Initialize Flask app
app = Flask(_name_)
app.secret_key = 'your_secret_key'

# Firebase API key
FIREBASE_API_KEY = "AIzaSyDSERShIWYu2s6MOjAEujYiD4EgAEgtejY"

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Connect to MySQL database
mydb = mysql.connector.connect(host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
                               user="smartpetcomfort", password="swinburneaaronsarawakidauniversityjacklin", database="petcomfort_db")

cloudCursor = mydb.cursor(dictionary=True)

cloudCursor.execute("SET time_zone = '+08:00';")
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Dog_Table (
    dogTableID INT AUTO_INCREMENT PRIMARY KEY,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    petCount INT,
    lightState BOOLEAN DEFAULT FALSE,
    humidity FLOAT,
    temperature_C FLOAT,
    temperature_F FLOAT,
    windowState BOOLEAN DEFAULT FALSE,
    fanState BOOLEAN DEFAULT FALSE,
    fanSpeed INT
)
""")


# Adjust threshold
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Dog_Adjust_Table (
    dogAdjustTableID INT AUTO_INCREMENT PRIMARY KEY,
    fanTemp FLOAT,
    dustWindow INT,
    petLight INT,
    irDistance INT
)
""")

cloudCursor.execute("SELECT COUNT(*) FROM Dog_Adjust_Table")
count = cloudCursor.fetchone()['COUNT(*)']
if count == 0:
    cloudCursor.execute(
        f"INSERT INTO Dog_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (28, 500, 1, 10)")
    mydb.commit()

# Manual value
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Dog_Control_Table (
    dogControlID INT AUTO_INCREMENT PRIMARY KEY,
    lightState BOOLEAN DEFAULT FALSE,
    fanState BOOLEAN DEFAULT FALSE,
    windowState BOOLEAN DEFAULT FALSE
)
""")
                    
cloudCursor.execute("SELECT COUNT(*) FROM Dog_Control_Table")
count = cloudCursor.fetchone()['COUNT(*)']
if count == 0:
    cloudCursor.execute(
        f"INSERT INTO Dog_Control_Table (lightState, fanState, windowState) VALUES (0, 0, 0)")
    mydb.commit()

cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Dog_Dust_Table (
    dogDustID INT AUTO_INCREMENT PRIMARY KEY,
    dogTableId INT,
    dustLevel FLOAT,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dogTableId) REFERENCES Dog_Table(dogTableID)
)
""")

cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Mode_Table (
    modeTableID INT AUTO_INCREMENT PRIMARY KEY,
    control VARCHAR(20)
)
""")

cloudCursor.execute("SELECT COUNT(*) FROM Mode_Table")
count = cloudCursor.fetchone()['COUNT(*)']
if count == 0:
    cloudCursor.execute(f"INSERT INTO Mode_Table (control) VALUES ('false')")
    mydb.commit()
    

cloudCursor.execute("SET time_zone = '+08:00';")
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Cat_Table (
    catTableID INT AUTO_INCREMENT PRIMARY KEY,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    petCount INT, 
    lightState BOOLEAN DEFAULT FALSE,
    humidity FLOAT,
    temperature_C FLOAT,
    temperature_F FLOAT,
    windowState BOOLEAN DEFAULT FALSE,
    fanState BOOLEAN DEFAULT FALSE,
    fanSpeed INT
)
""")

# Adjust threshold
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Cat_Adjust_Table (
    catAdjustTableID INT AUTO_INCREMENT PRIMARY KEY,
    fanTemp FLOAT,
    dustWindow INT,
    petLight INT,
    irDistance INT
)
""")

cloudCursor.execute("SELECT COUNT(*) FROM Cat_Adjust_Table")
count = cloudCursor.fetchone()['COUNT(*)']
if count == 0:
    cloudCursor.execute(
        f"INSERT INTO Cat_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (28, 500, 1, 10)")
    mydb.commit()

# Manual value
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Cat_Control_Table (
    catControlID INT AUTO_INCREMENT PRIMARY KEY,
    lightState BOOLEAN DEFAULT FALSE,
    fanState BOOLEAN DEFAULT FALSE,
    windowState BOOLEAN DEFAULT FALSE
)
""")

cloudCursor.execute("SELECT COUNT(*) FROM Cat_Control_Table")
count = cloudCursor.fetchone()['COUNT(*)']
if count == 0:
    cloudCursor.execute(
        f"INSERT INTO Cat_Control_Table (lightState, fanState, windowState) VALUES (0, 0, 0)")
    mydb.commit()

cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Cat_Dust_Table (
    catDustID INT AUTO_INCREMENT PRIMARY KEY,
    catTableId INT,
    dustLevel FLOAT,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (catTableId) REFERENCES Cat_Table(catTableID)
)
""")

cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Mode_Table (
    modeTableID INT AUTO_INCREMENT PRIMARY KEY,
    control VARCHAR(20)
)
""")


cloudCursor.execute("SET time_zone = '+08:00';")
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Pig_Table (
    pigTableID INT AUTO_INCREMENT PRIMARY KEY,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    petCount INT,
    lightState BOOLEAN DEFAULT FALSE,
    humidity FLOAT,
    temperature_C FLOAT,
    temperature_F FLOAT,
    windowState BOOLEAN DEFAULT FALSE,
    fanState BOOLEAN DEFAULT FALSE,
    fanSpeed INT
)
""")

# Adjust threshold
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Pig_Adjust_Table (
    pigAdjustTableID INT AUTO_INCREMENT PRIMARY KEY,
    fanTemp FLOAT,
    dustWindow INT,
    petLight INT,
    irDistance INT
)
""")

cloudCursor.execute("SELECT COUNT(*) FROM Pig_Adjust_Table")
count = cloudCursor.fetchone()['COUNT(*)']
if count == 0:
    cloudCursor.execute(
        f"INSERT INTO Pig_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (28, 500, 1, 10)")
    mydb.commit()

# Manual value
cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Pig_Control_Table (
    pigControlID INT AUTO_INCREMENT PRIMARY KEY,
    lightState BOOLEAN DEFAULT FALSE,
    fanState BOOLEAN DEFAULT FALSE,
    windowState BOOLEAN DEFAULT FALSE
)
""")

cloudCursor.execute("SELECT COUNT(*) FROM Pig_Control_Table")
count = cloudCursor.fetchone()['COUNT(*)']
if count == 0:
    cloudCursor.execute(
        f"INSERT INTO Pig_Control_Table (lightState, fanState, windowState) VALUES (0, 0, 0)")
    mydb.commit()

cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Pig_Dust_Table (
    pigDustID INT AUTO_INCREMENT PRIMARY KEY,
    pigTableId INT,
    dustLevel FLOAT,
    time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pigTableId) REFERENCES Pig_Table(pigTableID)
)
""")

cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Mode_Table (
    modeTableID INT AUTO_INCREMENT PRIMARY KEY,
    control VARCHAR(20)
)
""")

cloudCursor.execute("""
CREATE TABLE IF NOT EXISTS Picam_Table (
    piCamID INT AUTO_INCREMENT PRIMARY KEY,
    image MEDIUMBLOB NULL,
    takePhoto_dog BOOLEAN,
    takePhoto_cat BOOLEAN,
    takePhoto_pig BOOLEAN
)
""")

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'password' in request.form and 'email' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not password or not email:
            msg = 'Please fill out the form!'
        else:
            try:
                # Data to send to Firebase API
                data = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }
                
                # Call Firebase API
                response = requests.post(
                    f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}",
                    headers={"Content-Type": "application/json"},
                    json=data
                )
                
                # Check if the request was successful
                if response.status_code == 200:
                    msg = 'You have successfully registered!'
                else:
                    error_message = response.json().get('error', {}).get('message', 'Registration failed')
                    logging.error(f"Error during registration: {error_message}")
                    msg = f"Error during registration: {error_message}"
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                msg = f"Unexpected error: {str(e)}"
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    return render_template('register.html', msg=msg)

# Define route for index page
@app.route('/')
def index():
    if 'loggedin' not in session or session['loggedin'] != True:
        return render_template('login.html')
    else:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Cat_Adjust_Table WHERE catAdjustTableID = 1 LIMIT 1")
        cat_adjust_data = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM Cat_Control_Table WHERE catControlID = 1 LIMIT 1;")
        cat_control_data = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM Dog_Adjust_Table WHERE dogAdjustTableID = 1 LIMIT 1")
        dog_adjust_data = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM Dog_Control_Table WHERE dogControlID = 1 LIMIT 1;")
        dog_control_data = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM Pig_Adjust_Table WHERE pigAdjustTableID = 1 LIMIT 1")
        pig_adjust_data = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM Pig_Control_Table WHERE pigControlID = 1 LIMIT 1;")
        pig_control_data = cursor.fetchone()

        cursor.execute("SELECT * FROM Mode_Table LIMIT 1")
        existing_mode = cursor.fetchone()
        if not existing_mode:
            cursor.execute("INSERT INTO Mode_Table (control) VALUES ('false')")
            mydb.commit()

        cursor.close()

        # Call function to continuously insert sensor data
        return render_template('index.html', cat_adjust_data=cat_adjust_data, cat_control_data=cat_control_data,dog_adjust_data=dog_adjust_data, dog_control_data=dog_control_data, pig_adjust_data=pig_adjust_data, pig_control_data=pig_control_data)
@app.route('/email_password_login', methods=['GET', 'POST'])
def email_password_login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Data to send to Firebase API
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            # Call Firebase API
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
                headers={"Content-Type": "application/json"},
                json=data
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                user_data = response.json()
                session['loggedin'] = True
                session['user_id'] = user_data['localId']
                session['email'] = email
                msg = 'Logged in successfully!'
                return redirect(url_for('index'))  # Redirect to the root URL after login
            else:
                error_message = response.json().get('error', {}).get('message', 'Login failed')
                print(f"Error during login: {error_message}")
                msg = 'Incorrect email or password!'
        except Exception as e:
            print(f"Error during login: {str(e)}")
            msg = 'An unexpected error occurred!'
    
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('email_password_login'))

def update_mode_table(control):
    with mydb.cursor() as cursor:
        sql = "INSERT INTO Mode_Table (control) VALUES (%s) ON DUPLICATE KEY UPDATE control = VALUES(control)"
        cursor.execute(sql, (control,))
        mydb.commit()
        
@app.route('/globalAdjust', methods=['POST'])
def globalAdjust():
    if request.method == 'POST':
        # Form data
        fanTemp = request.form['fanTemp']
        dustWindow = request.form['dustWindow']
        petLight = request.form['petLight']
        irDistance = request.form['irDistance']

        # Connect to MySQL and execute INSERT or UPDATE query
        with mydb.cursor() as cursor:
            # Check if a record already exists in the table
            cursor.execute("SELECT * FROM Cat_Adjust_Table")
            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                sql = "UPDATE Cat_Adjust_Table SET fanTemp=%s, dustWindow=%s, petLight=%s, irDistance=%s"
                val = (fanTemp, dustWindow, petLight, irDistance)
            else:
                # Insert new record
                sql = "INSERT INTO Cat_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (%s, %s, %s, %s)"
                val = (fanTemp, dustWindow, petLight, irDistance)

            cursor.execute(sql, val)
            mydb.commit()
            
        # Connect to MySQL and execute INSERT or UPDATE query
        with mydb.cursor() as cursor:
            # Check if a record already exists in the table
            cursor.execute("SELECT * FROM Dog_Adjust_Table")
            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                sql = "UPDATE Dog_Adjust_Table SET fanTemp=%s, dustWindow=%s, petLight=%s, irDistance=%s"
                val = (fanTemp, dustWindow, petLight, irDistance)
            else:
                # Insert new record
                sql = "INSERT INTO Dog_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (%s, %s, %s, %s)"
                val = (fanTemp, dustWindow, petLight, irDistance)

            cursor.execute(sql, val)
            mydb.commit()

        # Connect to MySQL and execute INSERT or UPDATE query
        with mydb.cursor() as cursor:
            # Check if a record already exists in the table
            cursor.execute("SELECT * FROM Pig_Adjust_Table")
            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                sql = "UPDATE Pig_Adjust_Table SET fanTemp=%s, dustWindow=%s, petLight=%s, irDistance=%s"
                val = (fanTemp, dustWindow, petLight, irDistance)
            else:
                # Insert new record
                sql = "INSERT INTO Pig_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (%s, %s, %s, %s)"
                val = (fanTemp, dustWindow, petLight, irDistance)

            cursor.execute(sql, val)
            mydb.commit()
            
        # Redirect to a success page or render a success message
        return render_template('global.html')


@app.route('/catAdjust', methods=['POST'])
def catAdjust():
    cat_adjust_data = None
    cat_control_data = None
    dog_adjust_data = None
    dog_control_data = None
    pig_adjust_data = None
    pig_control_data = None
    if request.method == 'POST':
        # Form data
        fanTemp = request.form['fanTemp']
        dustWindow = request.form['dustWindow']
        petLight = request.form['petLight']
        irDistance = request.form['irDistance']

        # Connect to MySQL and execute INSERT or UPDATE query
        with mydb.cursor() as cursor:
            # Check if a record already exists in the table
            cursor.execute("SELECT * FROM Cat_Adjust_Table")
            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                sql = "UPDATE Cat_Adjust_Table SET fanTemp=%s, dustWindow=%s, petLight=%s, irDistance=%s"
                val = (fanTemp, dustWindow, petLight, irDistance)
            else:
                # Insert new record
                sql = "INSERT INTO Cat_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (%s, %s, %s, %s)"
                val = (fanTemp, dustWindow, petLight, irDistance)

            cursor.execute(sql, val)
            mydb.commit()

            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Cat_Adjust_Table WHERE catAdjustTableID = 1 LIMIT 1;")
            cat_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Cat_Control_Table WHERE catControlID = 1 LIMIT 1;")
            cat_control_data = cursor.fetchone()

            # Fetch dog_adjust_data and dog_control_data to ensure they're defined
            cursor.execute("SELECT * FROM Dog_Adjust_Table WHERE dogAdjustTableID = 1 LIMIT 1;")
            dog_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Dog_Control_Table WHERE dogControlID = 1 LIMIT 1;")
            dog_control_data = cursor.fetchone()

            # Fetch pig_adjust_data and pig_control_data to ensure they're defined
            cursor.execute("SELECT * FROM Pig_Adjust_Table WHERE pigAdjustTableID = 1 LIMIT 1;")
            pig_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Pig_Control_Table WHERE pigControlID = 1 LIMIT 1;")
            pig_control_data = cursor.fetchone()

        # Redirect to a success page or render a success message
        return render_template('index.html', cat_adjust_data=cat_adjust_data, cat_control_data=cat_control_data, dog_adjust_data=dog_adjust_data, dog_control_data=dog_control_data, pig_adjust_data=pig_adjust_data, pig_control_data=pig_control_data)
    
#dog Adjust
@app.route('/dogAdjust', methods=['POST'])
def dogAdjust():
    dog_adjust_data = None
    dog_control_data = None
    cat_adjust_data = None
    cat_control_data = None
    if request.method == 'POST':
        # Form data
        fanTemp = request.form['fanTemp']
        dustWindow = request.form['dustWindow']
        petLight = request.form['petLight']
        irDistance = request.form['irDistance']

        # Connect to MySQL and execute INSERT or UPDATE query
        with mydb.cursor() as cursor:
            # Check if a record already exists in the table
            cursor.execute("SELECT * FROM Dog_Adjust_Table")
            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                sql = "UPDATE Dog_Adjust_Table SET fanTemp=%s, dustWindow=%s, petLight=%s, irDistance=%s"
                val = (fanTemp, dustWindow, petLight, irDistance)
            else:
                # Insert new record
                sql = "INSERT INTO Dog_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (%s, %s, %s, %s)"
                val = (fanTemp, dustWindow, petLight, irDistance)

            cursor.execute(sql, val)
            mydb.commit()

            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Dog_Adjust_Table WHERE dogAdjustTableID = 1 LIMIT 1;")
            dog_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Dog_Control_Table WHERE dogControlID = 1 LIMIT 1;")
            dog_control_data = cursor.fetchone()

            # Fetch cat_adjust_data and cat_control_data to ensure they're defined
            cursor.execute("SELECT * FROM Cat_Adjust_Table WHERE catAdjustTableID = 1 LIMIT 1;")
            cat_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Cat_Control_Table WHERE catControlID = 1 LIMIT 1;")
            cat_control_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Pig_Adjust_Table WHERE pigAdjustTableID = 1 LIMIT 1;")
            pig_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Pig_Control_Table WHERE pigControlID = 1 LIMIT 1;")
            pig_control_data = cursor.fetchone()

        # Redirect to a success page or render a success message
        return render_template('index.html', cat_adjust_data=cat_adjust_data, cat_control_data=cat_control_data, dog_adjust_data=dog_adjust_data, dog_control_data=dog_control_data, pig_adjust_data=pig_adjust_data, pig_control_data=pig_control_data)
    
#  pig Adjust
@app.route('/pigAdjust', methods=['POST'])
def pigAdjust():
    pig_adjust_data = None
    pig_control_data = None
    cat_adjust_data = None  # Initialize this variable
    cat_control_data = None  # Initialize this variable
    if request.method == 'POST':
        # Form data
        fanTemp = request.form['fanTemp']
        dustWindow = request.form['dustWindow']
        petLight = request.form['petLight']
        irDistance = request.form['irDistance']

        # Connect to MySQL and execute INSERT or UPDATE query
        with mydb.cursor() as cursor:
            # Check if a record already exists in the table
            cursor.execute("SELECT * FROM Pig_Adjust_Table")
            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing record
                sql = "UPDATE Pig_Adjust_Table SET fanTemp=%s, dustWindow=%s, petLight=%s, irDistance=%s"
                val = (fanTemp, dustWindow, petLight, irDistance)
            else:
                # Insert new record
                sql = "INSERT INTO Pig_Adjust_Table (fanTemp, dustWindow, petLight, irDistance) VALUES (%s, %s, %s, %s)"
                val = (fanTemp, dustWindow, petLight, irDistance)

            cursor.execute(sql, val)
            mydb.commit()

            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Pig_Adjust_Table WHERE pigAdjustTableID = 1 LIMIT 1;")
            pig_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Pig_Control_Table WHERE pigControlID = 1 LIMIT 1;")
            pig_control_data = cursor.fetchone()

            # Fetch cat_adjust_data and cat_control_data to ensure they're defined
            cursor.execute("SELECT * FROM Cat_Adjust_Table WHERE catAdjustTableID = 1 LIMIT 1;")
            cat_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Cat_Control_Table WHERE catControlID = 1 LIMIT 1;")
            cat_control_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Dog_Adjust_Table WHERE dogAdjustTableID = 1 LIMIT 1;")
            dog_adjust_data = cursor.fetchone()

            cursor.execute("SELECT * FROM Dog_Control_Table WHERE dogControlID = 1 LIMIT 1;")
            dog_control_data = cursor.fetchone()

        # Redirect to a success page or render a success message
        return render_template('index.html', cat_adjust_data=cat_adjust_data, cat_control_data=cat_control_data, dog_adjust_data=dog_adjust_data, dog_control_data=dog_control_data, pig_adjust_data=pig_adjust_data, pig_control_data=pig_control_data)

# Route to handle toggle button change
@app.route('/toggle-mode', methods=['POST'])
def toggle_mode():
    mode = request.form['mode']
    control_value = 'false' if mode == 'controllable' else 'true'
    with mydb.cursor() as cursor:
        cursor.execute("SELECT * FROM Mode_Table LIMIT 1")
        existing_record = cursor.fetchone()
        if existing_record:
            cursor.execute("UPDATE Mode_Table SET control = %s",
                           (control_value,))
        else:
            cursor.execute(
                "INSERT INTO Mode_Table (control) VALUES (%s)", (control_value,))
        mydb.commit()
    return "Mode updated successfully"


@app.route('/globalControl', methods=['POST'])
def globalControl():
    # Retrieve states from form data
    lightState = request.form.get('light') == 'true'
    fanState = request.form.get('fan') == 'true'
    windowState = request.form.get('window') == 'true'

    with mydb.cursor() as cursor:
        # Check if a record already exists in the table
        cursor.execute("SELECT * FROM Dog_Control_Table LIMIT 1")
        existing_record = cursor.fetchone()

        if existing_record:
            # Construct the SQL query to update only the changed fields
            cursor.execute(
                f"UPDATE Dog_Control_Table SET lightState = {lightState}, fanState = {fanState}, windowState = {windowState} WHERE dogControlID = 1")
        else:
            # Insert new record if no existing record found
            sql = "INSERT INTO Dog_Control_Table (lightState, fanState, windowState) VALUES (%s, %s, %s)"
            cursor.execute(sql, (lightState, fanState, windowState))

        # Repeat the same process for other tables
        # Cat Control Table
        cursor.execute("SELECT * FROM Cat_Control_Table LIMIT 1")
        existing_record = cursor.fetchone()

        if existing_record:
            cursor.execute(
                f"UPDATE Cat_Control_Table SET lightState = {lightState}, fanState = {fanState}, windowState = {windowState} WHERE catControlID = 1")
        else:
            sql = "INSERT INTO Cat_Control_Table (lightState, fanState, windowState) VALUES (%s, %s, %s)"
            cursor.execute(sql, (lightState, fanState, windowState))

        # Pig Control Table
        cursor.execute("SELECT * FROM Pig_Control_Table LIMIT 1")
        existing_record = cursor.fetchone()

        if existing_record:
            cursor.execute(
                f"UPDATE Pig_Control_Table SET lightState = {lightState}, fanState = {fanState}, windowState = {windowState} WHERE pigControlID = 1")
        else:
            sql = "INSERT INTO Pig_Control_Table (lightState, fanState, windowState) VALUES (%s, %s, %s)"
            cursor.execute(sql, (lightState, fanState, windowState))

    # Commit all changes after executing all SQL statements
    mydb.commit()
    
    return "Data stored successfully"
    
    
@app.route('/catControl', methods=['POST'])
def catControl():
    lightState = request.form.get('light') == 'true'
    fanState = request.form.get('fan') == 'true'
    windowState = request.form.get('window') == 'true'

    with mydb.cursor() as cursor:
        # Check if a record already exists in the table
        cursor.execute("SELECT * FROM Cat_Control_Table LIMIT 1")
        existing_record = cursor.fetchone()

        if existing_record:
            # Construct the SQL query to update only the changed fields
            cursor.execute(
                f"UPDATE Cat_Control_Table SET lightState = {lightState} WHERE catControlID = 1")
            cursor.execute(
                f"UPDATE Cat_Control_Table SET fanState = {fanState} WHERE catControlID = 1")
            cursor.execute(
                f"UPDATE Cat_Control_Table SET windowState = {windowState} WHERE catControlID = 1")
        else:
            # Insert new record if no existing record found
            sql = "INSERT INTO Cat_Control_Table (lightState, fanState, windowState) VALUES (%s, %s, %s)"
            cursor.execute(sql, (lightState, fanState, windowState))

        mydb.commit()

    return "Data stored successfully"

# dog Control
@app.route('/dogControl', methods=['POST'])
def dogControl():
    lightState = request.form.get('light') == 'true'
    fanState = request.form.get('fan') == 'true'
    windowState = request.form.get('window') == 'true'

    with mydb.cursor() as cursor:
        # Check if a record already exists in the table
        cursor.execute("SELECT * FROM Dog_Control_Table LIMIT 1")
        existing_record = cursor.fetchone()

        if existing_record:
            # Construct the SQL query to update only the changed fields
            cursor.execute(
                f"UPDATE Dog_Control_Table SET lightState = {lightState} WHERE dogControlID = 1")
            cursor.execute(
                f"UPDATE Dog_Control_Table SET fanState = {fanState} WHERE dogControlID = 1")
            cursor.execute(
                f"UPDATE Dog_Control_Table SET windowState = {windowState} WHERE dogControlID = 1")
        else:
            # Insert new record if no existing record found
            sql = "INSERT INTO Dog_Control_Table (lightState, fanState, windowState) VALUES (%s, %s, %s)"
            cursor.execute(sql, (lightState, fanState, windowState))

        mydb.commit()

    return "Data stored successfully"

# pig Control
@app.route('/pigControl', methods=['POST'])
def pigControl():
    lightState = request.form.get('light') == 'true'
    fanState = request.form.get('fan') == 'true'
    windowState = request.form.get('window') == 'true'

    with mydb.cursor() as cursor:
        # Check if a record already exists in the table
        cursor.execute("SELECT * FROM Pig_Control_Table LIMIT 1")
        existing_record = cursor.fetchone()

        if existing_record:
            # Construct the SQL query to update only the changed fields
            cursor.execute(
                f"UPDATE Pig_Control_Table SET lightState = {lightState} WHERE pigControlID = 1")
            cursor.execute(
                f"UPDATE Pig_Control_Table SET fanState = {fanState} WHERE pigControlID = 1")
            cursor.execute(
                f"UPDATE Pig_Control_Table SET windowState = {windowState} WHERE pigControlID = 1")
        else:
            # Insert new record if no existing record found
            sql = "INSERT INTO Pig_Control_Table (lightState, fanState, windowState) VALUES (%s, %s, %s)"
            cursor.execute(sql, (lightState, fanState, windowState))

        mydb.commit()

    return "Data stored successfully"

# Define route to render catRoom page
@app.route('/main-room')
def mainRoom():
    
    return render_template('global.html')

@app.route('/cat-room')
def catRoom():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT Cat_Table.*, Cat_Dust_Table.dustLevel 
        FROM Cat_Table 
        LEFT JOIN Cat_Dust_Table ON Cat_Table.catTableID = Cat_Dust_Table.catTableId 
        WHERE Cat_Table.petCount > 0
        ORDER BY Cat_Table.catTableID DESC
    """)
    rows = cursor.fetchall()
    cats = {}

    for row in rows:
        if row['catTableID'] not in cats:
            cats[row['catTableID']] = row
            cats[row['catTableID']]['dust_levels'] = []

        if row['dustLevel'] is not None:
            cats[row['catTableID']]['dust_levels'].append(row['dustLevel'])

    cursor.close()

    cats_list = list(cats.values())

    cursor2 = mydb.cursor(dictionary=True)
    cursor2.execute("SELECT * FROM Cat_Table ORDER BY catTableID DESC LIMIT 1")
    last_row = cursor2.fetchone()
    last_petCount = last_row['petCount']
    cursor2.close()

    return render_template('cat-room.html', data=cats_list, last_petCount=last_petCount)

# Define route to render dogRoom page
@app.route('/dog-room')
def dogRoom():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT Dog_Table.*, Dog_Dust_Table.dustLevel 
        FROM Dog_Table 
        LEFT JOIN Dog_Dust_Table ON Dog_Table.dogTableID = Dog_Dust_Table.dogTableId 
        WHERE Dog_Table.petCount > 0
        ORDER BY Dog_Table.dogTableID DESC
    """)
    rows = cursor.fetchall()
    dogs = {}

    for row in rows:
        if row['dogTableID'] not in dogs:
            dogs[row['dogTableID']] = row
            dogs[row['dogTableID']]['dust_levels'] = []

        if row['dustLevel'] is not None:
            dogs[row['dogTableID']]['dust_levels'].append(row['dustLevel'])

    cursor.close()

    dogs_list = list(dogs.values())

    cursor2 = mydb.cursor(dictionary=True)
    cursor2.execute("SELECT * FROM Dog_Table ORDER BY dogTableID DESC LIMIT 1")
    last_row = cursor2.fetchone()
    last_petCount = last_row['petCount']
    cursor2.close()

    return render_template('dog-room.html', data=dogs_list, last_petCount=last_petCount)


# Define route to render pigRoom page
@app.route('/pig-room')
def pigRoom():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT Pig_Table.*, Pig_Dust_Table.dustLevel 
        FROM Pig_Table 
        LEFT JOIN Pig_Dust_Table ON Pig_Table.pigTableID = Pig_Dust_Table.pigTableId 
        WHERE Pig_Table.petCount > 0
        ORDER BY Pig_Table.pigTableID DESC
    """)
    rows = cursor.fetchall()
    pigs = {}

    for row in rows:
        if row['pigTableID'] not in pigs:
            pigs[row['pigTableID']] = row
            pigs[row['pigTableID']]['dust_levels'] = []

        if row['dustLevel'] is not None:
            pigs[row['pigTableID']]['dust_levels'].append(row['dustLevel'])

    cursor.close()

    pigs_list = list(pigs.values())

    cursor2 = mydb.cursor(dictionary=True)
    cursor2.execute("SELECT * FROM Pig_Table ORDER BY pigTableID DESC LIMIT 1")
    last_row = cursor2.fetchone()
    last_petCount = last_row['petCount']
    cursor2.close()

    return render_template('pig-room.html', data=pigs_list, last_petCount=last_petCount)

def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
   
@app.route('/camera_dog_feed')
def camera_dog_feed():
    try:
        # Connect to MySQL database
        cloudDB = mysql.connector.connect(
            host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
            user="smartpetcomfort",
            password="swinburneaaronsarawakidauniversityjacklin",
            database="petcomfort_db"
        )
        cloudCursor = cloudDB.cursor(dictionary=True)

        # Retrieve the image and takePhoto_dog value from row with piCamID = 1
        cloudCursor.execute("SELECT image, takePhoto_dog FROM Picam_Table WHERE piCamID = 1")
        result = cloudCursor.fetchone()

        if result:
            image_data = result['image']
            takePhoto = result['takePhoto_dog']

            # Set takePhoto_dog to TRUE if it's not already TRUE
            if not takePhoto:
                cloudCursor.execute("UPDATE Picam_Table SET takePhoto_dog = TRUE WHERE piCamID = 1")
                cloudDB.commit()

            if image_data:
                # Return the image
                return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
            else:
                print("There is no image to return.")
                return jsonify({"message": "There is no image to return."}), 404
        else:
            print("No data found for piCamID = 1.")
            return jsonify({"message": "No data found for piCamID = 1."}), 404

    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"message": "An error occurred."}), 500

    finally:
        if cloudDB.is_connected():
            cloudCursor.close()
            cloudDB.close()

@app.route('/camera_cat_feed')
def camera_cat_feed():
    try:
        # Connect to MySQL database
        cloudDB = mysql.connector.connect(
            host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
            user="smartpetcomfort",
            password="swinburneaaronsarawakidauniversityjacklin",
            database="petcomfort_db"
        )
        cloudCursor = cloudDB.cursor(dictionary=True)

        # Retrieve the image and takePhoto_cat value from row with piCamID = 1
        cloudCursor.execute("SELECT image, takePhoto_cat FROM Picam_Table WHERE piCamID = 1")
        result = cloudCursor.fetchone()

        if result:
            image_data = result['image']
            takePhoto = result['takePhoto_cat']

            # Set takePhoto_cat to TRUE if it's not already TRUE
            if not takePhoto:
                cloudCursor.execute("UPDATE Picam_Table SET takePhoto_cat = TRUE WHERE piCamID = 1")
                cloudDB.commit()

            if image_data:
                # Return the image
                return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
            else:
                print("There is no image to return.")
                return jsonify({"message": "There is no image to return."}), 404
        else:
            print("No data found for piCamID = 1.")
            return jsonify({"message": "No data found for piCamID = 1."}), 404

    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"message": "An error occurred."}), 500

    finally:
        if cloudDB.is_connected():
            cloudCursor.close()
            cloudDB.close()

@app.route('/camera_pig_feed')
def camera_pig_feed():
    try:
        # Connect to MySQL database
        cloudDB = mysql.connector.connect(
            host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
            user="smartpetcomfort",
            password="swinburneaaronsarawakidauniversityjacklin",
            database="petcomfort_db"
        )
        cloudCursor = cloudDB.cursor(dictionary=True)

        # Retrieve the image and takePhoto_pig value from row with piCamID = 1
        cloudCursor.execute("SELECT image, takePhoto_pig FROM Picam_Table WHERE piCamID = 1")
        result = cloudCursor.fetchone()

        if result:
            image_data = result['image']
            takePhoto = result['takePhoto_pig']

            # Set takePhoto_pig to TRUE if it's not already TRUE
            if not takePhoto:
                cloudCursor.execute("UPDATE Picam_Table SET takePhoto_pig = TRUE WHERE piCamID = 1")
                cloudDB.commit()

            if image_data:
                # Return the image
                return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
            else:
                print("There is no image to return.")
                return jsonify({"message": "There is no image to return."}), 404
        else:
            print("No data found for piCamID = 1.")
            return jsonify({"message": "No data found for piCamID = 1."}), 404

    except Exception as e:
        print("An error occurred:", e)
        return jsonify({"message": "An error occurred."}), 500

    finally:
        if cloudDB.is_connected():
            cloudCursor.close()
            cloudDB.close()

if __name__ == '__main__':
    # Start the Flask application
    app.run(debug=True)
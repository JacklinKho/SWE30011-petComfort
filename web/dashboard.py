import mysql.connector
import json
from datetime import timedelta
from flask import Flask, request, render_template, redirect, url_for, session, current_app, Response
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from picamera2 import Picamera2
import cv2
import re
import requests
import logging
import time  #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Firebase API key
FIREBASE_API_KEY = "AIzaSyDSERShIWYu2s6MOjAEujYiD4EgAEgtejY"

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Connect to MySQL database
mydb = mysql.connector.connect(host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
                               user="smartpetcomfort", password="swinburneaaronsarawakidauniversityjacklin", database="petcomfort_db")

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
        
        # Create a dictionary to hold the states
        data = {
            "fanTemp": fanTemp,
            "dustWindow": dustWindow,
            "petLight": petLight,
            "irDistance": irDistance,
        }

        # Convert the dictionary to JSON format
        payload = json.dumps(data)
        
        # AWS IoT certificate based connection
        myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
        myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
        myMQTTClient.configureCredentials("/home/ubuntu/swe30011/cert/AmazonRootCA1.pem", "/home/ubuntu/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-private.pem.key", "/home/ubuntu/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-certificate.pem.crt")
        myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

        # Connect to AWS IoT
        myMQTTClient.connect()

        # Publish the JSON payload to a topic
        myMQTTClient.publish("home/devices/threshold", payload, 0)

        # Disconnect from AWS IoT
        myMQTTClient.disconnect()

        # Redirect to a success page or render a success message
        return render_template('global.html')

@app.route('/catAdjust', methods=['POST'])
def catAdjust():
    cat_adjust_data = None
    cat_control_data = None
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

    # Create a dictionary to hold the states
    data = {
        "lightState": lightState,
        "fanState": fanState,
        "windowState": windowState
    }

    # Convert the dictionary to JSON format
    payload = json.dumps(data)

    # AWS IoT certificate based connection
    myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
    myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials("/home/ubuntu/swe30011/cert/AmazonRootCA1.pem", "/home/ubuntu/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-private.pem.key", "/home/ubuntu/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-certificate.pem.crt")
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect to AWS IoT
    myMQTTClient.connect()

    # Publish the JSON payload to a topic
    myMQTTClient.publish("home/devices/state", payload, 0)

    # Disconnect from AWS IoT
    myMQTTClient.disconnect() 
    
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

# Define route to render catRoom page
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
    # print(cats_list)

    cursor2 = mydb.cursor(dictionary=True)
    cursor2.execute("SELECT * FROM Cat_Table ORDER BY catTableID DESC LIMIT 1")
    last_row = cursor2.fetchone()
    last_petCount = last_row['petCount']
    cursor2.close()

    try:
        for cat in cats_list:
            dust_levels_list = cat['dust_levels']
            # print(dust_levels_list)
            if dust_levels_list.__len__() > 0:
                plt.plot(np.arange(1, len(dust_levels_list) + 1), dust_levels_list)
                plt.xlabel('Reading')
                plt.ylabel('Dust Levels')
                plt.title('Dust Level Readings')
                plt.grid(True)

                # Highlight min, max, and average values
                min_value = min(dust_levels_list)
                max_value = max(dust_levels_list)
                avg_value = sum(dust_levels_list) / len(dust_levels_list)

                plt.scatter(dust_levels_list.index(min_value) +
                            1, min_value, color='r', label='Min')
                plt.scatter(dust_levels_list.index(max_value) +
                            1, max_value, color='g', label='Max')

                plt.text(dust_levels_list.index(min_value) + 1, min_value,
                         f'Min: {min_value}', verticalalignment='bottom', horizontalalignment='right', color='r')
                plt.text(dust_levels_list.index(max_value) + 1, max_value,
                         f'Max: {max_value}', verticalalignment='bottom', horizontalalignment='right', color='g')

                plt.axhline(y=avg_value, color='orange', linestyle='--',
                            label=f'Average: {avg_value}')
                plt.text(len(dust_levels_list), avg_value, f'Avg: {avg_value}', color='orange',
                         verticalalignment='bottom', horizontalalignment='right')

                chart_filename = f"static/catRoom/chart/chart_{cat['catTableID']}.png"
                plt.savefig(chart_filename)
                plt.close()
    except Exception as e:
        print("Error:", e)

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
    # print(dogs_list)

    cursor2 = mydb.cursor(dictionary=True)
    cursor2.execute("SELECT * FROM Dog_Table ORDER BY dogTableID DESC LIMIT 1")
    last_row = cursor2.fetchone()
    last_petCount = last_row['petCount']
    cursor2.close()  

    try:
        for dog in dogs_list:
            dust_levels_list = dog['dust_levels']
            # print(dust_levels_list)
            if dust_levels_list.__len__() > 0:
                plt.plot(np.arange(1, len(dust_levels_list) + 1),
                         dust_levels_list)
                plt.xlabel('Reading')
                plt.ylabel('Dust Levels')
                plt.title('Dust Level Readings')
                plt.grid(True)

                # Highlight min, max, and average values
                min_value = min(dust_levels_list)
                max_value = max(dust_levels_list)
                avg_value = sum(dust_levels_list) / len(dust_levels_list)

                plt.scatter(dust_levels_list.index(min_value) +
                            1, min_value, color='r', label='Min')
                plt.scatter(dust_levels_list.index(max_value) +
                            1, max_value, color='g', label='Max')

                plt.text(dust_levels_list.index(min_value) + 1, min_value,
                         f'Min: {min_value}', verticalalignment='bottom', horizontalalignment='right', color='r')
                plt.text(dust_levels_list.index(max_value) + 1, max_value,
                         f'Max: {max_value}', verticalalignment='bottom', horizontalalignment='right', color='g')

                plt.axhline(y=avg_value, color='orange', linestyle='--',
                            label=f'Average: {avg_value}')
                plt.text(len(dust_levels_list), avg_value, f'Avg: {avg_value}', color='orange',
                         verticalalignment='bottom', horizontalalignment='right')
                
                chart_filename = f"static/dogRoom/chart/chart_{dog['dogTableID']}.png"
                plt.savefig(chart_filename)
                plt.close()
    except Exception as e:
        print("Error:", e)

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
    # print(pigs_list)

    cursor2 = mydb.cursor(dictionary=True)
    cursor2.execute("SELECT * FROM Pig_Table ORDER BY pigTableID DESC LIMIT 1")
    last_row = cursor2.fetchone()
    last_petCount = last_row['petCount']
    cursor2.close() 

    try:
        for pig in pigs_list:
            dust_levels_list = pig['dust_levels']
            # print(dust_levels_list)
            if dust_levels_list.__len__() > 0:
                plt.plot(np.arange(1, len(dust_levels_list) + 1),
                         dust_levels_list)
                plt.xlabel('Reading')
                plt.ylabel('Dust Levels')
                plt.title('Dust Level Readings')
                plt.grid(True)

                # Highlight min, max, and average values
                min_value = min(dust_levels_list)
                max_value = max(dust_levels_list)
                avg_value = sum(dust_levels_list) / len(dust_levels_list)

                plt.scatter(dust_levels_list.index(min_value) + 1, min_value, color='r', label='Min')
                plt.scatter(dust_levels_list.index(max_value) + 1, max_value, color='g', label='Max')

                plt.text(dust_levels_list.index(min_value) + 1, min_value,
                            f'Min: {min_value}', verticalalignment='bottom', horizontalalignment='right', color='r')
                plt.text(dust_levels_list.index(max_value) + 1, max_value,
                            f'Max: {max_value}', verticalalignment='bottom', horizontalalignment='right', color='g')
                
                plt.axhline(y=avg_value, color='orange', linestyle='--', label=f'Average: {avg_value}')
                plt.text(len(dust_levels_list), avg_value, f'Avg: {avg_value}', color='orange', verticalalignment='bottom', horizontalalignment='right')

                chart_filename = f"static/pigRoom/chart/chart_{pig['pigTableID']}.png"
                plt.savefig(chart_filename)
                plt.close()
    except Exception as e:
        print("Error:", e)

    return render_template('pig-room.html', data=pigs_list, last_petCount=last_petCount)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

# Function to capture an image
def capture_image(roomName):
    frame = camera.capture_array()
    filename = f'static/{roomName}/picam/picam.png'
    cv2.imwrite(filename, frame)
    return filename

@app.route('/capture-pig-image', methods=['GET'])
def capture_image_route():
    room_name = 'PigRoom'
    filename = capture_image(room_name)
    return {"image_path": filename}

@app.route('/capture-cat-image', methods=['GET'])
def capture_image_route():
    room_name = 'CatRoom'
    filename = capture_image(room_name)
    return {"image_path": filename}

if __name__ == '__main__':
    app.run()
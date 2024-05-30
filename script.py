import mysql.connector
import serial
import time
import json
from datetime import datetime
import os
import asyncio
import cv2
import pymysql.cursors
import threading
from picamera2 import Picamera2
from SerialInterface import SerialInterface
from catGlobalMQTT import catGlobalMQTT

current_cat_room_pet_number = None
previous_cat_room_pet_number = None

localDB = mysql.connector.connect(
    host="localhost", user="pi", password="123456", database="petcomfort_db")
localCursor = localDB.cursor(dictionary=True)

localCursor.execute("""
CREATE TABLE IF NOT EXISTS Cat_Raw_Data (
    rawID INT AUTO_INCREMENT PRIMARY KEY,
    petCount INT,
    humidity FLOAT,
    lightState BOOLEAN DEFAULT FALSE,
    temperature_C FLOAT,
    temperature_F FLOAT,
    fanState BOOLEAN DEFAULT FALSE,
    fanSpeed INT,
    windowState BOOLEAN DEFAULT FALSE,
    dustLevel FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


newInsertedID = None

cache = {
    'control': None,
    'fanTemp': None,
    'dustWindow': None,
    'petLight': None,
    'irDistance': None,
    'light': None,
    'fan': None,
    'window': None
}

result_lock = threading.Lock()
iface = SerialInterface()
mqtt = catGlobalMQTT()

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

def fetch_data():
    print("Fetching data")
    while True:
        try:
            result = mqtt.on_fetch()
            
            if result:
                cache["control"] = result.get("control")
                cache["fanTemp"] = result.get("fanTemp")
                cache["dustWindow"] = result.get("dustWindow")
                cache["petLight"] = result.get("petLight")
                cache["irDistance"] = result.get("irDistance")

                cache["light"] = result.get("light")
                cache["fan"] = result.get("fan")
                cache["window"] = result.get("window")
                
                data = {
                    'control': cache["control"],
                    'fanTemp': cache["fanTemp"],
                    'dustWindow': cache["dustWindow"],
                    'petLight': cache["petLight"],
                    'irDistance': cache["irDistance"],
                    'light': cache["light"],
                    'fan': cache["fan"],
                    'window': cache["window"],
                }

                print("Fetched data:", data)
                
                iface.write_msg(data)
            else:
                print("No data retrieved or error in fetching data")

        except Exception as e:
            print(f"An error occurred: {e}")
            
        try:
            # Connect to MySQL database
            cloudDB = mysql.connector.connect(
                host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
                user="smartpetcomfort",
                password="swinburneaaronsarawakidauniversityjacklin",
                database="petcomfort_db"
            )
            cloudCursor = cloudDB.cursor(dictionary=True)
            
            # Capture an image using the camera
            frame = camera.capture_array()
            _, buffer = cv2.imencode('.jpg', frame)
            img_binary = buffer.tobytes()
            
            # Update the image column in the database
            update_image_query = "UPDATE Picam_Table SET image = %s WHERE piCamID = 1"
            cloudCursor.execute(update_image_query, (img_binary,))
            
            # Set takePhoto to FALSE in the database
            update_takephoto_query = "UPDATE Picam_Table SET takePhoto = FALSE WHERE piCamID = 1"
            cloudCursor.execute(update_takephoto_query)
            
            cloudDB.commit()
            
            return {"message": "Image captured and stored in the database. takePhoto set to FALSE."}
        except Exception as e:
            print("An error occurred:", e)
            return {"message": "An error occurred."}
        finally:
            if cloudDB.is_connected():
                cloudCursor.close()
                cloudDB.close()
    
    time.sleep(1)
    

def take_image():
    try:
        # Connect to MySQL database
        cloudDB = mysql.connector.connect(
            host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
            user="smartpetcomfort",
            password="swinburneaaronsarawakidauniversityjacklin",
            database="petcomfort_db"
        )
        cloudCursor = cloudDB.cursor(dictionary=True)

        # Capture an image using the camera
        print("Capturing image...")
        frame = camera.capture_array()
        _, buffer = cv2.imencode('.jpg', frame)
        img_binary = buffer.tobytes()
        print("Image captured successfully.")

        # Update the image column in the database
        update_image_query = "UPDATE Picam_Table SET image = %s WHERE piCamID = 1"
        cloudCursor.execute(update_image_query, (img_binary,))
        print("Image updated in database.")

        # Set takePhoto_cat to FALSE in the database
        update_takephoto_query = "UPDATE Picam_Table SET takePhoto_cat = FALSE WHERE piCamID = 1"
        cloudCursor.execute(update_takephoto_query)
        print("takePhoto_cat set to FALSE.")

        cloudDB.commit()
        print("Database commit successful.")

        return {"message": "Image captured and stored in the database. takePhoto_cat set to FALSE."}
    except mysql.connector.Error as db_err:
        print("Database error occurred:", db_err)
        return {"message": "Database error occurred."}
    except Exception as e:
        print("An error occurred:", e)
        return {"message": "An error occurred."}

    time.sleep(1)

arduino_petCounter = None
arduino_light = None
arduino_humidity = None
arduino_temperature_C = None
arduino_temperature_F = None
arduino_dustValue = None
arduino_window = None
arduino_fan = None
arduino_fanSpeed = None

def assign_values(response):
    global arduino_petCounter, arduino_light, arduino_humidity, arduino_temperature_C, arduino_temperature_F, arduino_dustValue, arduino_window, arduino_fan, arduino_fanSpeed
    if ('arduino_petCounter' in response):
        arduino_petCounter = response['arduino_petCounter']

    if ('arduino_light' in response):
        arduino_light = response['arduino_light']

    if ('arduino_humidity' in response):
        arduino_humidity = response['arduino_humidity']

    if ('arduino_temperature_C' in response):
        arduino_temperature_C = response['arduino_temperature_C']

    if ('arduino_temperature_F' in response):
        arduino_temperature_F = response['arduino_temperature_F']

    if ('arduino_dustValue' in response):
        arduino_dustValue = response['arduino_dustValue']

    if ('arduino_window' in response):
        arduino_window = response['arduino_window']

    if ('arduino_fan' in response):
        arduino_fan = response['arduino_fan']

    if ('arduino_fanSpeed' in response):
        arduino_fanSpeed = response['arduino_fanSpeed']

def process_data():
    print("Processing data")
    previous_cat_room_pet_number = None

    while True:
        response = iface.read_msg()

        if (response is None):
            continue
        
        print(f"Response: {response}")
        assign_values(response)
        
        window_state = 1 if arduino_window else 0
        fan_state = 1 if arduino_fan else 0
        light_state = 1 if arduino_light else 0
        
        localCursor.execute("""INSERT INTO Cat_Raw_Data (petCount, humidity, lightState, temperature_C, temperature_F, fanState, fanSpeed, windowState, 
                            dustLevel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (arduino_petCounter, arduino_humidity, light_state, 
                            arduino_temperature_C, arduino_temperature_F, fan_state, arduino_fanSpeed, window_state, arduino_dustValue))
        
        localDB.commit()
        
        if arduino_petCounter is not None:
            if arduino_petCounter != previous_cat_room_pet_number:
                previous_cat_room_pet_number = arduino_petCounter

                if arduino_petCounter == 0:

                    mqtt.on_publish_table(0,0,0,0,0,0,0,0)
                elif arduino_petCounter > 0:
                    
                    mqtt.on_publish_table(arduino_petCounter, light_state, arduino_humidity, arduino_temperature_C, arduino_temperature_F, window_state, fan_state, arduino_fanSpeed)
                    
                    mqtt.on_publish_dust(arduino_dustValue)

            elif arduino_petCounter > 0 and arduino_petCounter == previous_cat_room_pet_number:
                print("Inserting dust level")
                #mqtt.on_publish_dust(arduino_dustValue)
                #time.sleep(3)

        

thread = threading.Thread(target=process_data)
thread.start()
second_thread = threading.Thread(target=fetch_data)
second_thread.start()

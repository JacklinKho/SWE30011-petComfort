import json
import mysql.connector
import paho.mqtt.client as mqtt

# Define a callback function to handle incoming messages
def on_connectControl(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("home/devices/state")  # Subscribe to the topic

def on_messageControl(client, userdata, msg):
    print("Message received from topic: {}".format(msg.topic))
    
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON payload: {e}")
        return

    # Print the received data
    print("Received message payload:")
    print(json.dumps(payload, indent=2))
    
    # Extract states from payload
    lightState = payload.get('lightState')
    fanState = payload.get('fanState')
    windowState = payload.get('windowState')

    if lightState is None or fanState is None or windowState is None:
        print("Invalid payload, missing one or more states.")
        return
    
    # Connect to MySQL databases
    try:
        cloudDB = mysql.connector.connect(
            host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
            user="smartpetcomfort",
            password="swinburneaaronsarawakidauniversityjacklin",
            database="petcomfort_db"
        )
        print("Connected to cloud database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return
    
    cloudCursor = cloudDB.cursor(dictionary=True)

    # Insert data into Cat_Control_Table for cloud database
    try:
        with cloudDB.cursor() as cursor:
            cursor.execute("SELECT * FROM Cat_Control_Table LIMIT 1")
            existing_record = cursor.fetchone()

            if existing_record:
                cursor.execute(
                    "UPDATE Cat_Control_Table SET lightState = %s, fanState = %s, windowState = %s WHERE catControlID = 1",
                    (lightState, fanState, windowState)
                )
            else:
                sql = "INSERT INTO Cat_Control_Table (lightState, fanState, windowState) VALUES (%s, %s, %s)"
                cursor.execute(sql, (lightState, fanState, windowState))
        
        # Commit changes to the cloud database
        cloudDB.commit()
        print("Changes committed to cloud database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cloudCursor.close()
        cloudDB.close()
        print("Cloud database connection closed")
        
# Define a callback function to handle incoming messages
def on_connectAdjust(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("home/devices/threshold")  # Subscribe to the topic

def on_messageAdjust(client, userdata, msg):
    print("Message received from topic: {}".format(msg.topic))
    
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON payload: {e}")
        return

    # Print the received data
    print("Received message payload:")
    print(json.dumps(payload, indent=2))
    
    fanTemp = payload.get('fanTemp')
    dustWindow = payload.get('dustWindow')
    petLight = payload.get('petLight')
    irDistance = payload.get('irDistance')

    if fanTemp is None or dustWindow is None or petLight is None or irDistance is None:
        print("Invalid payload, missing one or more states.")
        return
    
    # Connect to MySQL databases
    try:
        cloudDB = mysql.connector.connect(
            host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
            user="smartpetcomfort",
            password="swinburneaaronsarawakidauniversityjacklin",
            database="petcomfort_db"
        )
        print("Connected to cloud database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return
    
    cloudCursor = cloudDB.cursor(dictionary=True)

    # Insert data into Cat_Control_Table for cloud database
    try:
        with cloudCursor.cursor() as cursor:
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
                cloudCursor.commit()

        print("Changes committed to cloud database")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cloudCursor.close()
        cloudDB.close()
        print("Cloud database connection closed")

# Paho MQTT client setup
client1 = mqtt.Client()
client1.on_connect = on_connectControl
client1.on_message = on_messageControl

# Connect to the MQTT broker
broker_address = "aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com"
broker_port = 8883
client1.tls_set(ca_certs="/home/pi/swe30011/cert/AmazonRootCA1.pem",
               certfile="/home/pi/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-certificate.pem.crt",
               keyfile="/home/pi/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-private.pem.key")

print("Connecting to MQTT broker...")
client1.connect(broker_address, broker_port, 60)
print("Connected to MQTT broker")

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client1.loop_forever()

# Paho MQTT client setup
client2 = mqtt.Client()
client2.on_connect = on_connectAdjust
client2.on_message = on_messageAdjust

# Connect to the MQTT broker
broker_address = "aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com"
broker_port = 8883
client2.tls_set(ca_certs="/home/pi/swe30011/cert/AmazonRootCA1.pem",
               certfile="/home/pi/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-certificate.pem.crt",
               keyfile="/home/pi/swe30011/cert/1428cadeec4a4d8b8b7376dd5ffb9ddf1045e3ba425f7548d89794156cb07ca5-private.pem.key")

print("Connecting to MQTT broker...")
client2.connect(broker_address, broker_port, 60)
print("Connected to MQTT broker")

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client2.loop_forever()
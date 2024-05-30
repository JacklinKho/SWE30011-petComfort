
import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import mysql.connector
import threading
# Connect to MySQL database
mydb = mysql.connector.connect(host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
                               user="smartpetcomfort", password="swinburneaaronsarawakidauniversityjacklin", database="petcomfort_db")

cloudCursor = mydb.cursor(dictionary=True)
def upload_dog():
    # Initialize the MQTT client
    myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
    myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials(
        "/home/ubuntu/swe30011/dogcert/AmazonRootCA1.pem", 
        "/home/ubuntu/swe30011/dogcert/1e9c2c876f0a4d42b254ba15134dc8896c53c125a20f4ab7fb48c2275129366b-private.pem.key", 
        "/home/ubuntu/swe30011/dogcert/1e9c2c876f0a4d42b254ba15134dc8896c53c125a20f4ab7fb48c2275129366b-certificate.pem.crt"
    )
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Define the callback function to handle incoming messages
    def message_callback(client, userdata, message):
        payload = json.loads(message.payload.decode())
        
        petCounter = payload.get("petCounter")
        light = payload.get("light")
        humidity = payload.get("humidity")
        temperature_C = payload.get("temperature_C")
        temperature_F = payload.get("temperature_F")
        window = payload.get("window")
        fan = payload.get("fan")
        fanSpeed = payload.get("fanSpeed")
        
        cloudCursor.execute(
            "INSERT INTO Dog_Table (petCount, lightState, humidity, temperature_C, temperature_F, windowState, fanState, fanSpeed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (petCounter, light, humidity, temperature_C, temperature_F, window, fan, fanSpeed)
        )
        # Commit the transaction if necessary
        mydb.commit()

    # Connect to AWS IoT once
    myMQTTClient.connect()
    
    # Subscribe to the topic with the callback
    myMQTTClient.subscribe("dog/post/table", 1, message_callback)
    
    # Keep the script running to continue listening for messages
    while True:
        time.sleep(1)

def upload_dog_dust():
    # Initialize the MQTT client
    myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
    myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials(
        "/home/ubuntu/swe30011/dogcert/AmazonRootCA1.pem", 
        "/home/ubuntu/swe30011/dogcert/1e9c2c876f0a4d42b254ba15134dc8896c53c125a20f4ab7fb48c2275129366b-private.pem.key", 
        "/home/ubuntu/swe30011/dogcert/1e9c2c876f0a4d42b254ba15134dc8896c53c125a20f4ab7fb48c2275129366b-certificate.pem.crt"
    )
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    def message_callback(client, userdata, message):
        payload = json.loads(message.payload.decode())
        dustLevel = payload.get("dustLevel")
        
        # Fetch the latest dogTableID from Dog_Table
        cloudCursor.execute("SELECT dogTableId FROM Dog_Table ORDER BY dogTableID DESC LIMIT 1")
        row = cloudCursor.fetchone()
        if row is not None:
            latest_dogTableID = row["dogTableId"]
            
            # Insert data into Dog_Dust_Table
            cloudCursor.execute(
                "INSERT INTO Dog_Dust_Table (dogTableId, dustLevel) VALUES (%s, %s)",
                (latest_dogTableID, dustLevel)
            )
            # Commit the transaction if necessary
            mydb.commit()
        else:
            print("No valid dogTableID found.")

    # Connect to AWS IoT once
    myMQTTClient.connect()
    
    # Subscribe to the topic with the callback
    myMQTTClient.subscribe("dog/post/dust", 1, message_callback)
    
    # Keep the script running to continue listening for messages
    while True:
        time.sleep(1)
        
def upload_cat():
    # Initialize the MQTT client
    myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
    myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials(
        "/home/ubuntu/swe30011/catcert/AmazonRootCA1.pem", 
        "/home/ubuntu/swe30011/catcert/f1a759b8aa5e45ab38f13351635238a989e2f9d3ee4c884498da7340e6d90869-private.pem.key", 
        "/home/ubuntu/swe30011/catcert/f1a759b8aa5e45ab38f13351635238a989e2f9d3ee4c884498da7340e6d90869-certificate.pem.crt"
    )
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Define the callback function to handle incoming messages
    def message_callback(client, userdata, message):
        payload = json.loads(message.payload.decode())
        
        petCounter = payload.get("petCounter")
        light = payload.get("light")
        humidity = payload.get("humidity")
        temperature_C = payload.get("temperature_C")
        temperature_F = payload.get("temperature_F")
        window = payload.get("window")
        fan = payload.get("fan")
        fanSpeed = payload.get("fanSpeed")
        
        cloudCursor.execute(
            "INSERT INTO Cat_Table (petCount, lightState, humidity, temperature_C, temperature_F, windowState, fanState, fanSpeed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (petCounter, light, humidity, temperature_C, temperature_F, window, fan, fanSpeed)
        )
        # Commit the transaction if necessary
        mydb.commit()

    # Connect to AWS IoT once
    myMQTTClient.connect()
    
    # Subscribe to the topic with the callback
    myMQTTClient.subscribe("cat/post/table", 1, message_callback)
    
    # Keep the script running to continue listening for messages
    while True:
        time.sleep(1)

def upload_cat_dust():
    # Initialize the MQTT client
    myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
    myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials(
        "/home/ubuntu/swe30011/catcert/AmazonRootCA1.pem", 
        "/home/ubuntu/swe30011/catcert/f1a759b8aa5e45ab38f13351635238a989e2f9d3ee4c884498da7340e6d90869-private.pem.key", 
        "/home/ubuntu/swe30011/catcert/f1a759b8aa5e45ab38f13351635238a989e2f9d3ee4c884498da7340e6d90869-certificate.pem.crt"
    )
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    def message_callback(client, userdata, message):
        payload = json.loads(message.payload.decode())
        dustLevel = payload.get("dustLevel")
        
        # Fetch the latest catTableID from Cat_Table
        cloudCursor.execute("SELECT catTableId FROM Cat_Table ORDER BY catTableID DESC LIMIT 1")
        row = cloudCursor.fetchone()
        if row is not None:
            latest_catTableID = row["catTableId"]
            
            # Insert data into Cat_Dust_Table
            cloudCursor.execute(
                "INSERT INTO Cat_Dust_Table (catTableId, dustLevel) VALUES (%s, %s)",
                (latest_catTableID, dustLevel)
            )
            # Commit the transaction if necessary
            mydb.commit()
        else:
            print("No valid catTableID found.")

    # Connect to AWS IoT once
    myMQTTClient.connect()
    
    # Subscribe to the topic with the callback
    myMQTTClient.subscribe("cat/post/dust", 1, message_callback)
    
    # Keep the script running to continue listening for messages
    while True:
        time.sleep(1)
        
        
def upload_pig():
    # Initialize the MQTT client
    myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
    myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials(
        "/home/ubuntu/swe30011/pigcert/AmazonRootCA1.pem", 
        "/home/ubuntu/swe30011/pigcert/19dfd3616901c00d05996913c4bbfbd44a55e42b2aa9ec755673c546303812e8-private.pem.key", 
        "/home/ubuntu/swe30011/pigcert/19dfd3616901c00d05996913c4bbfbd44a55e42b2aa9ec755673c546303812e8-certificate.pem.crt"
    )
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Define the callback function to handle incoming messages
    def message_callback(client, userdata, message):
        payload = json.loads(message.payload.decode())
        
        petCounter = payload.get("petCounter")
        light = payload.get("light")
        humidity = payload.get("humidity")
        temperature_C = payload.get("temperature_C")
        temperature_F = payload.get("temperature_F")
        window = payload.get("window")
        fan = payload.get("fan")
        fanSpeed = payload.get("fanSpeed")
        
        cloudCursor.execute(
            "INSERT INTO Pig_Table (petCount, lightState, humidity, temperature_C, temperature_F, windowState, fanState, fanSpeed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (petCounter, light, humidity, temperature_C, temperature_F, window, fan, fanSpeed)
        )
        # Commit the transaction if necessary
        mydb.commit()

    # Connect to AWS IoT once
    myMQTTClient.connect()
    
    # Subscribe to the topic with the callback
    myMQTTClient.subscribe("pig/post/table", 1, message_callback)
    
    # Keep the script running to continue listening for messages
    while True:
        time.sleep(1)

def upload_pig_dust():
    # Initialize the MQTT client
    myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
    myMQTTClient.configureEndpoint("aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com", 8883)
    myMQTTClient.configureCredentials(
        "/home/ubuntu/swe30011/pigcert/AmazonRootCA1.pem", 
        "/home/ubuntu/swe30011/pigcert/19dfd3616901c00d05996913c4bbfbd44a55e42b2aa9ec755673c546303812e8-private.pem.key", 
        "/home/ubuntu/swe30011/pigcert/19dfd3616901c00d05996913c4bbfbd44a55e42b2aa9ec755673c546303812e8-certificate.pem.crt"
    )
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    def message_callback(client, userdata, message):
        payload = json.loads(message.payload.decode())
        dustLevel = payload.get("dustLevel")
        
        # Fetch the latest pigTableID from Pig_Table
        cloudCursor.execute("SELECT pigTableId FROM Pig_Table ORDER BY pigTableID DESC LIMIT 1")
        row = cloudCursor.fetchone()
        if row is not None:
            latest_pigTableID = row["pigTableId"]
            
            # Insert data into Pig_Dust_Table
            cloudCursor.execute(
                "INSERT INTO Pig_Dust_Table (pigTableId, dustLevel) VALUES (%s, %s)",
                (latest_pigTableID, dustLevel)
            )
            # Commit the transaction if necessary
            mydb.commit()
        else:
            print("No valid pigTableID found.")

    # Connect to AWS IoT once
    myMQTTClient.connect()
    
    # Subscribe to the topic with the callback
    myMQTTClient.subscribe("pig/post/dust", 1, message_callback)
    
    # Keep the script running to continue listening for messages
    while True:
        time.sleep(1)



if __name__ == '__main__':

    upload_dog_thread = threading.Thread(target=upload_dog)
    upload_dog_dust_thread = threading.Thread(target=upload_dog_dust)
    
    upload_pig_thread = threading.Thread(target=upload_pig)
    upload_pig_dust_thread = threading.Thread(target=upload_pig_dust)
    
    upload_cat_thread = threading.Thread(target=upload_cat)
    upload_cat_dust_thread = threading.Thread(target=upload_cat_dust)

    upload_dog_thread.start()
    upload_dog_dust_thread.start()

    upload_pig_thread.start()
    upload_pig_dust_thread.start()
    
    upload_cat_thread.start()
    upload_cat_dust_thread.start()
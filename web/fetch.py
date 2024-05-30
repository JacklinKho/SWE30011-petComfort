import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import mysql.connector
import threading

# Cache dictionary to store data
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

# Connect to MySQL database
mydb = mysql.connector.connect(host="database-1.cjjqkkvq5tm1.us-east-1.rds.amazonaws.com",
                               user="smartpetcomfort", password="swinburneaaronsarawakidauniversityjacklin", database="petcomfort_db")

cloudCursor = mydb.cursor(dictionary=True)

def fetch_dog_data():
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

    # Connect to AWS IoT once
    myMQTTClient.connect()

    while True:
        try:
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT Mode_Table.control, 
                        Dog_Adjust_Table.fanTemp, Dog_Adjust_Table.dustWindow, Dog_Adjust_Table.petLight, Dog_Adjust_Table.irDistance, 
                        Dog_Control_Table.* 
                    FROM Mode_Table 
                    LEFT JOIN Dog_Adjust_Table ON 1=1
                    LEFT JOIN Dog_Control_Table ON 1=1 
                    LIMIT 1
                """)
                
                raw_data = cursor.fetchone()
                if raw_data:
                    cache["control"] = raw_data["control"]
                    cache["fanTemp"] = raw_data["fanTemp"]
                    cache["dustWindow"] = raw_data["dustWindow"]
                    cache["petLight"] = raw_data["petLight"]
                    cache["irDistance"] = raw_data["irDistance"]

                    cache["light"] = raw_data["lightState"]
                    cache["fan"] = raw_data["fanState"]
                    cache["window"] = raw_data["windowState"]
                    
                    data = {
                        'control': 1 if cache['control'] == 'true' else 0,
                        'fanTemp': cache["fanTemp"],
                        'dustWindow': cache["dustWindow"],
                        'petLight': cache["petLight"],
                        'irDistance': cache["irDistance"],
                        'light': cache["light"],
                        'fan': cache["fan"],
                        'window': cache["window"],
                    }
                    
                    # Convert the dictionary to JSON format
                    payload = json.dumps(data)

                    # Publish the JSON payload to a topic
                    myMQTTClient.publish("dog/get/table", payload, 0)
                    
                    print("Data sent successfully")
                else:
                    print("No data retrieved from the database.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Wait for a specified amount of time before the next iteration
        time.sleep(3)  # Delay for 10 seconds
        
def fetch_cat_data():
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

    # Connect to AWS IoT once
    myMQTTClient.connect()

    while True:
        try:
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT Mode_Table.control, 
                        Cat_Adjust_Table.fanTemp, Cat_Adjust_Table.dustWindow, Cat_Adjust_Table.petLight, Cat_Adjust_Table.irDistance, 
                        Cat_Control_Table.* 
                    FROM Mode_Table 
                    LEFT JOIN Cat_Adjust_Table ON 1=1
                    LEFT JOIN Cat_Control_Table ON 1=1 
                    LIMIT 1
                """)
                
                raw_data = cursor.fetchone()
                if raw_data:
                    cache["control"] = raw_data["control"]
                    cache["fanTemp"] = raw_data["fanTemp"]
                    cache["dustWindow"] = raw_data["dustWindow"]
                    cache["petLight"] = raw_data["petLight"]
                    cache["irDistance"] = raw_data["irDistance"]

                    cache["light"] = raw_data["lightState"]
                    cache["fan"] = raw_data["fanState"]
                    cache["window"] = raw_data["windowState"]
                    
                    data = {
                        'control': 1 if cache['control'] == 'true' else 0,
                        'fanTemp': cache["fanTemp"],
                        'dustWindow': cache["dustWindow"],
                        'petLight': cache["petLight"],
                        'irDistance': cache["irDistance"],
                        'light': cache["light"],
                        'fan': cache["fan"],
                        'window': cache["window"],
                    }
                    
                    # Convert the dictionary to JSON format
                    payload = json.dumps(data)

                    # Publish the JSON payload to a topic
                    myMQTTClient.publish("cat/get/table", payload, 0)
                    
                    print("Data sent successfully")
                else:
                    print("No data retrieved from the database.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Wait for a specified amount of time before the next iteration
        time.sleep(3)  # Delay for 10 seconds
        
def fetch_pig_data():
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

    # Connect to AWS IoT once
    myMQTTClient.connect()

    while True:
        try:
            with mydb.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT Mode_Table.control, 
                        Pig_Adjust_Table.fanTemp, Pig_Adjust_Table.dustWindow, Pig_Adjust_Table.petLight, Pig_Adjust_Table.irDistance, 
                        Pig_Control_Table.* 
                    FROM Mode_Table 
                    LEFT JOIN Pig_Adjust_Table ON 1=1
                    LEFT JOIN Pig_Control_Table ON 1=1 
                    LIMIT 1
                    """)
                
                raw_data = cursor.fetchone()
                if raw_data:
                    cache["control"] = raw_data["control"]
                    cache["fanTemp"] = raw_data["fanTemp"]
                    cache["dustWindow"] = raw_data["dustWindow"]
                    cache["petLight"] = raw_data["petLight"]
                    cache["irDistance"] = raw_data["irDistance"]

                    cache["light"] = raw_data["lightState"]
                    cache["fan"] = raw_data["fanState"]
                    cache["window"] = raw_data["windowState"]
                    
                    data = {
                        'control': 1 if cache['control'] == 'true' else 0,
                        'fanTemp': cache["fanTemp"],
                        'dustWindow': cache["dustWindow"],
                        'petLight': cache["petLight"],
                        'irDistance': cache["irDistance"],
                        'light': cache["light"],
                        'fan': cache["fan"],
                        'window': cache["window"],
                    }
                    
                    # Convert the dictionary to JSON format
                    payload = json.dumps(data)

                    # Publish the JSON payload to a topic
                    myMQTTClient.publish("pig/get/table", payload, 0)
                    
                    print("Data sent successfully")
                else:
                    print("No data retrieved from the database.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Wait for a specified amount of time before the next iteration
        time.sleep(3)  # Delay for 10 seconds

if __name__ == '__main__':
    dog_thread = threading.Thread(target=fetch_dog_data)
    cat_thread = threading.Thread(target=fetch_cat_data)
    pig_thread = threading.Thread(target=fetch_pig_data)

    dog_thread.start()
    cat_thread.start()
    pig_thread.start()

# dogGlobalMQTT.py

import paho.mqtt.client as mqtt
import json
import logging

class dogGlobalMQTT:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.message_payload = None

        # Connect to the MQTT broker
        broker_address = "aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com"
        broker_port = 8883
        self.client.tls_set(
            ca_certs="/home/pi/swe30011/dogcert/AmazonRootCA1.pem",
            certfile="/home/pi/swe30011/dogcert/1e9c2c876f0a4d42b254ba15134dc8896c53c125a20f4ab7fb48c2275129366b-certificate.pem.crt",
            keyfile="/home/pi/swe30011/dogcert/1e9c2c876f0a4d42b254ba15134dc8896c53c125a20f4ab7fb48c2275129366b-private.pem.key"
        )

        logging.info("Connecting to MQTT broker...")
        self.client.connect(broker_address, broker_port, 60)
        logging.info("Connected to MQTT broker")

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Connected with result code {rc}")
        client.subscribe("dog/get/table")

    def on_message(self, client, userdata, msg):
        logging.info(f"Message received from topic: {msg.topic}")
        try:
            self.message_payload = json.loads(msg.payload.decode())
            logging.info("Received message payload:")
            logging.info(json.dumps(self.message_payload, indent=2))
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON payload: {e}")

    def on_fetch(self):
        return self.message_payload

    def on_publish_table(self, petCounter, light, humidity, temperature_C, temperature_F, window, fan, fanSpeed):
        data = {
            "petCounter": petCounter,
            "light": light,
            "humidity": humidity,
            "temperature_C": temperature_C,
            "temperature_F": temperature_F,
            "window": window,
            "fan": fan,
            "fanSpeed": fanSpeed
        }

        payload = json.dumps(data)
        self.client.publish("dog/post/table", payload, 0)

    def on_publish_dust(self, dustLevel):
        data = {
            "dustLevel": dustLevel
        }

        payload = json.dumps(data)
        self.client.publish("dog/post/dust", payload, 0)


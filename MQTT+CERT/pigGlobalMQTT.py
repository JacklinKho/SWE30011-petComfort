# pigGlobalMQTT.py

import paho.mqtt.client as mqtt
import json
import logging

class pigGlobalMQTT:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.message_payload = None

        # Connect to the MQTT broker
        broker_address = "aadckvyc4ktri-ats.iot.us-east-1.amazonaws.com"
        broker_port = 8883
        self.client.tls_set(
            ca_certs="/home/pi/swe30011/pigcert/AmazonRootCA1.pem",
            certfile="/home/pi/swe30011/pigcert/19dfd3616901c00d05996913c4bbfbd44a55e42b2aa9ec755673c546303812e8-certificate.pem.crt",
            keyfile="/home/pi/swe30011/pigcert/19dfd3616901c00d05996913c4bbfbd44a55e42b2aa9ec755673c546303812e8-private.pem.key"
        )

        logging.info("Connecting to MQTT broker...")
        self.client.connect(broker_address, broker_port, 60)
        logging.info("Connected to MQTT broker")

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Connected with result code {rc}")
        client.subscribe("pig/get/table")

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
        self.client.publish("pig/post/table", payload, 0)

    def on_publish_dust(self, dustLevel):
        data = {
            "dustLevel": dustLevel
        }

        payload = json.dumps(data)
        self.client.publish("pig/post/dust", payload, 0)


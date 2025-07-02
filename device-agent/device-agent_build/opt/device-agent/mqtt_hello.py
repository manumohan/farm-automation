"""
MQTT Hello World Script for Raspberry Pi Device Agent

- Reference: REQUIREMENTS.md, SETUP.md
- This script demonstrates basic MQTT connectivity and message handling.
"""

import paho.mqtt.client as mqtt
import os

BROKER = os.getenv('MQTT_BROKER', 'mqtt.eclipseprojects.io')
PORT = int(os.getenv('MQTT_PORT', 1883))
TOPIC = os.getenv('MQTT_TEST_TOPIC', 'farm-automation/test')


def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker at {BROKER}:{PORT} with result code {rc}")
    client.subscribe(TOPIC)
    print(f"Subscribed to topic: {TOPIC}")


def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Connecting to MQTT broker at {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    main() 
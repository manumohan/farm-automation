import paho.mqtt.client as mqtt
import time

BROKER = 'mqtt.eclipseprojects.io'  # Public broker for dev/testing
PORT = 1883
TOPIC = 'farm-automation/test'


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} {msg.payload.decode()}")


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Connecting to MQTT broker at {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, 60)

    # Blocking loop
    client.loop_forever()


if __name__ == "__main__":
    main() 
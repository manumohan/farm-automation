import paho.mqtt.client as mqtt
import time
import json
import argparse
import os
from datetime import datetime
import threading

DEFAULT_CONFIG_PATH = '/etc/device-agent/config.json'

def load_config(config_path):
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        exit(1)
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(f"[AGENT] Loaded config: {config}")
    return config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default=DEFAULT_CONFIG_PATH, help='Path to config file')
    args = parser.parse_args()
    config = load_config(args.config)

    broker = config.get('mqtt_broker', 'localhost')
    port = config.get('mqtt_port', 1883)
    device_id = config.get('deviceId')
    farm_id = config.get('farmId')
    status_interval = int(config.get('status_interval', 60))  # seconds
    if not device_id or not farm_id:
        print(f"[AGENT][ERROR] deviceId and farmId are required in config. Got deviceId={device_id}, farmId={farm_id}")
        exit(1)
    topic = f"farm/{farm_id}/device/{device_id}/status"
    print(f"[AGENT] Using topic: {topic}")
    print(f"[AGENT] Status publish interval: {status_interval} seconds")

    client = mqtt.Client()

    def publish_status():
        payload = json.dumps({
            "status": "online",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        })
        print(f"[AGENT] Publishing status to {topic}: {payload}")
        client.publish(topic, payload)

    def on_connect(client, userdata, flags, rc):
        print(f"[AGENT] Connected with result code {rc}")
        client.subscribe(topic)
        publish_status()  # Publish immediately on connect

    def on_message(client, userdata, msg):
        print(f"[AGENT] Received message: {msg.topic} {msg.payload.decode()}")

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[AGENT] Connecting to MQTT broker at {broker}:{port}...")
    client.connect(broker, port, 60)

    # Start periodic status publishing in a background thread
    def periodic_status():
        while True:
            time.sleep(status_interval)
            publish_status()

    threading.Thread(target=periodic_status, daemon=True).start()

    client.loop_forever()

if __name__ == "__main__":
    main() 
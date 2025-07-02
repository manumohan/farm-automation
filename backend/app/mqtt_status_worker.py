import os
import json
import re
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.device import Device
from app.db.base import Base
from app.core.config import settings
import threading

# MQTT config
MQTT_BROKER = settings.MQTT_BROKER
MQTT_PORT = settings.MQTT_PORT

TOPICS = [
    ('farm/+/device/+/status', 0),
    ('farm/+/device/+/logs', 0),
    ('farm/+/device/+/events', 0),
    ('farm/+/device/+/commands', 0),
]

# Database config
DB_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Regex to extract topic info
STATUS_REGEX = re.compile(r'farm/([^/]+)/device/([^/]+)/status')
LOGS_REGEX = re.compile(r'farm/([^/]+)/device/([^/]+)/logs')
EVENTS_REGEX = re.compile(r'farm/([^/]+)/device/([^/]+)/events')
COMMANDS_REGEX = re.compile(r'farm/([^/]+)/device/([^/]+)/commands')

def on_connect(client, userdata, flags, rc):
    print(f"[WORKER] Connected to MQTT broker with result code {rc}")
    for topic, qos in TOPICS:
        client.subscribe((topic, qos))
        print(f"[WORKER] Subscribed to topic: {topic}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    if STATUS_REGEX.match(topic):
        handle_status(topic, payload)
    elif LOGS_REGEX.match(topic):
        handle_logs(topic, payload)
    elif EVENTS_REGEX.match(topic):
        handle_events(topic, payload)
    elif COMMANDS_REGEX.match(topic):
        handle_commands(topic, payload)
    # else:  # Only log if you want to track unknown topics
    #     print("Unknown topic pattern.")

def handle_status(topic, payload):
    match = STATUS_REGEX.match(topic)
    if not match:
        print(f"[WORKER][WARN] Status topic does not match expected pattern: {topic}")
        return
    farm_id, device_id = match.groups()
    try:
        data = json.loads(payload)
        status = data.get('status', 'online')
        timestamp = data.get('timestamp')
        if timestamp:
            last_seen = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            last_seen = datetime.utcnow()
    except Exception as e:
        print(f"[WORKER][ERROR] Error parsing status payload: {e} | payload: {payload}")
        return
    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.device_uid == device_id, Device.is_deleted == False).first()
        if device:
            device.status = status
            setattr(device, 'last_seen', last_seen)
            db.commit()
            print(f"[WORKER] Updated device {device_id} status to {status} at {last_seen}")
        else:
            print(f"[WORKER][WARN] Device with device_uid {device_id} not found in DB. (topic: {topic})")
    except Exception as e:
        print(f"[WORKER][ERROR] DB error: {e}")
        db.rollback()
    finally:
        db.close()

def handle_logs(topic, payload):
    match = LOGS_REGEX.match(topic)
    if not match:
        return
    # Optionally store logs in DB

def handle_events(topic, payload):
    match = EVENTS_REGEX.match(topic)
    if not match:
        return
    # Optionally store events in DB

def handle_commands(topic, payload):
    match = COMMANDS_REGEX.match(topic)
    if not match:
        return
    # Optionally log command delivery/ack

def check_and_update_offline_devices():
    while True:
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            threshold_minutes = settings.offline_threshold_minutes
            devices = db.query(Device).filter(Device.is_deleted == False).all()
            for device in devices:
                last_seen = getattr(device, 'last_seen', None)
                if last_seen is not None:
                    minutes_since_seen = (now - last_seen).total_seconds() / 60
                    if minutes_since_seen > threshold_minutes and getattr(device, 'status', None) != 'offline':
                        print(f"[WORKER] Device {getattr(device, 'device_uid', None)} last seen {minutes_since_seen:.1f} min ago. Marking as offline.")
                        setattr(device, 'status', 'offline')
                        db.commit()
        except Exception as e:
            print(f"[WORKER][ERROR] Offline check failed: {e}")
            db.rollback()
        finally:
            db.close()
        time.sleep(60)  # check every minute

def main():
    print(f"[WORKER] Starting MQTT status worker...")
    print(f"[WORKER] MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        print(f"[WORKER] Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"[WORKER] Successfully connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"[WORKER][ERROR] Failed to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}: {e}")
        return
    threading.Thread(target=check_and_update_offline_devices, daemon=True).start()
    client.loop_forever()

if __name__ == "__main__":
    main() 
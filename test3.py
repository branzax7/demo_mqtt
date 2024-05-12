import time
import json
import pytz
import paho.mqtt.client as mqtt 
from random import choice
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("Message Published...")

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
TIMEZONE = "Europe/Bucharest"

# Set up the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the MQTT broker
client.connect("broker.hivemq.com", 1883, 60)

# This loop simulates sending messages
# data = ["data1","buna","ce faci","bravo", "scaun"]
data = ["xxxx","yyyy","mmmmm","nnnnn", "scssssssaun"]
client.loop_start()
while True:
    # message = input("Enter message to publish: ")
    # client.publish("sprc/chat/v1p3r4", random.choice(data))
    # time.sleep(1)  # Pause for a second before next input
    battery = choice(list(range(1, 101)))
    humidity = choice(list(range(20, 81)))
    temperature = choice(list(range(150, 280))) / 10
    non_numerical_option = "PRJ"
    non_numerical_value = "SPRC"

    location = choice(["UPB", "Dorinel"])
    station = choice(["RPi_1", "Zeus"])

    payload = {
        "BAT": float(battery),
        "HUMID": float(humidity),
        "TMP": float(temperature),
        non_numerical_option: non_numerical_value,
    }

    include_timestamp = choice([False, True])

    if include_timestamp:
        payload.update({'timestamp': datetime.strftime(datetime.now(pytz.timezone(TIMEZONE)), TIME_FORMAT)})

    publish_location = location + "/" + station
    # publish_location = "sprc/chat/v1p3r4"
    client.publish(publish_location, json.dumps(payload))

    print("", json.dumps(payload), " into ", publish_location)

    # Wait for 1 second
    time.sleep(1)

# Optional: client.loop_stop() can be called when done, if not running indefinitely

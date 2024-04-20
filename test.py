import paho.mqtt.client as mqtt
import time
import random

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("Message Published...")

# Set up the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the MQTT broker
client.connect("broker.hivemq.com", 1883, 60)

# This loop simulates sending messages
data = ["data1","buna","ce faci","bravo", "scaun"]
client.loop_start()
while True:
    # message = input("Enter message to publish: ")
    client.publish("sprc/chat/v1p3r4", random.choice(data))
    time.sleep(1)  # Pause for a second before next input

# Optional: client.loop_stop() can be called when done, if not running indefinitely

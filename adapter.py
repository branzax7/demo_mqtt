import os
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

# Read environment variables
mqtt_host = os.getenv('MQTT_HOST', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
influxdb_host = os.getenv('INFLUXDB_HOST', 'localhost')
influxdb_port = int(os.getenv('INFLUXDB_PORT', 8086))

# Initialize the InfluxDB client
influx_client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
influx_client.switch_database('mqtt_data')

# MQTT setup...
# Similar to previous setup for MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("sprc/chat/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " received message " + str(msg.payload))
    json_body = [
        {
            "measurement": "mqtt_messages",
            "tags": {
                "topic": msg.topic
            },
            "fields": {
                "value": str(msg.payload.decode('utf-8'))
            }
        }
    ]
    # Write the data to InfluxDB
    influx_client.write_points(json_body)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)

client.loop_forever()


import os
import re
import pytz
import json
from json.decoder import JSONDecodeError
import logging
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from datetime import datetime

# Read environment variables
mqtt_host = os.getenv('MQTT_HOST', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
influxdb_host = os.getenv('INFLUXDB_HOST', 'localhost')
influxdb_port = int(os.getenv('INFLUXDB_PORT', 8086))

# Initialize the InfluxDB client
influx_client = InfluxDBClient(host=influxdb_host, port=influxdb_port)
influx_client.switch_database('mqtt_data')
query = 'DROP SERIES FROM /.*/'
influx_client.query(query)

# MQTT setup...
# Similar to previous setup for MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("UPB/#")
    client.subscribe("Dorinel/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    # Extract the topic from the message
    topic = message.topic
    topic_matches = re.match(r"(?P<location>[^/]*?)/(?P<station>.*)", topic)

    # If the topic is not in the correct format, log the error and return
    if not topic_matches:
        logging.info("Wrong format {topic}".format(topic=topic))
        return

    location = topic_matches['location']
    station = topic_matches['station']

    # Log the message if DEBUG_DATA_FLOW is 'true'
    if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
        log_message = f"Received a message by topic {location}/{station}"
        logging.info(log_message)

    payload = json.loads(message.payload)

    # Extract the timestamp from the payload if it doesn't exist, use the current time
    timestamp = payload.get('timestamp', datetime.now(pytz.timezone("Europe/Bucharest")).strftime("%Y-%m-%dT%H:%M:%S%z"))

    # Log the timestamp if DEBUG_DATA_FLOW is 'true'
    if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
        timestamp_log_message = f"Data timestamp is {timestamp}" if 'timestamp' in payload else "Data timestamp is NOW"
        logging.info(timestamp_log_message)

    # Create a list of 'to-add' data
    db_data = []
    logging.info("payload!!!!!!!")
    logging.info(payload)



    # For each key-value pair in the payload
    for key, value in payload.items():
        # Check if the value is a numeric type or if the key is "timestamp"
        # if not (isinstance(value, (int, float)) or key == "timestamp"):
        if isinstance(value, str):
            # logging.info("OPRIRE FAAAAAAAAAAAAAAAAA")
            # break
            continue
        # logging.info("KEya, value este: ", key, value)
        # Log the field if DEBUG_DATA_FLOW is 'true'
        if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
            log_message = f"{location}.{station}.{key} {value}"
            logging.info(log_message)

        # Build the measurement as <station>.<key>
        measurement = f"{station}.{key}"

        # Build the entry object
        entry = {
            'measurement': measurement,
            'tags': {
                'location': location,
                'station': station,
            },
            'fields': {
                'value': value
            },
            'time': timestamp
        }
        # entry = {
        #     'measurement': measurement,
        #     'tags': {
        #         "topic": message.topic
        #     },
        #     'fields': {
        #         'value': value
        #     },
        #     'time': timestamp
        # }

        # Add the current entry to the list of 'to-add' data
        
        db_data.append(entry)

    # If at least one field was valid, add the data in the database
    if db_data:
        if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
            logging.info(f"Adding data to the database: {db_data}")

        # Assuming 'influxdb_client' is properly initialized before this point
        influx_client.write_points(db_data)
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
# Configure the logging module
logging.basicConfig(filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

client.connect("broker.hivemq.com", 1883, 60)

client.loop_forever()


import os
import re
import pytz
import json
import logging
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from datetime import datetime

# Define the callback function for the MQTT client
def on_message(message):
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

    # For each key-value pair in the payload
    for key, value in payload.items():
        # Check if the value is a numeric type or if the key is "timestamp"
        if not (isinstance(value, (int, float)) or key == "timestamp"):
            continue

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

        # Add the current entry to the list of 'to-add' data
        db_data.append(entry)

    # If at least one field was valid, add the data in the database
    if db_data:
        if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
            logging.info(f"Adding data to the database: {db_data}")

        # Assuming 'influxdb_client' is properly initialized before this point
        influxdb_client.write_points(db_data)


def main():
    # Create an InfluxDB client
    influxdb_client = InfluxDBClient(os.environ.get("INFLUXDB_HOST", "influxdb"))
    influxdb_client.switch_database(os.environ.get("INFLUXDB_DB", "mqtt_data"))

    # Create an MQTT client
    client = mqtt.Client("SPRC Adaptor")

    # Connect the MQTT client to the broker and subscribe to all topics
    client.connect(os.environ.get("MQTTBROKER_HOST", "mqtt_broker"))
    client.subscribe("#")
    client.on_message = on_message 

    # Configure the logging module
    logging.basicConfig(filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

    # Log the start of the adaptor
    if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
        logging.info("Adaptor started, connected to the broker, and is now listening")

    # Start the MQTT client loop
    client.loop_forever()

if __name__ == "__main__":
    # Initialize InfluxDB client to None
    influxdb_client = None
    # Call the main function
    main()
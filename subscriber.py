import paho.mqtt.client as mqtt
import json
from datetime import datetime
from dotenv import load_dotenv
import os

def process_json(json_str):
    # Parse the JSON string
    data = json.loads(json_str)

    # Convert "Time" to milliseconds since epoch
    time_dt = datetime.fromisoformat(data["Time"])
    time_ms = int(time_dt.timestamp() * 1000)

    # Extract ENERGY data into variables
    total_start_time = data["ENERGY"]["TotalStartTime"]
    total = data["ENERGY"]["Total"]
    yesterday = data["ENERGY"]["Yesterday"]
    today = data["ENERGY"]["Today"]
    period = data["ENERGY"]["Period"]
    power = data["ENERGY"]["Power"]
    apparent_power = data["ENERGY"]["ApparentPower"]
    reactive_power = data["ENERGY"]["ReactivePower"]
    factor = data["ENERGY"]["Factor"]
    voltage = data["ENERGY"]["Voltage"]
    current = data["ENERGY"]["Current"]

    return {
	"timestamp": time_ms,
        "power": power,
        "apparentPower": apparent_power,
        "reactivePower": reactive_power,
        "factor": factor,
        "voltage": voltage,
        "current": current,
	"todaykWh": today,
	"yesterdaykWh": yesterday,
    }

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    print("timestamp,power,apparentPower,reactivePower,factor,voltage,current,todaykWh,yesterdaykWh")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("tele/tasmota_switch/SENSOR")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = process_json(msg.payload)
    print("{},{},{},{},{},{},{},{},{}".format(data["timestamp"], data["power"], data["apparentPower"], data["reactivePower"], data["factor"],data["voltage"],data["current"],data["todaykWh"],data["yesterdaykWh"]))


load_dotenv()
MQTT_BROKER_IP_ADDR = os.getenv('MQTT_BROKER_IP_ADDR')
MQTT_BROKER_PORT_NUM = os.getenv('MQTT_BROKER_PORT_NUM')
MQTT_BROKER_USERNAME = os.getenv('MQTT_BROKER_USERNAME')
MQTT_BROKER_PASSWORD = os.getenv('MQTT_BROKER_PASSWORD')

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(MQTT_BROKER_USERNAME, MQTT_BROKER_PASSWORD)  # Replace with your MQTT account username and password


mqttc.connect(MQTT_BROKER_IP_ADDR, int(MQTT_BROKER_PORT_NUM), 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()

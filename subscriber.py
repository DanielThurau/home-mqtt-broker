from datetime import datetime
from dotenv import load_dotenv
import json
import paho.mqtt.client as mqtt
import os


def process_json(json_str):
    # Parse the JSON string
    data = json.loads(json_str)

    # Convert "Time" to milliseconds since epoch
    time_dt = datetime.fromisoformat(data["Time"])
    time_ms = int(time_dt.timestamp() * 1000)

    _total_start_time = data["ENERGY"]["TotalStartTime"]
    _total = data["ENERGY"]["Total"]
    yesterday = data["ENERGY"]["Yesterday"]
    today = data["ENERGY"]["Today"]
    _period = data["ENERGY"]["Period"]
    power = data["ENERGY"]["Power"]
    apparent_power = data["ENERGY"]["ApparentPower"]
    reactive_power = data["ENERGY"]["ReactivePower"]
    factor = data["ENERGY"]["Factor"]
    voltage = data["ENERGY"]["Voltage"]
    current = data["ENERGY"]["Current"]

    return {
        "timestamp": time_ms,
        "power": power,
        "apparent_power": apparent_power,
        "reactive_power": reactive_power,
        "factor": factor,
        "voltage": voltage,
        "current": current,
        "today_kWh": today,
        "yesterday_kWh": yesterday,
    }


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, _userdata, _flags, reason_code, _properties):
    print(f"Connected with result code {reason_code}")
    print("timestamp,power,apparent_power,reactive_power,factor,voltage,current,today_kWh,yesterday_kWh")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("tele/tasmota_switch/SENSOR")


# The callback for when a PUBLISH message is received from the server.
def on_message(_client, _userdata, msg):
    data = process_json(msg.payload)
    print(f"{data['timestamp']},{data["power"]},{data["apparent_power"]},{data["reactive_power"]},{data["factor"]},{data["voltage"]},{data["current"]},{data["today_kWh"]},{data["yesterday_kWh"]}")


if __name__ == "__main__":
    # Load secrets
    load_dotenv()
    MQTT_BROKER_IP_ADDR = os.getenv('MQTT_BROKER_IP_ADDR')
    MQTT_BROKER_PORT_NUM = os.getenv('MQTT_BROKER_PORT_NUM')
    MQTT_BROKER_USERNAME = os.getenv('MQTT_BROKER_USERNAME')
    MQTT_BROKER_PASSWORD = os.getenv('MQTT_BROKER_PASSWORD')

    # Create the client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(MQTT_BROKER_USERNAME, MQTT_BROKER_PASSWORD)
    mqtt_client.connect(MQTT_BROKER_IP_ADDR, int(MQTT_BROKER_PORT_NUM), 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    mqtt_client.loop_forever()

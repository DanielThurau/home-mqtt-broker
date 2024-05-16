# home-mqtt-broker
GitHub repo with instructions on how I set up my home [mqtt](https://mqtt.org/) broker.

## Configuring And Starting The MQTT Broker 

I followed instructions [here](https://medium.com/gravio-edge-iot-platform/how-to-set-up-a-mosquitto-mqtt-broker-securely-using-client-certificates-82b2aaaef9c8), it was pretty easy to follow, although since this is running just on my home network and for a single subscriber and publisher, I am KISSing this project and just using username/password authentication.

Use `./apt-install.sh` to install dependencies for the [mosquitto open-source mqtt broker](https://mosquitto.org/) on an ubuntu machine.

I added the following values to `/etc/mosquitto/conf.d/mosquitto.conf` based on the tutorial's recommendation. I did skipp the websockets protocol because it was causing issues later on.

```
listener 1883
allow_anonymous false
password_file /etc/mosquitto/conf.d/tasmota_passwd
```

Make sure to edit the `/etc/mosquitto/conf.d/mosquitto.conf` file for user-defined configuration, not the base `/etc/mosquitto/mosquitto.conf`

To start and enable services on startup in the future, I used the following systemctl commands: 

```
$ sudo systemctl start mosquitto
$ sudo systemctl enable mosquitto
```

and tailed its journal to make sure everything seemed to be in working order:

```
$ journalctl -f -u mosquitto
systemd[1]: Starting Mosquitto MQTT Broker...
mosquitto[1388819]: 1713734106: Loading config file /etc/mosquitto/conf.d/mosquitto.conf
systemd[1]: Started Mosquitto MQTT Broker
```

I had my firewall already running on my hardened machine, so I opened port `1883` to accept local network connections:

```
$ sudo ufw allow 1883 
```

and used the following `lsof` command to check that mosquitto was listening on the port **AFTER** I got mosquitto running:

```
$ sudo lsof -i -P -n | grep LISTEN
mosquitto 1388819       mosquitto    5u  IPv4 6577531      0t0  TCP *:1883 (LISTEN)
mosquitto 1388819       mosquitto    6u  IPv6 6577532      0t0  TCP *:1883 (LISTEN)
```

Before I could test anything I need to generate the password file that was in the file `/etc/mosquitto/conf.d/mosquitto.conf`:

```
$ mosquitto_passwd -c /etc/mosquitto/conf.d/tasmota_passwd <USERNAME>
```

Then I could test out if the broker was working...

On my ubuntu machine, create a subscription to a dummy topic:
```
$ mosquitto_sub -h localhost -t "test" -u "<USERNAME>" -P "<PASSWORD>"
```

And on any other machine on a network capable device (most likely on the same ubuntu machine in a different tab):

```
$ mosquitto_pub -h localhost -t "test" -m "Hello World" -u "<USERNAME>" -P "PASSWORD"
```

You should see the "Hello World" message on the subscriber's terminal. IF so, great, the broker is working as expected. Now I just have to handle configuring the first real topic on my home network, my tasmota flashed sonoff plug.

## Programmatic Subscription 

I have a tasmota plug that publishes to a mqtt topic named `tele/tasmota_switch/SENSOR`, and can be configured to talk with a mqtt broker pretty easily. I configure the tasmota plug to talk to my hardened ubuntu machine running mosquitto. 

The published message looks like this:

```
{
    "Time":"2024-04-21T22:45:10",
    "ENERGY":{
        "TotalStartTime": "2024-04-21T22:32:49",
        "Total": 0.002,
        "Yesterday": 0.000,
        "Today": 0.002,
        "Period": 0,
        "Power": 11,
        "ApparentPower": 22,
        "ReactivePower": 19,
        "Factor": 0.49,
        "Voltage": 122,
        "Current": 0.181
    }
}
```

which is some easy JSON to process. The tasmota plug configures how often to send this telemetry, and I currently have it publish every 30 seconds. `subscriber.py` is a short python script that will subscribe to the topic, on a message it will process the json and convert it to row data, and print to stdout. In the next iteration I'll probably dump this into a sqlite db for use later.

## Data pipeline

I ended up writing [amleth](https://github.com/DanielThurau/amleth) to run on another home server. It subscribes to the broker 
and pushes messages down a processing pipeline that eventually inserts it into a database. It's pretty cool, you should check it out.

## Log Rotation

I set up mosquitto to be included in my logwatch daily email, but ended up needing to rotate the logs. Mosquitto comes with a 
default configuration, but it would only rotate after 100k file size. This was too many logs put into my daily email so I updated
the configuration to rotate every single day regardless of file size.

```
$ cat /etc/logrotate.d/mosquitto
/var/log/mosquitto/mosquitto.log {
	rotate 3
	daily
	delaycompress
	notifempty
	create 640 mosquitto mosquitto
	missingok
	postrotate
		if invoke-rc.d mosquitto status > /dev/null 2>&1; then \
			invoke-rc.d mosquitto reload > /dev/null 2>&1; \
		fi;
	endscript
}
```

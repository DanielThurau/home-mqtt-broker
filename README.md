# home-mqtt-broker
Github repo with instructions on how I set up the mqtt broker

I followed the instructions [here](https://medium.com/gravio-edge-iot-platform/how-to-set-up-a-mosquitto-mqtt-broker-securely-using-client-certificates-82b2aaaef9c8)

Use `./apt-install.sh` to install dependencies for the [mosquitto open-source mqtt broker](https://mosquitto.org/).


Add the following values to `/etc/mosquitto/conf.d/mosquitto.conf`

```
listener 1883
allow_anonymous false
password_file /etc/mosquitto/conf.d/tasmota_passwd
```

Make sure to edit the `/etc/mosquitto/conf.d/mosquitto.conf` file for user defined configuration, not `/etc/mosquitto/mosquitto.conf`

And to start and enable services on startup in the future, I used systemctl to start the service:

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

I had my firewall already running on my hardened machine, so I opened port 1883 to accept local network connections.

```
$ sudo ufw allow 1883 
```

and used the following `lsof` command to check that moquitto was listening on the port AFTER I got mosquitto running:

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

Great, so the broker is working, now I just have to handle configuring my first real topic on  my home network, my tasmota flashed sonoff plug.

I have a tasmota plug that publishes to a mqtt topic named `tele/tasmota_switch/SENSOR`, and can be configured to talk with a mqtt broker pretty easily. I configure the tasmota plug to talk to my hardened ubuntu machine running mosquitto. The published message looks like this:

```
{"Time":"2024-04-21T22:45:10","ENERGY":{"TotalStartTime":"2024-04-21T22:32:49","Total":0.002,"Yesterday":0.000,"Today":0.002,"Period":0,"Power":11,"ApparentPower":22,"ReactivePower":19,"Factor":0.49,"Voltage":122,"Current":0.181}}
```

which is some very nice json to process. The tasmota plug configures how often to send this telemetry, and I currently have it publish every 30 seconds.

`subscriber.py` is a short python script that will subscribe to the topic, on a message it will process the json and convert it to row data, and print to stdout. In the next iteration I'll probably dump this into a sqlite db for use later.


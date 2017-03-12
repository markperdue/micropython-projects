espbootstrap
============

A small drop-in framework that abstracts away dealing with wifi and mqtt for an esp8266


Getting Started
---------------

1. In your main.py file import and then instantiate an ESPBootstrap object
```
from time import sleep
from espbootstrap import ESPBootstrap


# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "wifi": {
        "ssid": "ssid_here",
        "password": "password_here",
        "check_interval": 30
    },
    "mqtt": {
        "broker": "192.168.1.10",
        "user": "mqtt_user",
        "password": "mqtt_password",
        "topic": "mqtt_topic",
        "client_id": "mqtt_cid",
        "action": "all",
        "interval": 30,
        "deep_sleep": True
    }
}


def pub_callback():
    data = '{"message":"hello"}'

    return data


def sub_callback(topic, msg):
    print("Received callback message '%s' at topic '%s'" % (str(topic), str(msg)))


def main():
    ebs = ESPBootstrap(config=CONFIG)
    ebs.set_mqtt_pub_callback(pub_callback)
    ebs.set_mqtt_sub_callback(sub_callback)
    ebs.start()

    while True:
        ebs.run()
        sleep(1)


if __name__ == '__main__':
    main()

```


Resources
---------

For help copying files to an ESP8266 check out the [ampy](https://github.com/adafruit/ampy) project
import machine
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
        "action": "subscribe",
        "interval": 30
    }
}

light = machine.Pin(14, machine.Pin.OUT)
button = machine.Pin(12, machine.Pin.IN)


def toggle_light():
    print('Toggling light')
    global light
    light.value(not light.value())


def sub_callback(topic, msg):
    print("Received callback message '%s' at topic '%s'" % (str(topic), str(msg)))
    if msg == b'POWER':
        toggle_light()


def main():
    ebs = ESPBootstrap(CONFIG)
    ebs.set_mqtt_sub_callback(sub_callback)
    ebs.start()

    prev_input = 1  # Set start to 1 for ESP8266

    while True:
        current_value = button.value()
        if (not prev_input) and current_value:
            toggle_light()

        prev_input = current_value

        ebs.run()
        sleep(0.25)


if __name__ == '__main__':
    main()

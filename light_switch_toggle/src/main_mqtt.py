import machine
from time import sleep
import ubinascii
from espbootstrap import ESPBootstrap

# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "ssid": "ssid_here",
    "password": "password_here",
    "wlan_check_interval": 30,
    "mqtt": {
        "broker": "broker_here",
        "user": "user_here",
        "password": "password_here",
        "topic": "topic_here",
        "client_id": b"esp8266_" + ubinascii.hexlify(machine.unique_id())
    }
}

light = machine.Pin(14, machine.Pin.OUT)
button = machine.Pin(12, machine.Pin.IN)

def toggle_light():
    print('Toggling light')
    global light
    light.value(not light.value())

def mqtt_callback(topic, msg):
    print((topic, msg))
    if msg == b'POWER':
        toggle_light()

def main():
    ebs = ESPBootstrap(CONFIG)
    ebs.mqtt_client.set_callback(mqtt_callback)
    ebs.start()

    prev_input = 1  # Set start to 1 for ESP8266

    while True:
        current_value = button.value()
        if ((not prev_input) and current_value):
            toggle_light()

        prev_input = current_value

        ebs.run()

        sleep(0.25)


if __name__ == '__main__':
    main()

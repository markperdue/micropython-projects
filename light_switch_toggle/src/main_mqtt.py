import machine
import network
import time
import ubinascii
from simple import MQTTClient

# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "ssid": "ssid_here",
    "password": "password_here",
    "broker": "broker_here",
    "broker_username": "broker_username_here",
    "broker_password": "broker_password_here",
    "topic": b"topic_here",
    "client_id": b"esp8266_" + ubinascii.hexlify(machine.unique_id())
}

led = machine.Pin(14, machine.Pin.OUT)
button = machine.Pin(12, machine.Pin.IN)
wlan = network.WLAN(network.STA_IF)
client = None

def mqtt_callback(topic, msg):
    print((topic, msg))
    if msg == b'POWER':
        global led
        led.value(not led.value())

def do_connect():
    do_connect_wifi()
    do_connect_mqtt()

def do_connect_wifi():
    global wlan

    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to wifi network %s...' % (CONFIG['ssid']))
        wlan.connect(CONFIG['ssid'], CONFIG['password'])
        while not wlan.isconnected():
            pass

    print('WiFi connected with IP address %s' % (wlan.ifconfig()[0]))

def do_connect_mqtt():
    global client

    client = MQTTClient(CONFIG['client_id'], CONFIG['broker'], user=CONFIG['broker_username'], password=CONFIG['broker_password'])
    client.set_callback(mqtt_callback)
    print("Connecting to MQTT broker %s..." % (CONFIG['broker']))

    client.connect()
    print('Connected to MQTT broker %s' % (CONFIG['broker']))

    client.subscribe(CONFIG['topic'])
    print('Subscribed to MQTT topic %s' % (CONFIG['topic']))

def load_config():
    import ujson as json
    try:
        with open("/config.json") as f:
            config = json.loads(f.read())
    except (OSError, ValueError):
        print("Couldn't load /config.json")
        save_config()
    else:
        CONFIG.update(config)
        print("Loaded config from /config.json")

def save_config():
    import ujson as json
    try:
        with open("/config.json", "w") as f:
            f.write(json.dumps(CONFIG))
    except OSError:
        print("Couldn't save /config.json")

def keep_connected():
    if not wlan.isconnected():
        do_connect()

def main():
    load_config()
    do_connect()

    prev_input = 0

    while True:
        current_value = button.value()
        if ((not prev_input) and current_value):
            global led
            led.value(not led.value())

        prev_input = current_value

        global client
        client.check_msg()
        time.sleep(0.25)


if __name__ == '__main__':
    main()

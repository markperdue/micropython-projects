import machine
import network
from time import sleep, time
import ubinascii
import usocket as socket
from simple import MQTTClient

# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "ssid": "ssid_here",
    "password": "password_here",
    "broker": "broker_here",
    "broker_username": "broker_username_here",
    "broker_password": "broker_password_here",
    "topic": b"topic_here",
    "client_id": b"esp8266_" + ubinascii.hexlify(machine.unique_id()),
    "wlan_check_interval": 30
}

led = machine.Pin(14, machine.Pin.OUT)
button = machine.Pin(12, machine.Pin.IN)
wlan = network.WLAN(network.STA_IF)
wlan_last_checked = None
client = None
client_connected = False

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

    global client_connected

    try:
        client.connect()
        client_connected = True
    except OSError:
        client_connected = False
    else:
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
    print('Verifying connections are still active...')

    global wlan_last_checked
    wlan_last_checked = time()

    global wlan
    global client_connected
    if not wlan.isconnected() or not client_connected:
        do_connect()

def main():
    load_config()
    keep_connected()

    prev_input = 1  # Set start to 1 for ESP8266

    while True:
        current_value = button.value()
        if ((not prev_input) and current_value):
            global led
            led.value(not led.value())

        prev_input = current_value

        global wlan_last_checked
        if (time() - wlan_last_checked) > CONFIG['wlan_check_interval']:
            keep_connected()

        global client
        if client is not None:
            try:
                client.check_msg()
            except OSError:
                global client_connected
                client_connected = False

        sleep(0.25)


if __name__ == '__main__':
    main()

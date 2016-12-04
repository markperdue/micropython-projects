import machine
import network
from time import sleep, time
import ubinascii
from umqtt.simple import MQTTClient

# These defaults are overwritten with the contents of /config.json by load_config()
CONFIG = {
    "ssid": "ssid_here",
    "password": "password_here",
    "broker": "192.168.1.10",
    "sensor_pin": 0,
    "client_id": b"esp8266_" + ubinascii.hexlify(machine.unique_id()),
    "topic": b"home",
    "publish_interval": 10,
    "led_pin": 14,
}

led_pin = None
sensor_pin = None
wlan = network.WLAN(network.STA_IF)
client = None

def flash_led(seconds):
    led_pin.high()
    sleep(seconds)
    led_pin.low()
    sleep(seconds)

def setup_pins():
    global sensor_pin
    sensor_pin = machine.ADC(CONFIG['sensor_pin'])

    global led_pin
    led_pin = machine.Pin(CONFIG['led_pin'], machine.Pin.OUT)

def do_connect():
    do_connect_wifi()
    do_connect_mqtt()

def do_connect_wifi():
    import network
    global wlan
    # wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(CONFIG['ssid'], CONFIG['password'])
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

def do_connect_mqtt():
    global client
    client = MQTTClient(CONFIG['client_id'], CONFIG['broker'])
    client.connect()
    print("Connected to {}".format(CONFIG['broker']))

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
    last_sent = time()

    while True:
        data = sensor_pin.read()
        if data is not None:
            if data < 150:
                flash_led(0.125)
                flash_led(0.125)
                flash_led(0.125)
            elif data < 200:
                flash_led(0.25)
                flash_led(0.25)
            elif data < 300:
                flash_led(0.5)
            elif data < 350:
                led_pin.high()
            else:
                led_pin.low()

            if (time() - last_sent) > CONFIG['publish_interval']:
                keep_connected()

                client.publish(CONFIG['topic'], bytes(str(data), 'utf-8'))
                print('Sensor state: {}'.format(data))
                last_sent = time()
        else:
            flash_led(1)

        sleep(1)

if __name__ == '__main__':
    load_config()
    setup_pins()
    do_connect()
    main()

import network
from time import time
from simple import MQTTClient

class ESPBootstrap(object):
    def __init__(self, config):
        self.config = config
        self.wlan = None
        self.wlan_check_interval = None
        self.wlan_last_checked = 0
        self.is_configured = False
        self.mqtt_client = None
        self.mqtt_client_connected = False
        self.cb = None
        self.cid = None

        self.load_config()
        self.configure()

    def configure(self):
        if self.config is not None:
            if 'ssid' in self.config:
                self.wlan = network.WLAN(network.STA_IF)
                self.wlan.active(True)

                if 'wlan_check_interval' in self.config and self.config['wlan_check_interval']:
                    self.wlan_check_interval = self.config['wlan_check_interval']
                else:
                    self.wlan_check_interval = 30  # Default

            if 'mqtt' in self.config:
                if 'client_id' in self.config['mqtt'] and 'broker' in self.config['mqtt']:
                    self.cid = self.config['mqtt']['client_id']
                    self.mqtt_client = MQTTClient(self.cid, self.config['mqtt']['broker'])

                    if 'user' in self.config['mqtt']:
                        self.mqtt_client.user = self.config['mqtt']['user']

                    if 'password' in self.config['mqtt']:
                        self.mqtt_client.pswd = self.config['mqtt']['password']


    def do_connect(self):
        self.do_connect_wifi()
        self.do_connect_mqtt()

    def do_connect_wifi(self):
        if self.wlan is not None:
            if not self.wlan.isconnected():
                print('Connecting to WiFi network %s...' % (self.config['ssid']))
                self.wlan.connect(self.config['ssid'], self.config['password'])
                while not self.wlan.isconnected():
                    pass

            print('WiFi connected with IP address %s' % (self.wlan.ifconfig()[0]))

    def do_connect_mqtt(self):
        if self.mqtt_client is not None:
            if not self.mqtt_client_connected:
                print("Connecting to MQTT broker %s..." % (self.config['mqtt']['broker']))

                try:
                    self.mqtt_client.connect()
                    self.mqtt_client_connected = True
                except OSError:
                    self.mqtt_client_connected = False
                    print('Unable to connect to MQTT broker')
                else:
                    print('Connected to MQTT broker')

                    if self.config is not None and 'mqtt' in self.config and 'topic' in self.config['mqtt']:
                        try:
                            self.mqtt_client.subscribe(self.config['mqtt']['topic'].encode('utf-8'))
                        except OSError:
                            print('Unable to subscribe to topic')
                        else:
                            print('Subscribed to MQTT topic %s' % (self.config['mqtt']['topic']))

    def load_config(self):
        import ujson as json
        try:
            with open("/config.json") as f:
                new_config = json.loads(f.read())
        except (OSError, ValueError):
            print("Couldn't load /config.json")
            self.save_config()
        else:
            self.config.update(new_config)
            print("Loaded config from /config.json")

    def save_config(self):
        import ujson as json
        try:
            with open("/config.json", "w") as f:
                f.write(json.dumps(self.config))
        except OSError:
            print("Couldn't save /config.json")

    def keep_connected(self):
        print('Verifying connections are still active...')

        self.wlan_last_checked = time()
        if not self.wlan.isconnected() or not self.mqtt_client_connected:
            self.do_connect()

    def run(self):
        if self.wlan_last_checked is not None and (time() - self.wlan_last_checked > self.wlan_check_interval):
            self.keep_connected()

        if self.mqtt_client is not None:
            try:
                self.mqtt_client.check_msg()
            except OSError:
                self.mqtt_client_connected = False

    def start(self):
        self.do_connect()

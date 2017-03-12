import network
from time import time


class ESPBootstrap(object):
    def __init__(self, config=None):
        self.config = config
        self.wlan = None
        self.wlan_check_interval = None
        self.wlan_last_checked = 0
        self.ap = None
        self.mqtt_client = None
        self.mqtt_client_connected = False
        self.mqtt_action = None
        self.mqtt_interval = None
        self.mqtt_last_sent_ts = None
        self.mqtt_scb = None
        self.mqtt_pcb = None

        self.load_config()

        try:
            self.configure()
        except ValueError:
            print('Error: Problem configuring bootstrapper')
            raise SystemExit

    def set_mqtt_sub_callback(self, f):
        self.mqtt_scb = f

    def set_mqtt_pub_callback(self, f):
        self.mqtt_pcb = f

    def configure(self):
        try:
            self.conf_wifi(self.config['wifi'])
        except KeyError:
            pass

        try:
            self.conf_ap(self.config['access_point'])
        except KeyError:
            self.ap = network.WLAN(network.AP_IF)
            self.ap.active(False)
            pass
        except Exception:
            print('There was an issue configuring the access point')

        try:
            self.conf_mqtt(self.config['mqtt'])
        except KeyError:
            pass

    def conf_wifi(self, s):
        if s is not None and 'ssid' in s:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)

            try:
                self.wlan_check_interval = int(s['check_interval'])
            except (KeyError, ValueError):
                print('Error: Invalid check_interval value. Using default value')
                self.wlan_check_interval = 30
        else:
            print('WiFi disabled')

    def conf_ap(self, s):
        self.ap = network.WLAN(network.AP_IF)

        if s is not None and 'ssid' in s:
            print('Configuring access point...')

            try:
                self.ap.config(essid=s['ssid'])
            except (KeyError, ValueError):
                print('Error: Invalid ssid value')

            try:
                self.ap.config(channel=s['channel'])
            except (KeyError, ValueError):
                print('Error: Invalid channel value')

            try:
                self.ap.config(hidden=bool(s['hidden']))
            except (KeyError, ValueError):
                print('Error: Invalid hidden value')

            try:
                self.ap.config(authmode=int(s['authmode']))
            except (KeyError, ValueError):
                print('Error: Invalid authmode value')

            try:
                self.ap.config(password=s['password'])
            except (KeyError, ValueError):
                print('Error: Invalid password value')
        else:
            self.ap.active(False)
            return

    def conf_mqtt(self, s):
        if s is not None:
            from simple import MQTTClient
        else:
            return

        try:
            self.mqtt_client = MQTTClient(s['client_id'], s['broker'])
        except (KeyError, ValueError):
            print('Error: Invalid client_id or broker value')

        try:
            self.mqtt_client.user = s['user']
        except (KeyError, ValueError):
            print('Error: Invalid user value')

        try:
            self.mqtt_client.pswd = s['password']
        except (KeyError, ValueError):
            print('Error: Invalid password value')

        try:
            if s['action'] in ['all', 'publish', 'subscribe']:
                self.mqtt_action = s['action']
        except (KeyError, ValueError):
            print('Error: Invalid action value')

        try:
            self.mqtt_interval = int(s['interval'])
        except (KeyError, ValueError):
            print('Error: Invalid interval value')

    def conn(self):
        self.conn_wifi(ssid=self.config['wifi']['ssid'], password=self.config['wifi']['password'])
        self.conn_mqtt()

    def conn_wifi(self, ssid=None, password=None):
        if self.wlan is not None:
            if not self.wlan.isconnected():
                print('Connecting to WiFi network %s...' % ssid)
                self.wlan.connect(ssid, password)

                while not self.wlan.isconnected():
                    pass

            print('WiFi connected with IP address %s' % (self.wlan.ifconfig()[0]))

    def conn_mqtt(self):
        if self.mqtt_client is not None:
            if not self.mqtt_client_connected:
                print("Connecting to MQTT broker %s..." % (self.mqtt_client.addr[0]))

                try:
                    self.mqtt_client.connect()
                except OSError:
                    self.mqtt_client_connected = False
                    print('Unable to connect to MQTT broker')
                except IndexError:
                    self.mqtt_client_connected = False
                    print('Unable to connect to MQTT broker')
                else:
                    self.mqtt_client_connected = True
                    print('Connected to MQTT broker')

                    if self.config is not None and 'mqtt' in self.config and 'topic' in self.config['mqtt']:
                        if self.mqtt_action is not None and self.mqtt_action in ['all', 'subscribe']:
                            if self.mqtt_scb is not None:
                                self.mqtt_client.set_callback(self.mqtt_scb)

                                try:
                                    self.mqtt_client.subscribe(self.config['mqtt']['topic'].encode('utf-8'))
                                except OSError:
                                    print('Unable to subscribe to topic')
                                except AssertionError:
                                    print('AssertionError: Subscribe callback is not set')
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
            self.conn()

    def mqtt_pub(self):
        if self.mqtt_pcb is not None:
            data = self.mqtt_pcb()

            if data is not None:
                try:
                    topic = self.config['mqtt']['topic']
                except KeyError:
                    pass
                else:
                    print("Publishing message '%s' to topic '%s'" % (str(data), str(topic)))
                    self.mqtt_client.publish(topic, bytes(str(data), 'utf-8'))
                    self.mqtt_last_sent_ts = time()
            else:
                raise ValueError
        else:
            raise NotImplementedError

    def check_mqtt(self, rt):
        if self.mqtt_client is not None:
            try:
                self.mqtt_client.check_msg()
            except OSError:
                self.mqtt_client_connected = False

            if self.mqtt_last_sent_ts is None or (rt - self.mqtt_last_sent_ts > self.mqtt_interval):
                try:
                    self.mqtt_pub()
                except NotImplementedError:
                    print('Error: No MQTT data callback is implemented')
                except ValueError:
                    print('Error: MQTT data callback returned no data to publish')

    def check_wifi(self, rt):
        if self.wlan is not None:
            if self.wlan_last_checked is not None and (rt - self.wlan_last_checked > self.wlan_check_interval):
                self.keep_connected()

    def run(self):
        rt = time()

        self.check_wifi(rt)
        self.check_mqtt(rt)

    def start(self):
        self.conn()

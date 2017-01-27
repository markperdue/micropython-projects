light_switch_toggle
===================

Toggles a power outlet that is provided by a DLI IoT Relay. An ESP8266 is connected to a push button switch which has leads going to the DLI IoT Relay

There are 2 versions of this project:
- main.py acts as a simple toggle switch using a hardware button
- main_mqtt.py acts the same as main.py but also connects to a definable MQTT server and subscribes to a definable topic. If a 'POWER' message is received for the topic the script will toggle the light switch


Parts List
----------

- ESP8266 (NodeMCUv2)
- DLI IoT Relay (<https://www.amazon.com/Iot-Relay-Enclosed-High-power-Raspberry/dp/B00WV7GMA2>)
- Breadboard
- Wire leads


Installation - Simple version
-----------------------------

1. Flash micropython firmware on to the ESP8266
4. Copy main.py to the root directory of the micropython firmware running on the ESP8266


Installation - MQTT version
---------------------------

1. Flash micropython firmware on to the ESP8266
2. Rename config.json.example to config.json
3. Edit config.json with your WiFi and MQTT settings
4. Copy and rename main_mqtt.py to main.py to the root directory of the micropython firmware running on the ESP8266
5. Copy simple.py and config.json to the root directory of the micropython firmware running on the ESP8266


Resources
---------

For help copying files to an ESP8266 check out the [ampy](https://github.com/adafruit/ampy) project